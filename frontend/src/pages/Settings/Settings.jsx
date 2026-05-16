import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonText,
  SkeletonPlaceholder,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Form,
  FormGroup,
  TextInput,
  Toggle,
  Button,
  Select,
  SelectItem,
  Tag,
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  InlineLoading,
  InlineNotification,
  ToastNotification,
} from '@carbon/react';
import {
  Settings as SettingsIcon,
  Save,
  CheckmarkFilled,
  WarningAltFilled,
  Renew,
  TrashCan,
} from '@carbon/icons-react';
import { runtimeSettingsService, settingsService } from '../../services/platformService';
import './Settings.scss';

const Settings = () => {
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState(0);
  const [toast, setToast] = useState(null);
  const [formData, setFormData] = useState({
    github: { token: '', org: '', repo: '' },
    gitlab: { token: '', org: '', repo: '' },
    ollama: { url: 'http://localhost:11434', model: 'llama3' },
    watsonx: { apiKey: '', projectId: '', model: 'granite-13b-chat' },
    vectorDb: { type: 'db2', connectionString: '', collection: 'dexter_kb' },
    notifications: {
      email: true,
      slack: false,
      critical: true,
      reviewCompleted: true,
      architectureViolations: true,
      securityAlerts: true,
    },
  });

  const { data: settingsData, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsService.getSettings,
  });

  const { data: runtimeSettings } = useQuery({
    queryKey: ['runtime-settings'],
    queryFn: runtimeSettingsService.get,
    refetchInterval: 10000,
  });

  const saveGithubToken = useMutation({
    mutationFn: ({ token, verify }) =>
      runtimeSettingsService.saveGithubToken(token, verify),
    onSuccess: (data) => {
      setToast({
        kind: 'success',
        title: 'GitHub token saved',
        subtitle: data.message || `Now authenticating as ${data.login}`,
      });
      queryClient.invalidateQueries({ queryKey: ['runtime-settings'] });
      setFormData((prev) => ({ ...prev, github: { ...prev.github, token: '' } }));
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'GitHub token rejected',
        subtitle: err?.response?.data?.detail || err?.message || 'Unknown error',
      });
    },
  });

  const clearGithubToken = useMutation({
    mutationFn: () => runtimeSettingsService.clearGithubToken(),
    onSuccess: () => {
      setToast({ kind: 'info', title: 'GitHub token cleared', subtitle: 'Backend now uses .env value or unauthenticated requests.' });
      queryClient.invalidateQueries({ queryKey: ['runtime-settings'] });
    },
  });

  const verifyGithubToken = useMutation({
    mutationFn: () => runtimeSettingsService.verifyGithubToken(),
    onSuccess: (data) => {
      if (data.ok) {
        setToast({
          kind: 'success',
          title: 'Token verified',
          subtitle: `GitHub accepts the current token as ${data.login}`,
        });
      } else {
        setToast({
          kind: 'error',
          title: 'Token invalid',
          subtitle: data.message || data.reason || 'GitHub rejected the token',
        });
      }
    },
  });

  if (isLoading) {
    return <SettingsSkeleton />;
  }

  const { organization = 'IBM Engineering', integrations = [] } = settingsData || {};

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckmarkFilled size={20} className="status-icon status-icon--success" />;
      case 'standby':
        return <WarningAltFilled size={20} className="status-icon status-icon--warning" />;
      case 'disconnected':
        return <WarningAltFilled size={20} className="status-icon status-icon--error" />;
      default:
        return null;
    }
  };

  const getStatusTag = (status) => {
    const statusMap = {
      connected: { type: 'green', label: 'Connected' },
      standby: { type: 'purple', label: 'Standby' },
      disconnected: { type: 'red', label: 'Disconnected' },
    };
    const config = statusMap[status] || statusMap.disconnected;
    return <Tag type={config.type}>{config.label}</Tag>;
  };

  const handleInputChange = (section, field, value) => {
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleToggle = (section, field) => {
    setFormData((prev) => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: !prev[section][field],
      },
    }));
  };

  const handleSave = () => {
    console.log('Saving settings:', formData);
    // In real app, call settingsService.updateSettings(formData)
  };

  const handleTestConnection = (provider) => {
    console.log('Testing connection for:', provider);
    // In real app, call settingsService.testConnection(provider)
  };

  const teamMembers = [
    { id: '1', name: 'Sarah Chen', email: 'sarah.chen@ibm.com', role: 'Admin', team: 'OpenShift' },
    { id: '2', name: 'Michael Rodriguez', email: 'michael.r@ibm.com', role: 'Developer', team: 'Db2' },
    { id: '3', name: 'Emily Watson', email: 'emily.w@ibm.com', role: 'Developer', team: 'API Platform' },
  ];

  const teamHeaders = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
    { key: 'role', header: 'Role' },
    { key: 'team', header: 'Team' },
  ];

  return (
    <div className="settings-page">
      <div className="page-header">
        <div className="page-header__title">
          <SettingsIcon size={32} />
          <h1>Settings</h1>
        </div>
        <p className="page-header__description">
          Configure integrations, AI models, and organization preferences
        </p>
      </div>

      <Grid className="settings-grid" narrow>
        <Column lg={16} md={8} sm={4}>
          <Tile className="settings-tile">
            <Tabs selectedIndex={selectedTab} onChange={({ selectedIndex }) => setSelectedTab(selectedIndex)}>
              <TabList aria-label="Settings sections" contained>
                <Tab>Integrations</Tab>
                <Tab>AI Configuration</Tab>
                <Tab>Vector Database</Tab>
                <Tab>Notifications</Tab>
                <Tab>Team & RBAC</Tab>
                <Tab>Organization</Tab>
              </TabList>
              <TabPanels>
                {/* Integrations Tab */}
                <TabPanel>
                  <div className="tab-content">
                    <h3>Integration Status</h3>
                    <div className="integration-status">
                      {integrations.map((integration) => (
                        <div key={integration.name} className="integration-item">
                          <div className="integration-item__info">
                            {getStatusIcon(integration.status)}
                            <div>
                              <h4>{integration.name}</h4>
                              <p>{integration.detail}</p>
                            </div>
                          </div>
                          {getStatusTag(integration.status)}
                        </div>
                      ))}
                    </div>

                    <h3>GitHub Integration</h3>
                    <Form onSubmit={(e) => e.preventDefault()}>
                      <FormGroup legendText="">
                        {runtimeSettings?.github?.configured ? (
                          <InlineNotification
                            kind="success"
                            title="GitHub token is configured"
                            subtitle={`Source: ${runtimeSettings.github.source}${
                              runtimeSettings.runtime_overrides?.github_token
                                ? ` (${runtimeSettings.runtime_overrides.github_token})`
                                : ''
                            }`}
                            lowContrast
                            hideCloseButton
                          />
                        ) : (
                          <InlineNotification
                            kind="warning"
                            title="No GitHub token configured"
                            subtitle="Public PR analysis works; private repos require a token."
                            lowContrast
                            hideCloseButton
                          />
                        )}
                        <TextInput
                          id="github-token"
                          labelText="GitHub Personal Access Token"
                          type="password"
                          placeholder="ghp_xxxxxxxxxxxx or github_pat_xxx"
                          helperText="Stored in backend memory only; cleared on restart. Generate at https://github.com/settings/tokens (scopes: repo, read:org)."
                          value={formData.github.token}
                          onChange={(e) => handleInputChange('github', 'token', e.target.value)}
                        />
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
                          <Button
                            kind="primary"
                            size="sm"
                            renderIcon={Save}
                            onClick={() => saveGithubToken.mutate({ token: formData.github.token, verify: true })}
                            disabled={!formData.github.token.trim() || saveGithubToken.isPending}
                          >
                            {saveGithubToken.isPending ? <InlineLoading description="Verifying..." /> : 'Verify & Save'}
                          </Button>
                          <Button
                            kind="tertiary"
                            size="sm"
                            onClick={() => verifyGithubToken.mutate()}
                            disabled={verifyGithubToken.isPending || !runtimeSettings?.github?.configured}
                          >
                            {verifyGithubToken.isPending ? <InlineLoading description="Testing..." /> : 'Test Current Token'}
                          </Button>
                          {runtimeSettings?.runtime_overrides?.github_token && (
                            <Button
                              kind="danger--tertiary"
                              size="sm"
                              renderIcon={TrashCan}
                              onClick={() => clearGithubToken.mutate()}
                            >
                              Clear runtime token
                            </Button>
                          )}
                        </div>
                      </FormGroup>
                    </Form>

                    <h3>GitLab Integration</h3>
                    <Form>
                      <FormGroup legendText="">
                        <TextInput
                          id="gitlab-token"
                          labelText="GitLab Personal Access Token"
                          type="password"
                          placeholder="glpat-xxxxxxxxxxxx"
                          helperText="Required for GitLab integration"
                          value={formData.gitlab.token}
                          onChange={(e) => handleInputChange('gitlab', 'token', e.target.value)}
                        />
                        <TextInput
                          id="gitlab-org"
                          labelText="Group/Organization"
                          placeholder="ibm-engineering"
                          value={formData.gitlab.org}
                          onChange={(e) => handleInputChange('gitlab', 'org', e.target.value)}
                        />
                        <Button
                          kind="tertiary"
                          size="sm"
                          onClick={() => handleTestConnection('gitlab')}
                        >
                          Test Connection
                        </Button>
                      </FormGroup>
                    </Form>
                  </div>
                </TabPanel>

                {/* AI Configuration Tab */}
                <TabPanel>
                  <div className="tab-content">
                    <h3>LLM Provider Selection</h3>
                    <Form>
                      <FormGroup legendText="">
                        <Select
                          id="llm-provider"
                          labelText="Primary LLM Provider"
                          defaultValue="ollama"
                        >
                          <SelectItem value="ollama" text="Ollama (Local)" />
                          <SelectItem value="watsonx" text="IBM watsonx.ai" />
                          <SelectItem value="claude" text="Anthropic Claude" />
                          <SelectItem value="gpt4" text="OpenAI GPT-4" />
                        </Select>
                      </FormGroup>
                    </Form>

                    <h3>Ollama Configuration</h3>
                    <Form>
                      <FormGroup legendText="">
                        <TextInput
                          id="ollama-url"
                          labelText="Ollama URL"
                          placeholder="http://localhost:11434"
                          value={formData.ollama.url}
                          onChange={(e) => handleInputChange('ollama', 'url', e.target.value)}
                        />
                        <Select
                          id="ollama-model"
                          labelText="Model"
                          value={formData.ollama.model}
                          onChange={(e) => handleInputChange('ollama', 'model', e.target.value)}
                        >
                          <SelectItem value="llama3" text="Llama 3" />
                          <SelectItem value="codellama" text="Code Llama" />
                          <SelectItem value="mistral" text="Mistral" />
                          <SelectItem value="mixtral" text="Mixtral" />
                        </Select>
                        <Button
                          kind="tertiary"
                          size="sm"
                          onClick={() => handleTestConnection('ollama')}
                        >
                          Test Connection
                        </Button>
                      </FormGroup>
                    </Form>

                    <h3>IBM watsonx.ai Configuration</h3>
                    <Form>
                      <FormGroup legendText="">
                        <TextInput
                          id="watsonx-api-key"
                          labelText="API Key"
                          type="password"
                          placeholder="Enter watsonx API key"
                          value={formData.watsonx.apiKey}
                          onChange={(e) => handleInputChange('watsonx', 'apiKey', e.target.value)}
                        />
                        <TextInput
                          id="watsonx-project-id"
                          labelText="Project ID"
                          placeholder="Enter project ID"
                          value={formData.watsonx.projectId}
                          onChange={(e) => handleInputChange('watsonx', 'projectId', e.target.value)}
                        />
                        <Select
                          id="watsonx-model"
                          labelText="Model"
                          value={formData.watsonx.model}
                          onChange={(e) => handleInputChange('watsonx', 'model', e.target.value)}
                        >
                          <SelectItem value="granite-13b-chat" text="Granite 13B Chat" />
                          <SelectItem value="granite-20b-code" text="Granite 20B Code" />
                          <SelectItem value="llama-2-70b" text="Llama 2 70B" />
                        </Select>
                        <Button
                          kind="tertiary"
                          size="sm"
                          onClick={() => handleTestConnection('watsonx')}
                        >
                          Test Connection
                        </Button>
                      </FormGroup>
                    </Form>
                  </div>
                </TabPanel>

                {/* Vector Database Tab */}
                <TabPanel>
                  <div className="tab-content">
                    <h3>Vector Database Configuration</h3>
                    <Form>
                      <FormGroup legendText="">
                        <Select
                          id="vector-db-type"
                          labelText="Vector Database Type"
                          value={formData.vectorDb.type}
                          onChange={(e) => handleInputChange('vectorDb', 'type', e.target.value)}
                        >
                          <SelectItem value="db2" text="IBM Db2 Vector (langchain-db2)" />
                          <SelectItem value="inmemory" text="In-memory (development only)" />
                        </Select>
                        <TextInput
                          id="vector-db-connection"
                          labelText="Connection String"
                          placeholder="Enter connection string"
                          value={formData.vectorDb.connectionString}
                          onChange={(e) => handleInputChange('vectorDb', 'connectionString', e.target.value)}
                        />
                        <TextInput
                          id="vector-db-collection"
                          labelText="Collection/Index Name"
                          placeholder="dexter_kb"
                          value={formData.vectorDb.collection}
                          onChange={(e) => handleInputChange('vectorDb', 'collection', e.target.value)}
                        />
                        <Button
                          kind="tertiary"
                          size="sm"
                          onClick={() => handleTestConnection('vectordb')}
                        >
                          Test Connection
                        </Button>
                      </FormGroup>
                    </Form>
                  </div>
                </TabPanel>

                {/* Notifications Tab */}
                <TabPanel>
                  <div className="tab-content">
                    <h3>Notification Channels</h3>
                    <Form>
                      <FormGroup legendText="">
                        <Toggle
                          id="notif-email"
                          labelText="Email Notifications"
                          toggled={formData.notifications.email}
                          onToggle={() => handleToggle('notifications', 'email')}
                        />
                        <Toggle
                          id="notif-slack"
                          labelText="Slack Integration"
                          toggled={formData.notifications.slack}
                          onToggle={() => handleToggle('notifications', 'slack')}
                        />
                      </FormGroup>
                    </Form>

                    <h3>Notification Preferences</h3>
                    <Form>
                      <FormGroup legendText="">
                        <Toggle
                          id="notif-critical"
                          labelText="Critical Findings"
                          toggled={formData.notifications.critical}
                          onToggle={() => handleToggle('notifications', 'critical')}
                        />
                        <Toggle
                          id="notif-review"
                          labelText="Review Completed"
                          toggled={formData.notifications.reviewCompleted}
                          onToggle={() => handleToggle('notifications', 'reviewCompleted')}
                        />
                        <Toggle
                          id="notif-architecture"
                          labelText="Architecture Violations"
                          toggled={formData.notifications.architectureViolations}
                          onToggle={() => handleToggle('notifications', 'architectureViolations')}
                        />
                        <Toggle
                          id="notif-security"
                          labelText="Security Alerts"
                          toggled={formData.notifications.securityAlerts}
                          onToggle={() => handleToggle('notifications', 'securityAlerts')}
                        />
                      </FormGroup>
                    </Form>
                  </div>
                </TabPanel>

                {/* Team & RBAC Tab */}
                <TabPanel>
                  <div className="tab-content">
                    <h3>Team Members</h3>
                    <DataTable rows={teamMembers} headers={teamHeaders}>
                      {({
                        rows,
                        headers,
                        getHeaderProps,
                        getRowProps,
                        getTableProps,
                        getTableContainerProps,
                      }) => (
                        <TableContainer {...getTableContainerProps()}>
                          <Table {...getTableProps()} size="md" useZebraStyles>
                            <TableHead>
                              <TableRow>
                                {headers.map((header) => (
                                  <TableHeader key={header.key} {...getHeaderProps({ header })}>
                                    {header.header}
                                  </TableHeader>
                                ))}
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {rows.map((row) => (
                                <TableRow key={row.id} {...getRowProps({ row })}>
                                  {row.cells.map((cell) => (
                                    <TableCell key={cell.id}>{cell.value}</TableCell>
                                  ))}
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      )}
                    </DataTable>
                    <Button kind="primary" size="sm" style={{ marginTop: '1rem' }}>
                      Invite New Member
                    </Button>
                  </div>
                </TabPanel>

                {/* Organization Tab */}
                <TabPanel>
                  <div className="tab-content">
                    <h3>Organization Settings</h3>
                    <Form>
                      <FormGroup legendText="">
                        <TextInput
                          id="org-name"
                          labelText="Organization Name"
                          defaultValue={organization}
                        />
                        <Select
                          id="default-review-mode"
                          labelText="Default Review Mode"
                          defaultValue="automatic"
                        >
                          <SelectItem value="automatic" text="Automatic (AI-driven)" />
                          <SelectItem value="manual" text="Manual Review" />
                          <SelectItem value="hybrid" text="Hybrid (AI + Human)" />
                        </Select>
                        <Select
                          id="compliance-level"
                          labelText="Compliance Level"
                          defaultValue="standard"
                        >
                          <SelectItem value="standard" text="Standard" />
                          <SelectItem value="strict" text="Strict" />
                          <SelectItem value="enterprise" text="Enterprise" />
                        </Select>
                      </FormGroup>
                    </Form>
                  </div>
                </TabPanel>
              </TabPanels>
            </Tabs>

            <div className="settings-actions">
              <Button kind="primary" renderIcon={Save} onClick={handleSave}>
                Save Settings
              </Button>
              <Button kind="secondary" renderIcon={Renew}>
                Reset to Defaults
              </Button>
            </div>
          </Tile>
        </Column>
      </Grid>

      {toast && (
        <ToastNotification
          kind={toast.kind}
          title={toast.title}
          subtitle={toast.subtitle}
          timeout={5000}
          onClose={() => setToast(null)}
          style={{ position: 'fixed', bottom: 16, right: 16, zIndex: 9000 }}
        />
      )}
    </div>
  );
};

const SettingsSkeleton = () => (
  <div className="settings-page">
    <div className="page-header">
      <SkeletonText heading width="30%" />
      <SkeletonText width="50%" />
    </div>
    <Grid narrow>
      <Column lg={16} md={8} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '600px' }} />
        </Tile>
      </Column>
    </Grid>
  </div>
);

export default Settings;

// Made with Bob
