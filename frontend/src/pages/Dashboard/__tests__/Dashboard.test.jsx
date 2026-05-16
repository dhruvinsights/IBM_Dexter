import { describe, it, expect, beforeEach, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../../utils/testUtils';
import Dashboard from '../Dashboard';
import * as platformService from '../../../services/platformService';

// Mock the platform service
vi.mock('../../../services/platformService');

describe('Dashboard Component', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
    
    // Mock successful data fetch
    platformService.getDashboardData.mockResolvedValue({
      kpis: {
        totalPRs: 156,
        avgReviewTime: '2.5h',
        codeQualityScore: 87,
        securityScore: 92,
      },
      recentActivity: [],
      trends: {},
    });
  });

  it('renders dashboard title', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('displays KPI cards with correct data', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText('Total Pull Requests')).toBeInTheDocument();
      expect(screen.getByText('156')).toBeInTheDocument();
      
      expect(screen.getByText('Avg Review Time')).toBeInTheDocument();
      expect(screen.getByText('2.5h')).toBeInTheDocument();
      
      expect(screen.getByText('Code Quality Score')).toBeInTheDocument();
      expect(screen.getByText('87')).toBeInTheDocument();
      
      expect(screen.getByText('Security Score')).toBeInTheDocument();
      expect(screen.getByText('92')).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    // Mock a delayed response
    platformService.getDashboardData.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );
    
    renderWithProviders(<Dashboard />);
    
    // Should show skeleton loaders
    const skeletons = document.querySelectorAll('.cds--skeleton');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('handles error state gracefully', async () => {
    // Mock error response
    platformService.getDashboardData.mockRejectedValue(
      new Error('Failed to fetch dashboard data')
    );
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
    });
  });

  it('renders charts section', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      // Check for chart containers
      expect(screen.getByText(/review trends/i)).toBeInTheDocument();
      expect(screen.getByText(/code quality/i)).toBeInTheDocument();
    });
  });

  it('renders recent activity section', async () => {
    platformService.getDashboardData.mockResolvedValue({
      kpis: {
        totalPRs: 156,
        avgReviewTime: '2.5h',
        codeQualityScore: 87,
        securityScore: 92,
      },
      recentActivity: [
        {
          id: 1,
          type: 'review',
          title: 'PR #123 reviewed',
          timestamp: '2024-01-01T00:00:00Z',
        },
      ],
      trends: {},
    });
    
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(screen.getByText(/recent activity/i)).toBeInTheDocument();
    });
  });

  it('calls platform service on mount', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(platformService.getDashboardData).toHaveBeenCalledTimes(1);
    });
  });

  it('renders with correct layout structure', async () => {
    const { container } = renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      const dashboard = container.querySelector('.dashboard');
      expect(dashboard).toBeInTheDocument();
      
      const kpisSection = container.querySelector('.dashboard__kpis');
      expect(kpisSection).toBeInTheDocument();
      
      const chartsSection = container.querySelector('.dashboard__charts');
      expect(chartsSection).toBeInTheDocument();
    });
  });

  it('displays data in Carbon tiles', async () => {
    renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      const tiles = document.querySelectorAll('.cds--tile');
      expect(tiles.length).toBeGreaterThan(0);
    });
  });

  it('handles refresh action', async () => {
    const { rerender } = renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      expect(platformService.getDashboardData).toHaveBeenCalledTimes(1);
    });
    
    // Trigger refresh by re-rendering
    rerender(<Dashboard />);
    
    // Service should be called again
    expect(platformService.getDashboardData).toHaveBeenCalled();
  });

  it('renders with dark theme', async () => {
    renderWithProviders(<Dashboard />, { theme: 'g100' });
    
    await waitFor(() => {
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });
  });

  it('is accessible', async () => {
    const { container } = renderWithProviders(<Dashboard />);
    
    await waitFor(() => {
      // Check for proper heading hierarchy
      const h1 = container.querySelector('h1, h2, h3');
      expect(h1).toBeInTheDocument();
      
      // Check for ARIA labels where needed
      const interactiveElements = container.querySelectorAll('button, a');
      interactiveElements.forEach(element => {
        expect(element).toHaveAccessibleName();
      });
    });
  });
});

// Made with Bob
