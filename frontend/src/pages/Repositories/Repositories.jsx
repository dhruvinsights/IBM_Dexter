import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonPlaceholder,
  Tag,
  Button,
  Modal,
  TextInput,
  Select,
  SelectItem,
  ToastNotification,
  InlineNotification,
  CodeSnippet,
  Toggle,
} from '@carbon/react';
import { Add, LogoGithub, LogoGitlab, TrashCan } from '@carbon/icons-react';
import { repositoryService } from '../../services/platformService';
import { API_BASE_URL } from '../../constants/appConstants';
import './Repositories.scss';

const WEBHOOK_URL = `${API_BASE_URL}/webhooks/github`;

const Repositories = () => {
  const queryClient = useQueryClient();
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const [form, setForm] = useState({
    name: '',
    full_name: '',
    url: '',
    owner_id: 1,
    platform: 'github',
    auto_review_enabled: true,
  });

  const defaultForm = () => ({
    name: '',
    full_name: '',
    url: '',
    owner_id: 1,
    platform: 'github',
    auto_review_enabled: true,
  });

  const { data: repos = [], isLoading, error } = useQuery({
    queryKey: ['repositories-list'],
    queryFn: repositoryService.list,
  });

  const createMutation = useMutation({
    mutationFn: (payload) => repositoryService.create(payload),
    onSuccess: (data) => {
      const hint = data?.webhook_setup?.webhook_url;
      setToast({
        kind: 'success',
        title: 'Repository registered',
        subtitle: hint
          ? `${data.full_name} — webhook: ${hint}`
          : `${data.full_name}. Point GitHub to ${WEBHOOK_URL} (see Repositories page).`,
      });
      queryClient.invalidateQueries({ queryKey: ['repositories-list'] });
      setIsAddOpen(false);
      setForm(defaultForm());
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Failed to create repository',
        subtitle: err?.response?.data?.detail?.toString?.() || err.message,
      });
    },
  });

  const toggleAutoMutation = useMutation({
    mutationFn: ({ id, auto_review_enabled }) => repositoryService.update(id, { auto_review_enabled }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['repositories-list'] });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Could not update auto-review',
        subtitle: err?.response?.data?.detail?.toString?.() || err.message,
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => repositoryService.delete(id),
    onSuccess: () => {
      setToast({ kind: 'success', title: 'Repository removed', subtitle: '' });
      queryClient.invalidateQueries({ queryKey: ['repositories-list'] });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Delete failed',
        subtitle: err?.response?.data?.detail?.toString?.() || err.message,
      });
    },
  });

  const inferFromUrl = (url) => {
    const m = url.match(/github\.com[/:]([\w.-]+)\/([\w.-]+?)(?:\.git)?$/i);
    if (m) {
      setForm((prev) => ({
        ...prev,
        url,
        platform: 'github',
        full_name: `${m[1]}/${m[2]}`,
        name: m[2],
      }));
      return;
    }
    setForm((prev) => ({ ...prev, url }));
  };

  return (
    <div className="repositories-page">
      <div className="page-header">
        <div>
          <h1>Repositories</h1>
          <p className="page-subtitle">
            Register source repositories so Dexter can run reviews against their pull requests.
            With <strong>auto-review</strong> enabled (GitHub), configure a repository webhook to{' '}
            <code>{WEBHOOK_URL}</code> using the same secret as <code>DEXTER_GITHUB_WEBHOOK_SECRET</code>.
          </p>
        </div>
        <Button kind="primary" renderIcon={Add} onClick={() => setIsAddOpen(true)}>
          Add repository
        </Button>
      </div>

      {isLoading && <SkeletonPlaceholder style={{ height: 200 }} />}
      {error && (
        <InlineNotification
          kind="error"
          title="Backend error"
          subtitle={error?.response?.data?.detail || error.message}
          hideCloseButton
          lowContrast
        />
      )}

      {!isLoading && repos.length === 0 && (
        <Tile className="repos-empty">
          <LogoGithub size={48} />
          <h3>No repositories registered yet</h3>
          <p>Click "Add repository" to point Dexter at your first repo, or just paste a public PR URL on the Pull Requests page.</p>
        </Tile>
      )}

      <Grid narrow>
        {repos.map((repo) => (
          <Column lg={8} md={4} sm={4} key={repo.id}>
            <Tile className="repo-card">
              <div className="repo-card__header">
                <div className="repo-card__icon">
                  {repo.platform === 'gitlab' ? <LogoGitlab size={20} /> : <LogoGithub size={20} />}
                </div>
                <div>
                  <h3>{repo.full_name || repo.name}</h3>
                  <a href={repo.url} target="_blank" rel="noreferrer">{repo.url}</a>
                </div>
                <Button
                  kind="danger--ghost"
                  size="sm"
                  renderIcon={TrashCan}
                  onClick={() => deleteMutation.mutate(repo.id)}
                  disabled={deleteMutation.isPending}
                  hasIconOnly
                  iconDescription="Remove repository"
                />
              </div>
              <div className="repo-card__tags">
                <Tag type={repo.is_active ? 'green' : 'cool-gray'} size="sm">
                  {repo.is_active ? 'Active' : 'Paused'}
                </Tag>
                <Tag type="blue" size="sm">{repo.platform}</Tag>
                {repo.platform === 'github' && (
                  <Tag type={repo.auto_review_enabled !== false ? 'teal' : 'cool-gray'} size="sm">
                    {repo.auto_review_enabled !== false ? 'Auto-review on' : 'Auto-review off'}
                  </Tag>
                )}
              </div>
              {repo.platform === 'github' && (
                <>
                  <Toggle
                    id={`auto-${repo.id}`}
                    size="sm"
                    labelText="Auto-review new/updated PRs via webhook"
                    toggled={repo.auto_review_enabled !== false}
                    disabled={toggleAutoMutation.isPending}
                    onToggle={() => {
                      const on = repo.auto_review_enabled !== false;
                      toggleAutoMutation.mutate({ id: repo.id, auto_review_enabled: !on });
                    }}
                    style={{ marginTop: '0.75rem' }}
                  />
                  <p style={{ margin: '0.5rem 0 0', fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
                    Webhook URL (Payload URL in GitHub):
                  </p>
                  <CodeSnippet type="single">{WEBHOOK_URL}</CodeSnippet>
                </>
              )}
            </Tile>
          </Column>
        ))}
      </Grid>

      <Modal
        open={isAddOpen}
        onRequestClose={() => setIsAddOpen(false)}
        modalHeading="Register a repository"
        primaryButtonText={createMutation.isPending ? 'Registering...' : 'Register'}
        secondaryButtonText="Cancel"
        primaryButtonDisabled={
          createMutation.isPending || !form.full_name.trim() || !form.url.trim() || !form.name.trim()
        }
        onRequestSubmit={() => createMutation.mutate(form)}
      >
        <p style={{ marginBottom: '1rem' }}>
          Paste the clone URL (or GitHub web URL) — name &amp; full_name auto-fill.
        </p>
        <TextInput
          id="repo-url"
          labelText="URL"
          placeholder="https://github.com/owner/repo"
          value={form.url}
          onChange={(e) => inferFromUrl(e.target.value)}
        />
        <TextInput
          id="repo-full-name"
          labelText="Full name"
          placeholder="owner/repo"
          value={form.full_name}
          onChange={(e) => setForm((prev) => ({ ...prev, full_name: e.target.value }))}
        />
        <TextInput
          id="repo-name"
          labelText="Short name"
          placeholder="repo"
          value={form.name}
          onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
        />
        <Select
          id="repo-platform"
          labelText="Platform"
          value={form.platform}
          onChange={(e) => setForm((prev) => ({ ...prev, platform: e.target.value }))}
        >
          <SelectItem value="github" text="GitHub" />
          <SelectItem value="gitlab" text="GitLab" />
        </Select>
        {form.platform === 'github' && (
          <Toggle
            id="repo-auto"
            labelText="Enable automatic PR review when GitHub sends pull_request webhooks"
            toggled={form.auto_review_enabled}
            onToggle={() => setForm((prev) => ({ ...prev, auto_review_enabled: !prev.auto_review_enabled }))}
            style={{ marginTop: '1rem' }}
          />
        )}
      </Modal>

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

export default Repositories;

// Made with Bob
