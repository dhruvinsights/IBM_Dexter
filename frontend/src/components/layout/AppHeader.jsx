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
  Search,
  Tag,
} from '@carbon/react';
import {
  Asleep,
  Light,
  Notification,
  UserAvatar,
  Chip,
  CheckmarkFilled,
  WarningAltFilled,
} from '@carbon/icons-react';
import useThemeStore from '../../store/useThemeStore';
import './AppHeader.scss';

const AppHeader = () => {
  const { theme, toggleTheme } = useThemeStore();
  const [isUserPanelExpanded, setIsUserPanelExpanded] = useState(false);
  const [isNotificationPanelExpanded, setIsNotificationPanelExpanded] = useState(false);
  
  // Mock data for demo
  const aiStatus = 'active'; // active, warning, error
  const integrationStatus = {
    github: true,
    ollama: true,
    db2: true,
  };
  const notificationCount = 3;

  return (
    <Header aria-label="IBM Dexter" className="dexter-header">
      <HeaderName href="/" prefix="IBM">
        Dexter
      </HeaderName>
      
      {/* Organization/Context Indicator */}
      <div className="dexter-header__context">
        <Tag type="blue" size="sm">
          IBM Engineering
        </Tag>
      </div>
      
      <HeaderGlobalBar>
        {/* Search */}
        <div className="dexter-header__search">
          <Search
            size="lg"
            placeholder="Search repositories, PRs, reviews..."
            labelText="Search"
            closeButtonLabelText="Clear search"
            id="header-search"
          />
        </div>
        
        {/* AI Status Indicator */}
        <HeaderGlobalAction
          aria-label="AI Status"
          tooltipAlignment="end"
          className="dexter-header__ai-status"
        >
          <Chip size={20} />
          {aiStatus === 'active' && (
            <CheckmarkFilled size={12} className="status-indicator status-active" />
          )}
          {aiStatus === 'warning' && (
            <WarningAltFilled size={12} className="status-indicator status-warning" />
          )}
        </HeaderGlobalAction>
        
        {/* Theme Toggle */}
        <HeaderGlobalAction
          aria-label={`Switch to ${theme === 'g100' ? 'light' : 'dark'} theme`}
          onClick={toggleTheme}
          tooltipAlignment="end"
        >
          {theme === 'g100' ? <Light size={20} /> : <Asleep size={20} />}
        </HeaderGlobalAction>
        
        {/* Notifications */}
        <HeaderGlobalAction
          aria-label="Notifications"
          tooltipAlignment="end"
          isActive={isNotificationPanelExpanded}
          onClick={() => setIsNotificationPanelExpanded(!isNotificationPanelExpanded)}
        >
          <Notification size={20} />
          {notificationCount > 0 && (
            <span className="notification-badge">{notificationCount}</span>
          )}
        </HeaderGlobalAction>
        
        {/* User Menu */}
        <HeaderGlobalAction
          aria-label="User menu"
          tooltipAlignment="end"
          isActive={isUserPanelExpanded}
          onClick={() => setIsUserPanelExpanded(!isUserPanelExpanded)}
        >
          <UserAvatar size={20} />
        </HeaderGlobalAction>
      </HeaderGlobalBar>
      
      {/* Notifications Panel */}
      <HeaderPanel
        aria-label="Notifications"
        expanded={isNotificationPanelExpanded}
      >
        <Switcher aria-label="Notifications">
          <div className="notification-panel">
            <h4 className="notification-panel__title">Recent Notifications</h4>
            <SwitcherItem
              aria-label="New security findings for pull request 123"
              href="/reviews/123"
            >
              <div className="notification-item">
                <strong>New security findings</strong>
                <p>3 critical vulnerabilities detected in PR #123</p>
                <span className="notification-time">5 minutes ago</span>
              </div>
            </SwitcherItem>
            <SwitcherItem
              aria-label="Review completed for authentication service"
              href="/reviews/122"
            >
              <div className="notification-item">
                <strong>Review completed</strong>
                <p>AI review finished for authentication-service</p>
                <span className="notification-time">1 hour ago</span>
              </div>
            </SwitcherItem>
            <SwitcherItem
              aria-label="New pull request 124 ready for review"
              href="/pull-requests"
            >
              <div className="notification-item">
                <strong>New pull request</strong>
                <p>PR #124 ready for review</p>
                <span className="notification-time">2 hours ago</span>
              </div>
            </SwitcherItem>
            <SwitcherDivider />
            <SwitcherItem aria-label="View all notifications" href="/notifications">
              View all notifications
            </SwitcherItem>
          </div>
        </Switcher>
      </HeaderPanel>
      
      {/* User Menu Panel */}
      <HeaderPanel
        aria-label="User menu"
        expanded={isUserPanelExpanded}
      >
        <Switcher aria-label="User menu">
          <div className="user-panel">
            <div className="user-panel__info">
              <strong>John Doe</strong>
              <p>john.doe@ibm.com</p>
              <p className="user-role">Engineering Lead</p>
            </div>
            <SwitcherDivider />
            <div className="integration-status">
              <h5>Integrations</h5>
              <div className="integration-item">
                <span>GitHub</span>
                <Tag type={integrationStatus.github ? 'green' : 'red'} size="sm">
                  {integrationStatus.github ? 'Connected' : 'Disconnected'}
                </Tag>
              </div>
              <div className="integration-item">
                <span>Ollama</span>
                <Tag type={integrationStatus.ollama ? 'green' : 'red'} size="sm">
                  {integrationStatus.ollama ? 'Active' : 'Inactive'}
                </Tag>
              </div>
              <div className="integration-item">
                <span>Db2 Vector</span>
                <Tag type={integrationStatus.db2 ? 'green' : 'red'} size="sm">
                  {integrationStatus.db2 ? 'Connected' : 'Disconnected'}
                </Tag>
              </div>
            </div>
            <SwitcherDivider />
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
          </div>
        </Switcher>
      </HeaderPanel>
    </Header>
  );
};

export default AppHeader;

// Made with Bob
