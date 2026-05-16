import { useLocation, useNavigate } from 'react-router-dom';
import {
  SideNav as CarbonSideNav,
  SideNavItems,
  SideNavLink,
  SideNavMenu,
  SideNavMenuItem,
} from '@carbon/react';
import {
  Dashboard,
  DocumentTasks,
  Catalog,
  DataBase,
  Settings,
  ChartLineData,
} from '@carbon/icons-react';

const SideNav = ({ isOpen }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path) => location.pathname === path;

  return (
    <CarbonSideNav
      aria-label="Side navigation"
      expanded={isOpen}
      isPersistent={false}
    >
      <SideNavItems>
        <SideNavLink
          renderIcon={Dashboard}
          href="/"
          isActive={isActive('/')}
          onClick={(e) => {
            e.preventDefault();
            navigate('/');
          }}
        >
          Dashboard
        </SideNavLink>
        
        <SideNavMenu
          renderIcon={DocumentTasks}
          title="Reviews"
          defaultExpanded={location.pathname.startsWith('/reviews')}
        >
          <SideNavMenuItem
            href="/reviews"
            isActive={isActive('/reviews')}
            onClick={(e) => {
              e.preventDefault();
              navigate('/reviews');
            }}
          >
            All Reviews
          </SideNavMenuItem>
          <SideNavMenuItem
            href="/reviews/pending"
            isActive={isActive('/reviews/pending')}
            onClick={(e) => {
              e.preventDefault();
              navigate('/reviews/pending');
            }}
          >
            Pending
          </SideNavMenuItem>
          <SideNavMenuItem
            href="/reviews/completed"
            isActive={isActive('/reviews/completed')}
            onClick={(e) => {
              e.preventDefault();
              navigate('/reviews/completed');
            }}
          >
            Completed
          </SideNavMenuItem>
        </SideNavMenu>
        
        <SideNavLink
          renderIcon={Catalog}
          href="/repositories"
          isActive={isActive('/repositories')}
          onClick={(e) => {
            e.preventDefault();
            navigate('/repositories');
          }}
        >
          Repositories
        </SideNavLink>
        
        <SideNavLink
          renderIcon={DataBase}
          href="/memory"
          isActive={isActive('/memory')}
          onClick={(e) => {
            e.preventDefault();
            navigate('/memory');
          }}
        >
          AI Memory
        </SideNavLink>
        
        <SideNavLink
          renderIcon={ChartLineData}
          href="/analytics"
          isActive={isActive('/analytics')}
          onClick={(e) => {
            e.preventDefault();
            navigate('/analytics');
          }}
        >
          Analytics
        </SideNavLink>
        
        <SideNavLink
          renderIcon={Settings}
          href="/settings"
          isActive={isActive('/settings')}
          onClick={(e) => {
            e.preventDefault();
            navigate('/settings');
          }}
        >
          Settings
        </SideNavLink>
      </SideNavItems>
    </CarbonSideNav>
  );
};

export default SideNav;

// Made with Bob
