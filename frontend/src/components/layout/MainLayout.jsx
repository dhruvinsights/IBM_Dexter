import { useLayoutEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Content, Theme } from '@carbon/react';
import AppHeader from './AppHeader';
import SideNav from './SideNav';
import useThemeStore from '../../store/useThemeStore';
import './MainLayout.scss';

const MainLayout = () => {
  const [isSideNavExpanded, setIsSideNavExpanded] = useState(true);
  const { theme } = useThemeStore();

  // Carbon tokens and portaled UI (toasts, modals) resolve from the document root.
  // Without this, `data-carbon-theme` only lived under `.dexter-shell` and light theme
  // could leave body/outside nodes with wrong `--cds-text-*` (e.g. light gray on white).
  useLayoutEffect(() => {
    document.documentElement.setAttribute('data-carbon-theme', theme);
  }, [theme]);

  const toggleSideNav = () => {
    setIsSideNavExpanded(!isSideNavExpanded);
  };

  return (
    <Theme theme={theme}>
      <div className="dexter-shell" data-carbon-theme={theme}>
        <AppHeader />
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
