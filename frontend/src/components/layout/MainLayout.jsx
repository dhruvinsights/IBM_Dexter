import { useLayoutEffect, useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { Content, Theme } from '@carbon/react';
import AppHeader from './AppHeader';
import SideNav from './SideNav';
import useThemeStore from '../../store/useThemeStore';
import './MainLayout.scss';

const MainLayout = () => {
  // Initialize sidebar state based on screen size
  const [isSideNavExpanded, setIsSideNavExpanded] = useState(() => {
    return window.innerWidth >= 1056;
  });
  const { theme } = useThemeStore();

  // Carbon tokens and portaled UI (toasts, modals) resolve from the document root.
  // Without this, `data-carbon-theme` only lived under `.dexter-shell` and light theme
  // could leave body/outside nodes with wrong `--cds-text-*` (e.g. light gray on white).
  useLayoutEffect(() => {
    document.documentElement.setAttribute('data-carbon-theme', theme);
  }, [theme]);

  // Handle window resize to auto-close/open sidebar
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1056) {
        setIsSideNavExpanded(true);
      } else {
        setIsSideNavExpanded(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSideNav = () => {
    setIsSideNavExpanded(!isSideNavExpanded);
  };

  return (
    <Theme theme={theme}>
      <div className="dexter-shell" data-carbon-theme={theme}>
        <AppHeader
          onMenuClick={toggleSideNav}
          isSideNavExpanded={isSideNavExpanded}
        />
        <SideNav
          isOpen={isSideNavExpanded}
          onToggle={toggleSideNav}
        />
        <Content className="dexter-content">
          <div className="dexter-content-inner">
            <Outlet />
          </div>
        </Content>
      </div>
    </Theme>
  );
};

export default MainLayout;

// Made with Bob
