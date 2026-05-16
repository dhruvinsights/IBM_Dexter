import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Content, Theme } from '@carbon/react';
import AppHeader from './AppHeader';
import SideNav from './SideNav';
import useThemeStore from '../../store/useThemeStore';

const MainLayout = () => {
  const [isSideNavExpanded] = useState(false);
  const { theme } = useThemeStore();

  return (
    <Theme theme={theme}>
      <div className="app-container" data-carbon-theme={theme}>
        <AppHeader />
        <SideNav isOpen={isSideNavExpanded} />
        <Content className="main-content">
          <Outlet />
        </Content>
      </div>
    </Theme>
  );
};

export default MainLayout;

// Made with Bob
