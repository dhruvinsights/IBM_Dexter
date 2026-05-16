import { useState } from 'react';
import {
  Header,
  HeaderName,
  HeaderGlobalBar,
  HeaderGlobalAction,
  HeaderPanel,
  Switcher,
  SwitcherItem,
  SwitcherDivider,
} from '@carbon/react';
import {
  Asleep,
  Light,
  Notification,
  UserAvatar,
} from '@carbon/icons-react';
import useThemeStore from '../../store/useThemeStore';

const AppHeader = () => {
  const { theme, toggleTheme } = useThemeStore();
  const [isUserPanelExpanded, setIsUserPanelExpanded] = useState(false);

  return (
    <Header aria-label="IBM Dexter">
      <HeaderName href="/" prefix="IBM">
        Dexter AI Code Reviewer
      </HeaderName>
      
      <HeaderGlobalBar>
        <HeaderGlobalAction
          aria-label="Toggle theme"
          onClick={toggleTheme}
          tooltipAlignment="end"
        >
          {theme === 'white' ? <Asleep size={20} /> : <Light size={20} />}
        </HeaderGlobalAction>
        
        <HeaderGlobalAction
          aria-label="Notifications"
          tooltipAlignment="end"
        >
          <Notification size={20} />
        </HeaderGlobalAction>
        
        <HeaderGlobalAction
          aria-label="User menu"
          tooltipAlignment="end"
          isActive={isUserPanelExpanded}
          onClick={() => setIsUserPanelExpanded(!isUserPanelExpanded)}
        >
          <UserAvatar size={20} />
        </HeaderGlobalAction>
      </HeaderGlobalBar>
      
      <HeaderPanel
        aria-label="User menu"
        expanded={isUserPanelExpanded}
      >
        <Switcher aria-label="User menu">
          <SwitcherItem aria-label="Profile" href="/profile">
            Profile
          </SwitcherItem>
          <SwitcherItem aria-label="Settings" href="/settings">
            Settings
          </SwitcherItem>
          <SwitcherDivider />
          <SwitcherItem aria-label="Logout" href="/logout">
            Logout
          </SwitcherItem>
        </Switcher>
      </HeaderPanel>
    </Header>
  );
};

export default AppHeader;

// Made with Bob
