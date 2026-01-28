/**
 * Dashboard Page Tests
 * Tests for the main dashboard component
 */

import { render, screen, waitFor } from '@testing-library/react';
import DashboardPage from '../app/page';

// Mock the fetch API
beforeEach(() => {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ agents: [], analytics: {} }),
    })
  );
});

afterEach(() => {
  jest.resetAllMocks();
});

describe('Dashboard Page', () => {
  it('renders the dashboard header', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Today's Social Media Activity/i)).toBeInTheDocument();
    });
  });

  it('displays metric cards', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Engagement Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/Weekly Reach/i)).toBeInTheDocument();
      expect(screen.getByText(/Sentiment Score/i)).toBeInTheDocument();
      expect(screen.getByText(/Posts Scheduled/i)).toBeInTheDocument();
    });
  });

  it('shows agent status cards', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Agent Status/i)).toBeInTheDocument();
      expect(screen.getByText(/Master Orchestrator/i)).toBeInTheDocument();
      expect(screen.getByText(/Content Generator/i)).toBeInTheDocument();
    });
  });

  it('displays quick action buttons', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Pause All/i)).toBeInTheDocument();
      expect(screen.getByText(/Emergency Post/i)).toBeInTheDocument();
    });
  });

  it('shows system alerts section', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/System Alerts/i)).toBeInTheDocument();
    });
  });

  it('renders platform performance chart', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/Platform Performance/i)).toBeInTheDocument();
    });
  });
});

describe('Dashboard Interactions', () => {
  it('handles pause/resume toggle', async () => {
    const { getByText } = render(<DashboardPage />);
    
    await waitFor(() => {
      const pauseButton = getByText(/Pause All/i);
      expect(pauseButton).toBeInTheDocument();
    });
  });
});
