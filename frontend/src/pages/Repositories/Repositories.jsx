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
} from '@carbon/react';
import { Add, LogoGithub, LogoGitlab, TrashCan } from '@carbon/icons-react';
import { repositoryService } from '../../services/platformService';
import './Repositories.scss';

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
  });

  const { data: repos = [], isLoading, error } = useQuery({
    queryKey: ['repositories-list'],
    queryFn: repositoryService.list,
  });

  const createMutation = useMutation({
    mutationFn: (payload) => repositoryService.create(payload),
    onSuccess: () => {
      setToast({ kind: 'success', title: 'Repository registered', subtitle: form.full_name });
      queryClient.invalidateQueries({ queryKey: ['repositories-list'] });
      setIsAddOpen(false);
      setForm({ name: '', full_name: '', url: '', owner_id: 1, platform: 'github' });
    },
    onError: (err) => {
      setToast({
        kind: 'error',
        title: 'Failed to create repository',
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
              </div>
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
