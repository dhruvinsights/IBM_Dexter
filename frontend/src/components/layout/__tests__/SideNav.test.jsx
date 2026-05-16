import { describe, it, expect, vi } from 'vitest';
import { screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../../../utils/testUtils';
import SideNav from '../SideNav';

describe('SideNav Component', () => {
  it('renders navigation items', () => {
    renderWithProviders(<SideNav />);
    
    // Check for main navigation items
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Pull Requests')).toBeInTheDocument();
    expect(screen.getByText('Architecture')).toBeInTheDocument();
    expect(screen.getByText('Security')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
    expect(screen.getByText('Team Analytics')).toBeInTheDocument();
    expect(screen.getByText('AI Agents')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('highlights active navigation item based on current route', () => {
    renderWithProviders(<SideNav />, { route: '/dashboard' });
    
    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveClass('cds--side-nav__link--current');
  });

  it('navigates to correct route when item is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<SideNav />);
    
    const pullRequestsLink = screen.getByText('Pull Requests');
    await user.click(pullRequestsLink);
    
    // Check if URL changed
    expect(window.location.pathname).toBe('/pull-requests');
  });

  it('renders with correct ARIA labels for accessibility', () => {
    renderWithProviders(<SideNav />);
    
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    
    // Check for links
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
    
    // Each link should have accessible text
    links.forEach(link => {
      expect(link).toHaveAccessibleName();
    });
  });

  it('displays icons for each navigation item', () => {
    const { container } = renderWithProviders(<SideNav />);
    
    // Check for SVG icons
    const icons = container.querySelectorAll('svg');
    expect(icons.length).toBeGreaterThanOrEqual(8); // At least 8 nav items
  });

  it('applies correct styling classes', () => {
    const { container } = renderWithProviders(<SideNav />);
    
    const sideNav = container.querySelector('.cds--side-nav');
    expect(sideNav).toBeInTheDocument();
    expect(sideNav).toHaveClass('cds--side-nav--expanded');
  });

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    renderWithProviders(<SideNav />);
    
    const firstLink = screen.getByText('Dashboard');
    firstLink.focus();
    
    expect(firstLink).toHaveFocus();
    
    // Tab to next item
    await user.tab();
    const secondLink = screen.getByText('Pull Requests');
    expect(secondLink).toHaveFocus();
  });

  it('renders all navigation sections', () => {
    renderWithProviders(<SideNav />);
    
    // Main section
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Pull Requests')).toBeInTheDocument();
    
    // Analysis section
    expect(screen.getByText('Architecture')).toBeInTheDocument();
    expect(screen.getByText('Security')).toBeInTheDocument();
    
    // Intelligence section
    expect(screen.getByText('Knowledge Base')).toBeInTheDocument();
    expect(screen.getByText('Team Analytics')).toBeInTheDocument();
    expect(screen.getByText('AI Agents')).toBeInTheDocument();
    
    // Settings section
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });
});

// Made with Bob
