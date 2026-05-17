import { useState, useEffect, useMemo } from 'react';
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
  TextArea,
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

const MASK_SECRETS_STORAGE_KEY = 'dexter-settings-mask-secrets-demo';

const Settings = () => {
  const queryClient = useQueryClient();
  const [selectedTab, setSelectedTab] = useState(0);
  const [toast, setToast] = useState(null);
  const [maskSecretsDemo, setMaskSecretsDemo] = useState(() => {
    if (typeof window === 'undefined') return false;
    try {
      return window.localStorage.getItem(MASK_SECRETS_STORAGE_KEY) === '1';
    } catch {
      return false;
    }
  });
  const [formData, setFormData] = useState({
    github: { token: '', org: '', repo: '' },
    gitlab: { token: '', org: '', repo: '' },
    ollama: { url: 'http://localhost:11434', model: '' },
    watsonx: { apiKey: '', projectId: '', model: 'granite-13b-chat' },
    vectorDb: { type: 'db2', connectionString: '', collection: 'DEXTER', schema: '' },
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

  useEffect(() => {
    if (!runtimeSettings?.llm) return;
    setFormData((prev) => ({
      ...prev,
      ollama: {
        url: runtimeSettings.llm.base_url || prev.ollama.url,
        model: runtimeSettings.llm.model || prev.ollama.model,
      },
      vectorDb: {
        ...prev.vectorDb,
        type: runtimeSettings.vector_db?.type || prev.vectorDb.type,
        collection:
          runtimeSettings.vector_db?.db2_kb_table_prefix || prev.vectorDb.collection,
        schema: runtimeSettings.runtime_overrides?.db2_schema ?? prev.vectorDb.schema ?? '',
      },
    }));
  }, [runtimeSettings]);

  useEffect(() => {
    try {
      window.localStorage.setItem(MASK_SECRETS_STORAGE_KEY, maskSecretsDemo ? '1' : '0');
    } catch {
      /* ignore quota / private mode */
    }
  }, [maskSecretsDemo]);

  const saveOllama = useMutation({
    mutationFn: () =>
      runtimeSettingsService.saveOllamaSettings({
        base_url: formData.ollama.url?.trim(),
        model: formData.ollama.model?.trim(),
      }),
    onSuccess: (data) => {
      setToast({
        kind: 'success',
        title: 'Ollama settings saved',
        subtitle: `Using ${data?.llm?.model} at ${data?.llm?.base_url} (in-memory until backend restart).`,
      });
      queryClient.invalidateQueries({ queryKey: ['runtime-settings'] });
      queryClient.invalidateQueries({ queryKey: ['agents-status'] });
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      queryClient.invalidateQueries({ queryKey: ['ollama-health'] });
      queryClient.invalidateQueries({ queryKey: ['ollama-tags'] });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Could not save Ollama settings',
        subtitle: err?.response?.data?.detail || err?.message || 'Unknown error',
      });
    },
  });

  const testDb2 = useMutation({
    mutationFn: (connectionString) => runtimeSettingsService.testDb2Connection(connectionString),
    onSuccess: () => {
      setToast({
        kind: 'success',
        title: 'Db2 connection OK',
        subtitle: 'The backend reached Db2 and ran SELECT 1 successfully.',
      });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Db2 connection test failed',
        subtitle: err?.response?.data?.detail || err?.message || 'Unknown error',
      });
    },
  });

  const saveDb2 = useMutation({
    mutationFn: () =>
      runtimeSettingsService.saveDb2Connection({
        connection_string: formData.vectorDb.connectionString.trim(),
        kb_table_prefix: formData.vectorDb.collection?.trim() || undefined,
        db2_schema: formData.vectorDb.schema?.trim() ?? '',
      }),
    onSuccess: (data) => {
      setToast({
        kind: 'success',
        title: 'Db2 connection saved',
        subtitle: data?.message || 'Knowledge base reloaded with this connection.',
      });
      queryClient.invalidateQueries({ queryKey: ['runtime-settings'] });
      queryClient.invalidateQueries({ queryKey: ['kb-status'] });
      queryClient.invalidateQueries({ queryKey: ['kb-documents'] });
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Could not save Db2 connection',
        subtitle: err?.response?.data?.detail || err?.message || 'Unknown error',
      });
    },
  });

  const clearDb2Runtime = useMutation({
    mutationFn: () => runtimeSettingsService.clearDb2Runtime(),
    onSuccess: (data) => {
      setToast({
        kind: 'success',
        title: 'Runtime Db2 override cleared',
        subtitle: data?.message || 'Using DEXTER_DB2_* from environment only.',
      });
      queryClient.invalidateQueries({ queryKey: ['runtime-settings'] });
      queryClient.invalidateQueries({ queryKey: ['kb-status'] });
      queryClient.invalidateQueries({ queryKey: ['kb-documents'] });
      queryClient.invalidateQueries({ queryKey: ['settings'] });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Could not clear Db2 override',
        subtitle: err?.response?.data?.detail || err?.message || 'Unknown error',
      });
    },
  });

  const testOllama = useMutation({
    mutationFn: () => runtimeSettingsService.ollamaHealth(formData.ollama.url?.trim()),
    onSuccess: (data) => {
      setToast({
        kind: 'success',
        title: 'Ollama responded',
        subtitle: `${data?.model_count ?? 0} model(s) reported at ${data?.base_url}`,
      });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Ollama check failed',
        subtitle: err?.response?.data?.detail || err?.message || 'Unknown error',
      });
    },
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

  const { data: ollamaTagData, refetch: refetchOllamaModels, isFetching: ollamaTagsLoading } = useQuery({
    queryKey: ['ollama-tags', formData.ollama.url],
    queryFn: () => runtimeSettingsService.listOllamaTags(formData.ollama.url?.trim()),
    enabled: selectedTab === 1 && Boolean(formData.ollama.url?.trim()),
    retry: false,
  });

  const ollamaModelOptions = useMemo(() => {
    const fromApi = ollamaTagData?.models || [];
    const cur = formData.ollama.model?.trim();
    const uniq = new Set(fromApi);
    if (cur) uniq.add(cur);
    return [...uniq];
  }, [ollamaTagData, formData.ollama.model]);

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
    if (provider === 'ollama') {
      testOllama.mutate();
      return;
    }
    if (provider === 'vectordb') {
      const cs = formData.vectorDb.connectionString?.trim();
      if (!cs) {
        setToast({
          kind: 'warning',
          title: 'Connection string required',
          subtitle: 'Paste an IBM Db2 CLI connection string, then try again.',
        });
        return;
      }
      testDb2.mutate(cs);
      return;
    }
    setToast({
      kind: 'info',
      title: 'Not wired yet',
      subtitle: `${provider} connectivity checks are not implemented in the backend.`,
    });
  };

  const handleSaveOllama = () => {
    saveOllama.mutate();
  };

  const teamMembers = [];

  const teamHeaders = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
    { key: 'role', header: 'Role' },
    { key: 'team', header: 'Team' },
  ];

  return (
    <div
      className={`settings-page${maskSecretsDemo ? ' settings-page--mask-secrets' : ''}`}
    >
      <div className="page-header">
        <div className="page-header__title">
          <SettingsIcon size={32} />
          <h1>Settings</h1>
        </div>
        <p className="page-header__description">
          Configure integrations, AI models, and organization preferences
        </p>
        <div className="page-header__presentation">
          <Toggle
            id="settings-presentation-mask"
            labelText="Presentation mode — mask secrets on screen (screen recording / demos)"
            toggled={maskSecretsDemo}
            onToggle={() => setMaskSecretsDemo((v) => !v)}
            size="sm"
          />
          {maskSecretsDemo && (
            <p className="cds--label-description page-header__presentation-hint">
              Obscures passwords, tokens, and Db2 connection strings in the UI. This only changes how they
              look—do not open DevTools → Application → Local Storage toward viewers while this page is open.
            </p>
          )}
        </div>
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
                            subtitle={
                              maskSecretsDemo
                                ? `Source: ${runtimeSettings.github.source}. A token is saved; the preview is hidden in presentation mode.`
                                : `Source: ${runtimeSettings.github.source}${
                                    runtimeSettings.runtime_overrides?.github_token
                                      ? ` (${runtimeSettings.runtime_overrides.github_token})`
                                      : ''
                                  }`
                            }
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
                        <div className="settings-mask-sensitive">
                          <TextInput
                            id="github-token"
                            labelText="GitHub Personal Access Token"
                            type="password"
                            placeholder="ghp_xxxxxxxxxxxx or github_pat_xxx"
                            helperText="Stored in backend memory only; cleared on restart. Generate at https://github.com/settings/tokens (scopes: repo, read:org)."
                            value={formData.github.token}
                            onChange={(e) => handleInputChange('github', 'token', e.target.value)}
                          />
                        </div>
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
                        <div className="settings-mask-sensitive">
                          <TextInput
                            id="gitlab-token"
                            labelText="GitLab Personal Access Token"
                            type="password"
                            placeholder="glpat-xxxxxxxxxxxx"
                            helperText="Required for GitLab integration"
                            value={formData.gitlab.token}
                            onChange={(e) => handleInputChange('gitlab', 'token', e.target.value)}
                          />
                        </div>
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
                    {runtimeSettings?.llm?.sources && (
                      <InlineNotification
                        kind="info"
                        title="Effective values"
                        subtitle={`Model from ${runtimeSettings.llm.sources.model}; base URL from ${runtimeSettings.llm.sources.base_url}. Saving below updates runtime overrides only.`}
                        lowContrast
                        hideCloseButton
                      />
                    )}
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
                          {ollamaModelOptions.length === 0 ? (
                            <SelectItem value={formData.ollama.model || ''} text={formData.ollama.model || 'Type or refresh model list'} />
                          ) : (
                            ollamaModelOptions.map((m) => (
                              <SelectItem key={m} value={m} text={m} />
                            ))
                          )}
                        </Select>
                        <p className="cds--label-description" style={{ marginTop: '0.5rem' }}>
                          Open the AI Configuration tab to load tags from your Ollama daemon, or type a model name manually
                          (e.g. qwen2.5-coder:14b).
                        </p>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
                          <Button
                            kind="tertiary"
                            size="sm"
                            onClick={() => handleTestConnection('ollama')}
                            disabled={testOllama.isPending || !formData.ollama.url?.trim()}
                          >
                            {testOllama.isPending ? <InlineLoading description="Testing..." /> : 'Test connection'}
                          </Button>
                          <Button kind="tertiary" size="sm" onClick={() => refetchOllamaModels()} disabled={ollamaTagsLoading}>
                            {ollamaTagsLoading ? <InlineLoading description="Loading models..." /> : 'Refresh model list'}
                          </Button>
                          <Button
                            kind="primary"
                            size="sm"
                            renderIcon={Save}
                            onClick={handleSaveOllama}
                            disabled={saveOllama.isPending || !formData.ollama.model?.trim()}
                          >
                            {saveOllama.isPending ? <InlineLoading description="Saving..." /> : 'Save Ollama settings'}
                          </Button>
                        </div>
                      </FormGroup>
                    </Form>

                    <h3>IBM watsonx.ai Configuration</h3>
                    <Form>
                      <FormGroup legendText="">
                        <div className="settings-mask-sensitive">
                          <TextInput
                            id="watsonx-api-key"
                            labelText="API Key"
                            type="password"
                            placeholder="Enter watsonx API key"
                            value={formData.watsonx.apiKey}
                            onChange={(e) => handleInputChange('watsonx', 'apiKey', e.target.value)}
                          />
                        </div>
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
                    <p className="cds--helper-text" style={{ marginBottom: '1rem', maxWidth: '52rem' }}>
                      <strong>Database name</strong> is the Db2 <em>catalog</em> (<code>DATABASE=…</code> in the CLI string,
                      or <code>DEXTER_DB2_DATABASE</code> in <code>.env</code>). <strong>Schema</strong> and{' '}
                      <strong>table</strong> are separate: a typical KB target is <code>DEXTER.DEXTER_KB</code> (schema{' '}
                      <code>DEXTER</code>, table <code>DEXTER_KB</code>). Dexter stores <em>all uploads</em> as rows in that
                      one vector table (document ids in metadata)—it does not create a new table per file.
                    </p>
                    <p className="cds--helper-text" style={{ marginBottom: '1rem', maxWidth: '52rem' }}>
                      <code>DEXTER_VECTOR_DB_TYPE</code> selects Db2 vs in-memory. Use the fields below for an optional{' '}
                      <strong>runtime</strong> CLI string (saved in <code>backend/data/runtime_overrides.json</code>).
                    </p>
                    {runtimeSettings?.vector_db?.db2_kb_qualified_table && (
                      <p className="cds--label-01" style={{ marginBottom: '1rem', maxWidth: '52rem' }}>
                        Resolved vector KB: catalog <code>{runtimeSettings.vector_db.db2_database_catalog}</code>
                        {' — table '}
                        <code>{runtimeSettings.vector_db.db2_kb_qualified_table}</code>
                      </p>
                    )}
                    {runtimeSettings?.vector_db?.db2_runtime_connection && (
                      <InlineNotification
                        kind="info"
                        title="Runtime Db2 connection is active"
                        subtitle="The knowledge base uses the saved CLI string in addition to DEXTER_DB2_* defaults where needed."
                        lowContrast
                        hideCloseButton
                      />
                    )}
                    <Form>
                      <FormGroup legendText="">
                        <Select
                          id="vector-db-type"
                          labelText="Vector Database Type (read-only — set in backend .env)"
                          value={formData.vectorDb.type}
                          onChange={(e) => handleInputChange('vectorDb', 'type', e.target.value)}
                          disabled
                        >
                          <SelectItem value="db2" text="IBM Db2 Vector (langchain-db2)" />
                          <SelectItem value="inmemory" text="In-memory (development only)" />
                        </Select>
                        <div className="settings-mask-sensitive">
                          <TextArea
                            id="vector-db-connection"
                            labelText="Db2 CLI connection string"
                            helperText={
                              maskSecretsDemo
                                ? 'Input is visually masked. Use KEY=VAL pairs separated by semicolons.'
                                : 'Example: DATABASE=MYDB;HOSTNAME=localhost;PORT=50000;PROTOCOL=TCPIP;UID=user;PWD=secret; — optional Security=SSL and SSLServerCertificate=/path/file.arm'
                            }
                            rows={4}
                            value={formData.vectorDb.connectionString}
                            onChange={(e) => handleInputChange('vectorDb', 'connectionString', e.target.value)}
                          />
                        </div>
                        <TextInput
                          id="vector-db-collection"
                          labelText="KB table stem"
                          helperText="If the value ends with _KB (e.g. DEXTER_KB), that is the full table name. Otherwise _KB is appended (DEXTER → DEXTER_KB)."
                          placeholder="DEXTER"
                          value={formData.vectorDb.collection}
                          onChange={(e) => handleInputChange('vectorDb', 'collection', e.target.value)}
                        />
                        <TextInput
                          id="vector-db-schema"
                          labelText="Db2 schema (optional runtime override)"
                          helperText="Leave empty to use DEXTER_DB2_SCHEMA from the backend environment."
                          placeholder=""
                          value={formData.vectorDb.schema}
                          onChange={(e) => handleInputChange('vectorDb', 'schema', e.target.value)}
                        />
                        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', marginTop: '1rem' }}>
                          <Button
                            kind="tertiary"
                            size="sm"
                            onClick={() => handleTestConnection('vectordb')}
                            disabled={testDb2.isPending}
                          >
                            {testDb2.isPending ? <InlineLoading description="Testing..." /> : 'Test connection'}
                          </Button>
                          <Button
                            kind="primary"
                            size="sm"
                            renderIcon={Save}
                            onClick={() => saveDb2.mutate()}
                            disabled={
                              saveDb2.isPending || !formData.vectorDb.connectionString?.trim()
                            }
                          >
                            {saveDb2.isPending ? (
                              <InlineLoading description="Saving..." />
                            ) : (
                              'Save & apply to backend'
                            )}
                          </Button>
                          <Button
                            kind="danger--tertiary"
                            size="sm"
                            renderIcon={TrashCan}
                            onClick={() => clearDb2Runtime.mutate()}
                            disabled={
                              clearDb2Runtime.isPending ||
                              !runtimeSettings?.vector_db?.db2_runtime_connection
                            }
                          >
                            {clearDb2Runtime.isPending ? (
                              <InlineLoading description="Clearing..." />
                            ) : (
                              'Clear runtime override'
                            )}
                          </Button>
                        </div>
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
                    <h3>Team members</h3>
                    <p className="cds--helper-text">No team directory API is configured yet.</p>
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
