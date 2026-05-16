import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Content, Theme } from '@carbon/react';
import AppHeader from './AppHeader';
import SideNav from './SideNav';
import useThemeStore from '../../store/useThemeStore';
import './MainLayout.scss';

const MainLayout = () => {
  const [isSideNavExpanded, setIsSideNavExpanded] = useState(true);
  const { theme } = useThemeStore();

  const toggleSideNav = () => {
    setIsSideNavExpanded(!isSideNavExpanded);
  };

  return (
    <Theme theme={theme}>
      <div className="dexter-shell" data-carbon-theme={theme}>
        <AppHeader onToggleSideNav={toggleSideNav} />
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
