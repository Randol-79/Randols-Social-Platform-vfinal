"""
LLM Client with Token Tracking, Cost Estimation, and Retry Logic
Provides a unified interface for OpenAI calls with observability
"""

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from utils.config import Config
from utils.logger import setup_logger

# Try to import dependencies
try:
    import openai
    from openai import AsyncOpenAI, OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from tenacity import (
        RetryError,
        before_sleep_log,
        retry,
        retry_if_exception_type,
        stop_after_attempt,
        wait_exponential,
    )

    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False


# Pricing per 1K tokens (as of 2024)
MODEL_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
}


@dataclass
class LLMUsageStats:
    """Track LLM usage statistics"""

    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost_usd: float = 0.0
    requests_by_model: Dict[str, int] = field(default_factory=dict)
    errors: int = 0
    retries: int = 0
    avg_latency_ms: float = 0.0
    _latencies: List[float] = field(default_factory=list)

    def record_request(
        self, model: str, prompt_tokens: int, completion_tokens: int, cost: float, latency_ms: float
    ):
        """Record a successful request"""
        self.total_requests += 1
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.total_cost_usd += cost
        self.requests_by_model[model] = self.requests_by_model.get(model, 0) + 1
        self._latencies.append(latency_ms)
        self.avg_latency_ms = sum(self._latencies) / len(self._latencies)

    def record_error(self):
        """Record a failed request"""
        self.errors += 1

    def record_retry(self):
        """Record a retry attempt"""
        self.retries += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/reporting"""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_cost_usd": round(self.total_cost_usd, 4),
            "requests_by_model": self.requests_by_model,
            "errors": self.errors,
            "retries": self.retries,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "error_rate": round(self.errors / max(self.total_requests, 1) * 100, 2),
        }


@dataclass
class LLMResponse:
    """Structured LLM response with metadata"""

    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
    finish_reason: str
    raw_response: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "tokens": {
                "prompt": self.prompt_tokens,
                "completion": self.completion_tokens,
                "total": self.total_tokens,
            },
            "cost_usd": round(self.cost_usd, 6),
            "latency_ms": round(self.latency_ms, 2),
            "finish_reason": self.finish_reason,
        }


class LLMClient:
    """
    Unified LLM client with:
    - Token counting and cost tracking
    - Automatic retries with exponential backoff
    - Request/response logging
    - Usage statistics
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        """Singleton pattern for consistent usage tracking"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = setup_logger("llm_client")
        self.stats = LLMUsageStats()
        self._client: Optional[OpenAI] = None
        self._async_client: Optional[AsyncOpenAI] = None
        self._encoder = None
        self._model = Config.OPENAI_MODEL or "gpt-4"
        self._max_tokens = Config.OPENAI_MAX_TOKENS or 500
        self._temperature = Config.OPENAI_TEMPERATURE or 0.7

        self._init_clients()
        self._init_tokenizer()
        self._initialized = True

    def _init_clients(self):
        """Initialize OpenAI clients"""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI package not installed")
            return

        api_key = Config.OPENAI_API_KEY
        if not api_key or api_key.startswith("sk-your"):
            self.logger.warning("OpenAI API key not configured")
            return

        try:
            self._client = OpenAI(api_key=api_key)
            self._async_client = AsyncOpenAI(api_key=api_key)
            self.logger.info(f"OpenAI clients initialized with model: {self._model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI clients: {e}")

    def _init_tokenizer(self):
        """Initialize tiktoken encoder"""
        if not TIKTOKEN_AVAILABLE:
            self.logger.warning("tiktoken not installed, token counting disabled")
            return

        try:
            self._encoder = tiktoken.encoding_for_model(self._model)
        except KeyError:
            # Fallback for unknown models
            self._encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if not self._encoder:
            # Rough estimate: ~4 chars per token
            return len(text) // 4
        return len(self._encoder.encode(text))

    def estimate_cost(
        self, prompt_tokens: int, completion_tokens: int, model: Optional[str] = None
    ) -> float:
        """Estimate cost in USD"""
        model = model or self._model
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["gpt-4"])
        return (prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]) / 1000

    @property
    def is_available(self) -> bool:
        """Check if LLM client is available"""
        return self._client is not None

    def _create_retry_decorator(self):
        """Create retry decorator with exponential backoff"""
        if not TENACITY_AVAILABLE:
            # Return no-op decorator if tenacity not available
            def no_retry(func):
                return func

            return no_retry

        return retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=4, max=60),
            retry=retry_if_exception_type(
                (
                    openai.RateLimitError if OPENAI_AVAILABLE else Exception,
                    openai.APIConnectionError if OPENAI_AVAILABLE else Exception,
                    openai.APITimeoutError if OPENAI_AVAILABLE else Exception,
                )
            ),
            before_sleep=lambda retry_state: self.stats.record_retry(),
        )

    def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None,
    ) -> LLMResponse:
        """
        Synchronous completion with full tracking.

        Args:
            prompt: User prompt text
            system_prompt: Optional system prompt
            model: Model override
            max_tokens: Max tokens override
            temperature: Temperature override
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            LLMResponse with content and metadata
        """
        if not self._client:
            raise RuntimeError("OpenAI client not available")

        model = model or self._model
        max_tokens = max_tokens or self._max_tokens
        temperature = temperature or self._temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Count input tokens
        prompt_tokens = sum(self.count_tokens(m["content"]) for m in messages)

        start_time = time.time()

        try:
            # Apply retry decorator
            @self._create_retry_decorator()
            def _call():
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                return self._client.chat.completions.create(**kwargs)

            response = _call()

            latency_ms = (time.time() - start_time) * 1000

            # Extract response data
            content = response.choices[0].message.content
            completion_tokens = (
                response.usage.completion_tokens if response.usage else self.count_tokens(content)
            )
            actual_prompt_tokens = response.usage.prompt_tokens if response.usage else prompt_tokens
            total_tokens = actual_prompt_tokens + completion_tokens
            cost = self.estimate_cost(actual_prompt_tokens, completion_tokens, model)

            # Record stats
            self.stats.record_request(
                model, actual_prompt_tokens, completion_tokens, cost, latency_ms
            )

            # Log usage
            self.logger.info(
                "LLM request completed",
                extra={
                    "model": model,
                    "prompt_tokens": actual_prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "cost_usd": round(cost, 6),
                    "latency_ms": round(latency_ms, 2),
                },
            )

            return LLMResponse(
                content=content,
                model=model,
                prompt_tokens=actual_prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response,
            )

        except Exception as e:
            self.stats.record_error()
            self.logger.error(f"LLM request failed: {e}")
            raise

    async def complete_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        response_format: Optional[Dict] = None,
    ) -> LLMResponse:
        """
        Asynchronous completion with full tracking.
        Same interface as complete() but async.
        """
        if not self._async_client:
            raise RuntimeError("OpenAI async client not available")

        model = model or self._model
        max_tokens = max_tokens or self._max_tokens
        temperature = temperature or self._temperature

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        prompt_tokens = sum(self.count_tokens(m["content"]) for m in messages)
        start_time = time.time()

        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
            if response_format:
                kwargs["response_format"] = response_format

            # Retry logic for async
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await self._async_client.chat.completions.create(**kwargs)
                    break
                except (
                    openai.RateLimitError,
                    openai.APIConnectionError,
                    openai.APITimeoutError,
                ) as e:
                    self.stats.record_retry()
                    if attempt == max_retries - 1:
                        raise
                    wait_time = min(4 * (2**attempt), 60)
                    self.logger.warning(
                        f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)

            latency_ms = (time.time() - start_time) * 1000

            content = response.choices[0].message.content
            completion_tokens = (
                response.usage.completion_tokens if response.usage else self.count_tokens(content)
            )
            actual_prompt_tokens = response.usage.prompt_tokens if response.usage else prompt_tokens
            total_tokens = actual_prompt_tokens + completion_tokens
            cost = self.estimate_cost(actual_prompt_tokens, completion_tokens, model)

            self.stats.record_request(
                model, actual_prompt_tokens, completion_tokens, cost, latency_ms
            )

            self.logger.info(
                "Async LLM request completed",
                extra={
                    "model": model,
                    "prompt_tokens": actual_prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "cost_usd": round(cost, 6),
                    "latency_ms": round(latency_ms, 2),
                },
            )

            return LLMResponse(
                content=content,
                model=model,
                prompt_tokens=actual_prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                latency_ms=latency_ms,
                finish_reason=response.choices[0].finish_reason,
                raw_response=response,
            )

        except Exception as e:
            self.stats.record_error()
            self.logger.error(f"Async LLM request failed: {e}")
            raise

    def complete_json(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """
        Completion that returns parsed JSON.
        Uses JSON mode if available.
        """
        response = self.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"},
            **kwargs,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            # Try to extract JSON from response
            content = response.content
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            raise

    async def complete_json_async(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Async version of complete_json"""
        response = await self.complete_async(
            prompt=prompt,
            system_prompt=system_prompt,
            response_format={"type": "json_object"},
            **kwargs,
        )

        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {e}")
            content = response.content
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.stats.to_dict()

    def reset_stats(self):
        """Reset usage statistics"""
        self.stats = LLMUsageStats()


# Singleton instance
def get_llm_client() -> LLMClient:
    """Get the singleton LLM client instance"""
    return LLMClient()
