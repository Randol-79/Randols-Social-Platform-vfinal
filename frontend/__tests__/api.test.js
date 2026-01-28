/**
 * API Hooks Tests
 * Tests for the API client and React hooks
 */

import { renderHook, waitFor } from '@testing-library/react';
import { api, useFetch, useLocalStorage, useDebounce } from '../lib/api';

// Mock fetch globally
beforeEach(() => {
  global.fetch = jest.fn();
});

afterEach(() => {
  jest.resetAllMocks();
});

describe('API Client', () => {
  it('makes GET requests correctly', async () => {
    const mockData = { success: true, data: 'test' };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await api.get('/api/v1/test');
    
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/test'),
      expect.objectContaining({ method: 'GET' })
    );
    expect(result).toEqual(mockData);
  });

  it('makes POST requests with body', async () => {
    const mockData = { id: 1, created: true };
    const postBody = { content: 'test content' };
    
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await api.post('/api/v1/content', postBody);
    
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/content'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify(postBody),
      })
    );
    expect(result).toEqual(mockData);
  });

  it('handles errors correctly', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({ message: 'Server error' }),
    });

    await expect(api.get('/api/v1/error')).rejects.toThrow();
  });

  it('makes PUT requests', async () => {
    const mockData = { updated: true };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const result = await api.put('/api/v1/content/1', { text: 'updated' });
    
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/content/1'),
      expect.objectContaining({ method: 'PUT' })
    );
  });

  it('makes DELETE requests', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ deleted: true }),
    });

    await api.delete('/api/v1/content/1');
    
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/content/1'),
      expect.objectContaining({ method: 'DELETE' })
    );
  });
});

describe('useFetch Hook', () => {
  it('fetches data on mount', async () => {
    const mockData = { items: [1, 2, 3] };
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockData),
    });

    const { result } = renderHook(() => useFetch('/api/v1/items'));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toEqual(mockData);
      expect(result.current.error).toBeNull();
    });
  });

  it('handles fetch errors', async () => {
    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useFetch('/api/v1/items'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe('Network error');
    });
  });
});

describe('useLocalStorage Hook', () => {
  beforeEach(() => {
    localStorage.clear();
    localStorage.getItem.mockReturnValue(null);
  });

  it('returns initial value when storage is empty', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));
    
    expect(result.current[0]).toBe('initial');
  });

  it('returns stored value when present', () => {
    localStorage.getItem.mockReturnValue(JSON.stringify('stored-value'));
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'));
    
    expect(result.current[0]).toBe('stored-value');
  });
});

describe('useDebounce Hook', () => {
  jest.useFakeTimers();

  it('debounces value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'updated', delay: 500 });
    expect(result.current).toBe('initial');

    jest.advanceTimersByTime(500);
    expect(result.current).toBe('updated');
  });

  afterEach(() => {
    jest.useRealTimers();
  });
});
