import { useLocation, useNavigate } from 'react-router-dom';
import {
  SideNav as CarbonSideNav,
  SideNavItems,
  SideNavLink,
  SideNavDivider,
} from '@carbon/react';
import { APP_SHELL_BASE } from '../../constants/appConstants';
import {
  Dashboard,
  DocumentTasks,
  Catalog,
  Settings,
  PullRequest,
  Security,
  ReferenceArchitecture,
  Book,
  Analytics,
  UserMultiple,
  Bot,
} from '@carbon/icons-react';
import './SideNav.scss';

const SideNav = ({ isOpen, onToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path || location.pathname === `${path}/`;

  const handleNavigation = (e, path) => {
    e.preventDefault();
    navigate(path);
    // Close sidebar on mobile after navigation
    if (window.innerWidth < 1056 && onToggle) {
      onToggle();
    }
  };

  const handleOverlayClick = () => {
    if (onToggle) {
      onToggle();
    }
  };

  return (
    <>
      {/* Mobile overlay backdrop */}
      {isOpen && (
        <div
          className="dexter-sidenav-overlay"
          onClick={handleOverlayClick}
          aria-hidden="true"
        />
      )}
      <CarbonSideNav
        aria-label="IBM Dexter Navigation"
        expanded={isOpen}
        isPersistent={false}
        isFixedNav
        className="dexter-sidenav"
      >
      <SideNavItems>
        {/* Core Navigation */}
        <SideNavLink
          renderIcon={Dashboard}
          href={`${APP_SHELL_BASE}/dashboard`}
          isActive={isActive(`${APP_SHELL_BASE}/dashboard`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/dashboard`)}
        >
          Dashboard
        </SideNavLink>
        
        <SideNavLink
          renderIcon={PullRequest}
          href={`${APP_SHELL_BASE}/pull-requests`}
          isActive={isActive(`${APP_SHELL_BASE}/pull-requests`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/pull-requests`)}
        >
          Pull Requests
        </SideNavLink>
        
        <SideNavLink
          renderIcon={DocumentTasks}
          href={`${APP_SHELL_BASE}/reviews`}
          isActive={isActive(`${APP_SHELL_BASE}/reviews`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/reviews`)}
        >
          Reviews
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Catalog}
          href={`${APP_SHELL_BASE}/repositories`}
          isActive={isActive(`${APP_SHELL_BASE}/repositories`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/repositories`)}
        >
          Repositories
        </SideNavLink>

        <SideNavDivider />

        {/* Analysis & Insights */}
        <SideNavLink
          renderIcon={ReferenceArchitecture}
          href={`${APP_SHELL_BASE}/architecture`}
          isActive={isActive(`${APP_SHELL_BASE}/architecture`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/architecture`)}
        >
          Architecture
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Security}
          href={`${APP_SHELL_BASE}/security`}
          isActive={isActive(`${APP_SHELL_BASE}/security`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/security`)}
        >
          Security
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Book}
          href={`${APP_SHELL_BASE}/knowledge-base`}
          isActive={isActive(`${APP_SHELL_BASE}/knowledge-base`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/knowledge-base`)}
        >
          Knowledge Base
        </SideNavLink>

        <SideNavDivider />

        {/* Analytics & Team */}
        <SideNavLink
          renderIcon={Analytics}
          href={`${APP_SHELL_BASE}/analytics`}
          isActive={isActive(`${APP_SHELL_BASE}/analytics`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/analytics`)}
        >
          Analytics
        </SideNavLink>

        <SideNavLink
          renderIcon={UserMultiple}
          href={`${APP_SHELL_BASE}/team-insights`}
          isActive={isActive(`${APP_SHELL_BASE}/team-insights`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/team-insights`)}
        >
          Team Insights
        </SideNavLink>

        <SideNavLink
          renderIcon={Bot}
          href={`${APP_SHELL_BASE}/ai-agents`}
          isActive={isActive(`${APP_SHELL_BASE}/ai-agents`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/ai-agents`)}
        >
          AI Agents
        </SideNavLink>

        <SideNavDivider />

        {/* Settings */}
        <SideNavLink
          renderIcon={Settings}
          href={`${APP_SHELL_BASE}/settings`}
          isActive={isActive(`${APP_SHELL_BASE}/settings`)}
          onClick={(e) => handleNavigation(e, `${APP_SHELL_BASE}/settings`)}
        >
          Settings
        </SideNavLink>
      </SideNavItems>
    </CarbonSideNav>
    </>
  );
};

export default SideNav;

// Made with Bob
