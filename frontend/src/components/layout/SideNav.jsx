import { useLocation, useNavigate } from 'react-router-dom';
import {
  SideNav as CarbonSideNav,
  SideNavItems,
  SideNavLink,
  SideNavDivider,
} from '@carbon/react';
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

const SideNav = ({ isOpen }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path;

  const handleNavigation = (e, path) => {
    e.preventDefault();
    navigate(path);
  };

  return (
    <CarbonSideNav
      aria-label="IBM Dexter Navigation"
      expanded={isOpen}
      isPersistent={true}
      isFixedNav
      className="dexter-sidenav"
    >
      <SideNavItems>
        {/* Core Navigation */}
        <SideNavLink
          renderIcon={Dashboard}
          href="/"
          isActive={isActive('/')}
          onClick={(e) => handleNavigation(e, '/')}
        >
          Dashboard
        </SideNavLink>
        
        <SideNavLink
          renderIcon={PullRequest}
          href="/pull-requests"
          isActive={isActive('/pull-requests')}
          onClick={(e) => handleNavigation(e, '/pull-requests')}
        >
          Pull Requests
        </SideNavLink>
        
        <SideNavLink
          renderIcon={DocumentTasks}
          href="/reviews"
          isActive={isActive('/reviews')}
          onClick={(e) => handleNavigation(e, '/reviews')}
        >
          Reviews
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Catalog}
          href="/repositories"
          isActive={isActive('/repositories')}
          onClick={(e) => handleNavigation(e, '/repositories')}
        >
          Repositories
        </SideNavLink>

        <SideNavDivider />

        {/* Analysis & Insights */}
        <SideNavLink
          renderIcon={ReferenceArchitecture}
          href="/architecture"
          isActive={isActive('/architecture')}
          onClick={(e) => handleNavigation(e, '/architecture')}
        >
          Architecture
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Security}
          href="/security"
          isActive={isActive('/security')}
          onClick={(e) => handleNavigation(e, '/security')}
        >
          Security
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Book}
          href="/knowledge-base"
          isActive={isActive('/knowledge-base')}
          onClick={(e) => handleNavigation(e, '/knowledge-base')}
        >
          Knowledge Base
        </SideNavLink>

        <SideNavDivider />

        {/* Analytics & Team */}
        <SideNavLink
          renderIcon={Analytics}
          href="/analytics"
          isActive={isActive('/analytics')}
          onClick={(e) => handleNavigation(e, '/analytics')}
        >
          Analytics
        </SideNavLink>

        <SideNavLink
          renderIcon={UserMultiple}
          href="/team-insights"
          isActive={isActive('/team-insights')}
          onClick={(e) => handleNavigation(e, '/team-insights')}
        >
          Team Insights
        </SideNavLink>

        <SideNavLink
          renderIcon={Bot}
          href="/ai-agents"
          isActive={isActive('/ai-agents')}
          onClick={(e) => handleNavigation(e, '/ai-agents')}
        >
          AI Agents
        </SideNavLink>

        <SideNavDivider />

        {/* Settings */}
        <SideNavLink
          renderIcon={Settings}
          href="/settings"
          isActive={isActive('/settings')}
          onClick={(e) => handleNavigation(e, '/settings')}
        >
          Settings
        </SideNavLink>
      </SideNavItems>
    </CarbonSideNav>
  );
};

export default SideNav;

// Made with Bob
