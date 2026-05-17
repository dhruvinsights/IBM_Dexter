import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
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
import { APP_SHELL_BASE } from '../../constants/appConstants';
import { knowledgeBaseService, runtimeSettingsService } from '../../services/platformService';
import './AppHeader.scss';

const AppHeader = () => {
  const { theme, toggleTheme } = useThemeStore();
  const [isUserPanelExpanded, setIsUserPanelExpanded] = useState(false);
  const [isNotificationPanelExpanded, setIsNotificationPanelExpanded] = useState(false);

  const { data: runtimeSettings } = useQuery({
    queryKey: ['runtime-settings'],
    queryFn: runtimeSettingsService.get,
    staleTime: 30_000,
  });

  const { data: ollamaHealth } = useQuery({
    queryKey: ['ollama-health'],
    queryFn: () => runtimeSettingsService.ollamaHealth(),
    staleTime: 30_000,
    retry: false,
  });

  const { data: kbStatus } = useQuery({
    queryKey: ['kb-status'],
    queryFn: knowledgeBaseService.getStatus,
    refetchOnWindowFocus: true,
    refetchInterval: 12_000,
  });

  const kbBackend = kbStatus?.backend;
  const kbVdbReachable = kbStatus?.vector_db_reachable;
  const db2Configured = kbBackend === 'db2';
  let db2TagType = 'purple';
  let db2Label = kbBackend || 'In-memory';
  if (db2Configured) {
    if (kbVdbReachable === false) {
      db2TagType = 'red';
      db2Label = 'Unreachable';
    } else {
      db2TagType = 'green';
      db2Label = 'Active';
    }
  }

  const integrationStatus = {
    github: Boolean(runtimeSettings?.github?.configured),
    ollama: Boolean(ollamaHealth?.ok),
  };

  const aiStatus = ollamaHealth?.ok ? 'active' : 'warning';
  const notificationCount = 0;

  return (
    <Header aria-label="IBM Dexter" className="dexter-header">
      <div className="dexter-header__brand">
        <a href="/" className="dexter-header__logo-link" aria-label="Dexter home">
          <img src="/Dexter_logo.png" alt="" width={28} height={28} />
        </a>
        <HeaderName href={`${APP_SHELL_BASE}/dashboard`} prefix="IBM">
          Dexter
        </HeaderName>
      </div>
      
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
            <h4 className="notification-panel__title">Notifications</h4>
            <p className="cds--helper-text">No notifications yet.</p>
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
              <strong>Dexter user</strong>
              <p className="cds--helper-text">Local session</p>
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
                <Tag type={db2TagType} size="sm">
                  {db2Label}
                </Tag>
              </div>
            </div>
            <SwitcherDivider />
            <SwitcherItem aria-label="Profile" href="/profile">
              Profile
            </SwitcherItem>
            <SwitcherItem aria-label="Settings" href={`${APP_SHELL_BASE}/settings`}>
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
