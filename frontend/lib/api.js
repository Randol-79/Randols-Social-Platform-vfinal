'use client';

import { useState, useEffect, useCallback } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// ============================================
// Generic Fetch Hook
// ============================================

export function useFetch(endpoint, options = {}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [endpoint]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, error, loading, refetch: fetchData };
}

// ============================================
// API Client
// ============================================

class ApiClient {
  constructor(baseUrl = API_BASE) {
    this.baseUrl = baseUrl;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data)
    });
  }

  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data)
    });
  }

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }
}

export const api = new ApiClient();

// ============================================
// System Hooks
// ============================================

export function useSystemStatus() {
  return useFetch('/api/v1/status');
}

export function useHealth() {
  return useFetch('/api/v1/health');
}

// ============================================
// Content Hooks
// ============================================

export function useContent(filters = {}) {
  const params = new URLSearchParams();
  if (filters.status) params.append('status', filters.status);
  if (filters.type) params.append('type', filters.type);
  if (filters.platform) params.append('platform', filters.platform);
  if (filters.limit) params.append('limit', filters.limit);

  const queryString = params.toString();
  const endpoint = `/api/v1/content${queryString ? `?${queryString}` : ''}`;

  return useFetch(endpoint);
}

export function useContentById(id) {
  return useFetch(id ? `/api/v1/content/${id}` : null);
}

export async function createContent(content) {
  return api.post('/api/v1/content', content);
}

export async function updateContent(id, updates) {
  return api.put(`/api/v1/content/${id}`, updates);
}

export async function deleteContent(id) {
  return api.delete(`/api/v1/content/${id}`);
}

export async function generateContent(params) {
  return api.post('/api/v1/content/generate', params);
}

export async function validateContent(text) {
  return api.post('/api/v1/content/validate', { text });
}

export async function enhanceContent(text, keywords = []) {
  return api.post('/api/v1/content/enhance', { text, keywords });
}

// ============================================
// Schedule Hooks
// ============================================

export function useSchedule(date) {
  const params = date ? `?date=${date}` : '';
  return useFetch(`/api/v1/schedule${params}`);
}

export function usePendingPosts() {
  return useFetch('/api/v1/schedule/pending');
}

export function useCalendar(startDate, days = 7) {
  const params = new URLSearchParams();
  if (startDate) params.append('start', startDate);
  params.append('days', days.toString());

  return useFetch(`/api/v1/schedule/calendar?${params.toString()}`);
}

export function useOptimalTimes() {
  return useFetch('/api/v1/schedule/optimal-times');
}

export async function schedulePost(contentId, platform, scheduledTime, priority = 'normal') {
  return api.post('/api/v1/schedule', {
    content_id: contentId,
    platform,
    scheduled_time: scheduledTime,
    priority
  });
}

export async function cancelPost(postId) {
  return api.post(`/api/v1/schedule/${postId}/cancel`);
}

// ============================================
// Analytics Hooks
// ============================================

export function useDailyAnalytics(date) {
  const params = date ? `?date=${date}` : '';
  return useFetch(`/api/v1/analytics/daily${params}`);
}

export function useAnalyticsRange(startDate, endDate) {
  const params = new URLSearchParams();
  if (startDate) params.append('start', startDate);
  if (endDate) params.append('end', endDate);

  return useFetch(`/api/v1/analytics/range?${params.toString()}`);
}

export function useWeeklyReports(limit = 12) {
  return useFetch(`/api/v1/analytics/weekly?limit=${limit}`);
}

export function usePlatformAnalytics(platform, days = 30) {
  return useFetch(`/api/v1/analytics/platform/${platform}?days=${days}`);
}

export function usePerformanceAnalysis(period = '7d') {
  return useFetch(`/api/v1/analytics/performance?period=${period}`);
}

export function useRecommendations() {
  return useFetch('/api/v1/analytics/recommendations');
}

// ============================================
// Agent Hooks
// ============================================

export function useAgents() {
  return useFetch('/api/v1/agents');
}

export function useAgentStatus(agentName) {
  return useFetch(agentName ? `/api/v1/agents/${agentName}` : null);
}

export function useAgentLogs(agentName, limit = 100) {
  return useFetch(`/api/v1/agents/${agentName}/logs?limit=${limit}`);
}

export function useErrorLogs(hours = 24) {
  return useFetch(`/api/v1/agents/logs/errors?hours=${hours}`);
}

// ============================================
// Admin Hooks
// ============================================

export async function triggerEmergencyOverride(reason, options = {}) {
  return api.post('/api/v1/admin/emergency-override', {
    reason,
    message: options.message,
    platforms: options.platforms || ['facebook', 'instagram'],
    generate_content: options.generateContent || false
  });
}

export async function pauseSystem() {
  return api.post('/api/v1/admin/pause');
}

export async function resumeSystem() {
  return api.post('/api/v1/admin/resume');
}

export async function runWorkflow() {
  return api.post('/api/v1/admin/run-workflow');
}

export async function startABTest(config) {
  return api.post('/api/v1/admin/ab-test', config);
}

export async function evaluateABTest(testId) {
  return api.post(`/api/v1/admin/ab-test/${testId}/evaluate`);
}

export function useNotifications() {
  return useFetch('/api/v1/admin/notifications');
}

export async function markNotificationRead(notificationId) {
  return api.post(`/api/v1/admin/notifications/${notificationId}/read`);
}

// ============================================
// Brand Hooks
// ============================================

export function useBrandGuidelines() {
  return useFetch('/api/v1/brand/guidelines');
}

export function useCajunPhrases() {
  return useFetch('/api/v1/brand/cajun-phrases');
}

// ============================================
// WebSocket Hook for Real-time Updates
// ============================================

export function useWebSocket(url, options = {}) {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);

  useEffect(() => {
    const wsUrl = url || `${API_BASE.replace('http', 'ws')}/socket.io`;
    
    // For Socket.IO, we'd use the socket.io-client library
    // This is a simplified WebSocket implementation
    try {
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnected(true);
        options.onOpen?.();
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setLastMessage(data);
        options.onMessage?.(data);
      };

      ws.onclose = () => {
        setConnected(false);
        options.onClose?.();
      };

      ws.onerror = (error) => {
        options.onError?.(error);
      };

      setSocket(ws);

      return () => {
        ws.close();
      };
    } catch (error) {
      console.error('WebSocket connection failed:', error);
    }
  }, [url]);

  const sendMessage = useCallback((message) => {
    if (socket && connected) {
      socket.send(JSON.stringify(message));
    }
  }, [socket, connected]);

  return { connected, lastMessage, sendMessage };
}

// ============================================
// Polling Hook for Real-time Data
// ============================================

export function usePolling(fetchFn, interval = 30000, enabled = true) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  const poll = useCallback(async () => {
    try {
      const result = await fetchFn();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [fetchFn]);

  useEffect(() => {
    if (!enabled) return;

    poll();
    const timer = setInterval(poll, interval);

    return () => clearInterval(timer);
  }, [poll, interval, enabled]);

  return { data, error, loading, refetch: poll };
}

// ============================================
// Local Storage Hook
// ============================================

export function useLocalStorage(key, initialValue) {
  const [storedValue, setStoredValue] = useState(() => {
    if (typeof window === 'undefined') return initialValue;
    
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  return [storedValue, setValue];
}

// ============================================
// Debounce Hook
// ============================================

export function useDebounce(value, delay) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
