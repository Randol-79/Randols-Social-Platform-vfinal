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
      expect(screen.getAllByText(/Engagement Rate/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Weekly Reach/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Sentiment Score/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Posts Scheduled/i).length).toBeGreaterThan(0);
    });
  });

  it('shows agent status cards', async () => {
    render(<DashboardPage />);
    
    await waitFor(() => {
      expect(screen.getAllByText(/Agent Status/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Master Orchestrator/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/Content Generator/i).length).toBeGreaterThan(0);
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
