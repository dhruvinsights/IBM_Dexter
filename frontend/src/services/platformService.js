import axios from 'axios';
import { API_BASE_URL, ENABLE_MOCK_FALLBACK } from '../constants/appConstants';
import { buildLiveDashboard } from '../utils/liveDashboard';

const backendHealthUrl = () => {
  const trimmed = API_BASE_URL.replace(/\/$/, '');
  const withoutApi = trimmed.replace(/\/api\/v1$/i, '');
  return `${withoutApi}/health`;
};

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Bare axios instance for multipart: lets the browser set Content-Type with boundary.
const apiMultipart = axios.create({ baseURL: API_BASE_URL });

const attachAuth = (config) => {
  const token = localStorage.getItem('dexter-token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

api.interceptors.request.use(attachAuth, (error) => Promise.reject(error));
apiMultipart.interceptors.request.use(attachAuth, (error) => Promise.reject(error));

const shouldUseFallback = (error) => {
  if (!ENABLE_MOCK_FALLBACK) return false;
  if (!error?.response) return true;
  const status = error.response.status;
  return status >= 500 && status < 600;
};

const withFallback = async (request, fallback) => {
  try {
    const response = await request();
    return response.data;
  } catch (error) {
    if (shouldUseFallback(error)) {
      // eslint-disable-next-line no-console
      console.warn('[platformService] API unreachable, using empty fallback:', error?.config?.url, error?.message);
    }
    if (shouldUseFallback(error)) {
      return typeof fallback === 'function' ? fallback() : fallback;
    }
    throw error;
  }
};

const EMPTY_KB_STATUS = {
  backend: 'unknown',
  vector_db_type: 'unknown',
  embedding_model: '',
  embeddings: null,
  embeddings_healthy: false,
  document_count: 0,
  chunk_count: 0,
  vector_db_reachable: false,
  vector_db_error: null,
  vector_db_detail: '',
  vector_db_status: null,
};

const EMPTY_SECURITY_SUMMARY = {
  overview: {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    totalVulnerabilities: 0,
  },
  vulnerabilities: [],
  secrets: [],
  dependencyRisks: [],
  vulnerabilityTrends: [],
};

const EMPTY_ARCHITECTURE_SUMMARY = {
  complianceScore: 0,
  services: [],
  violations: [],
  modernizationOpportunities: [],
};

const EMPTY_ANALYTICS_SUMMARY = {
  summary: {
    reviewsCompleted: 0,
    avgReviewTime: '0m',
    codeQualityScore: '0%',
    issuesResolved: 0,
  },
  teamPerformance: [],
  aiAdoption: {
    coverage: 0,
    autoAssignedReviews: 0,
    commentAcceptanceRate: 0,
  },
};

const EMPTY_AI_AGENTS_SUMMARY = {
  agents: [],
  activityTimeline: [],
  configuration: {},
};

const EMPTY_TEAM_ANALYTICS = {
  teams: ['All Teams'],
  metrics: {
    'All Teams': {
      reviewVelocity: 0,
      avgReviewTime: '0m',
      issueResolutionRate: 0,
      qualityScore: 0,
      aiAdoptionRate: 0,
      codeQualityScore: 0,
      aiReviewCoverage: 0,
    },
  },
  velocityTrends: [],
  qualityTrends: [],
  topContributors: [],
  teamComparison: [],
  aiAdoption: { breakdown: [] },
};

export const integrationService = {
  health: () =>
    withFallback(
      () => axios.get(backendHealthUrl()),
      () => ({ status: 'degraded', backend: 'offline' })
    ),
};

export const repositoryService = {
  list: () => withFallback(() => api.get('/repositories'), () => []),
  getById: (id) =>
    withFallback(
      () => api.get(`/repositories/${id}`),
      () => null
    ),
  create: async (payload) => {
    const response = await api.post('/repositories', payload);
    return response.data;
  },
  update: async (id, payload) => {
    const response = await api.put(`/repositories/${id}`, payload);
    return response.data;
  },
  delete: async (id) => {
    await api.delete(`/repositories/${id}`);
    return { id };
  },
};

export const pullRequestService = {
  list: () => withFallback(() => api.get('/pull-requests'), () => []),
  getById: (id) =>
    withFallback(
      () => api.get(`/pull-requests/${id}`),
      () => null
    ),
  assignDexterReviewer: async (id) => {
    const response = await api.post(`/pull-requests/${id}/review`, { reviewer: 'IBM Dexter' });
    return response.data;
  },
};

export const reviewService = {
  list: () => withFallback(() => api.get('/reviews'), () => []),
  getById: (id) =>
    withFallback(
      () => api.get(`/reviews/${id}`),
      () => null
    ),
};

export const dashboardService = {
  getSummary: async () => {
    const settled = await Promise.allSettled([
      reviewService.list(),
      repositoryService.list(),
      pullRequestService.list(),
      knowledgeBaseService.getStatus(),
    ]);

    const pick = (index, fallback) => {
      const entry = settled[index];
      if (!entry || entry.status !== 'fulfilled') return fallback;
      return entry.value;
    };

    const reviews = pick(0, []);
    const repositories = pick(1, []);
    const pullRequests = pick(2, []);
    const kbStatus = pick(3, null);

    const live = buildLiveDashboard({
      reviews: Array.isArray(reviews) ? reviews : [],
      repositories: Array.isArray(repositories) ? repositories : [],
      pullRequests: Array.isArray(pullRequests) ? pullRequests : [],
      kbStatus,
    });

    const recentReviews = [...(Array.isArray(reviews) ? reviews : [])]
      .sort(
        (a, b) =>
          new Date(b.completed_at || 0).getTime() - new Date(a.completed_at || 0).getTime()
      )
      .slice(0, 5);

    const feedErrors = settled
      .map((s, i) => ({ s, i }))
      .filter(({ s }) => s.status === 'rejected')
      .map(({ s }) => (s.reason?.message ? String(s.reason.message) : 'A dashboard request failed'));

    return {
      ...live,
      recentReviews,
      ...(feedErrors.length ? { dashboardFeedErrors: feedErrors } : {}),
    };
  },
};

export const knowledgeBaseService = {
  getSummary: async () => {
    const [status, documents] = await Promise.all([
      knowledgeBaseService.getStatus(),
      knowledgeBaseService.listDocuments(),
    ]);
    const docs = Array.isArray(documents) ? documents : [];
    return {
      documents: docs,
      documentCount: docs.length,
      chunkCount: status?.chunk_count ?? 0,
      documentCountKb: status?.document_count ?? 0,
      embeddingModel: status?.embedding_model ?? '',
      backend: status?.backend ?? 'unknown',
    };
  },
  getStatus: () => withFallback(() => api.get('/knowledge-base/status'), () => ({ ...EMPTY_KB_STATUS })),
  listDocuments: () => withFallback(() => api.get('/knowledge-base/documents'), () => []),
  uploadFile: async (file, title, tags) => {
    const form = new FormData();
    form.append('file', file);
    if (title) form.append('title', title);
    if (tags) form.append('tags', tags);
    const response = await apiMultipart.post('/knowledge-base/upload', form);
    return response.data;
  },
  ingestText: async (payload) => {
    const response = await api.post('/knowledge-base/documents', payload);
    return response.data;
  },
  deleteDocument: async (id) => {
    await api.delete(`/knowledge-base/documents/${id}`);
    return { id };
  },
  getDocument: async (id) => {
    const response = await api.get(`/knowledge-base/documents/${encodeURIComponent(id)}`);
    return response.data;
  },
  search: async (query, limit = 4) => {
    const response = await api.post('/knowledge-base/search', { query, limit });
    return response.data;
  },
  uploadDocument: async (file) => knowledgeBaseService.uploadFile(file),
};

export const liveReviewService = {
  analyzePullRequestUrl: async ({
    url,
    useRag = true,
    ragQuery,
    ragLimit = 4,
    postReviewToGithub = false,
    requestSelfAsReviewer = false,
    inlineReviewComments = true,
  }) => {
    const response = await api.post(
      '/pull-requests/analyze-url',
      {
        url,
        use_rag: useRag,
        rag_query: ragQuery,
        rag_limit: ragLimit,
        post_review_to_github: postReviewToGithub,
        request_self_as_reviewer: requestSelfAsReviewer,
        inline_review_comments: inlineReviewComments,
      },
      { timeout: 180000 }
    );
    return response.data;
  },
};

export const agentsService = {
  list: () => withFallback(() => api.get('/agents'), () => []),
  status: () =>
    withFallback(() => api.get('/agents/status'), () => ({
      llm_provider: 'unknown',
      llm_model: 'unknown',
      llm_base_url: '',
      embedding_provider: '',
      embedding_model: '',
      embedding_dimension: 0,
      agent_count: 0,
      agents: [],
    })),
};

export const runtimeSettingsService = {
  get: () =>
    withFallback(() => api.get('/settings'), () => ({
      llm: { provider: 'unknown', model: 'unknown', base_url: '', sources: {} },
      vector_db: {
        type: 'unknown',
        backend: 'unknown',
        reachable: false,
        error: null,
        detail: '',
        configured_type: 'unknown',
        kb_store_backend: 'unknown',
        db2_runtime_connection: false,
        db2_kb_table_prefix: '',
        db2_database_catalog: '',
        db2_schema: '',
        db2_kb_table: '',
        db2_kb_qualified_table: '',
      },
      embeddings: {
        provider: '',
        model: '',
        dimension: 0,
        api_key_configured: false,
        base_url: '',
      },
      deployment: {
        hosted_ollama_notice_visible: false,
        hosted_ollama_notice: '',
        desktop_app_teaser: '',
      },
      github: { configured: false, source: 'none' },
      runtime_overrides: {},
    })),
  saveGithubToken: async (token, verify = true) => {
    const response = await api.post('/settings/github-token', { token, verify });
    return response.data;
  },
  clearGithubToken: async () => {
    await api.delete('/settings/github-token');
    return { ok: true };
  },
  verifyGithubToken: async () => {
    const response = await api.post('/settings/github/verify', {});
    return response.data;
  },
  listOllamaTags: async (baseUrl) => {
    const response = await api.get('/settings/ollama/tags', {
      params: baseUrl ? { base_url: baseUrl } : {},
    });
    return response.data;
  },
  ollamaHealth: async (baseUrl) => {
    const response = await api.get('/settings/ollama/health', {
      params: baseUrl ? { base_url: baseUrl } : {},
    });
    return response.data;
  },
  saveOllamaSettings: async (payload) => {
    const response = await api.post('/settings/ollama', payload);
    return response.data;
  },
  testDb2Connection: async (connectionString) => {
    const response = await api.post('/settings/db2/test', {
      connection_string: connectionString,
    });
    return response.data;
  },
  saveDb2Connection: async (payload) => {
    const response = await api.post('/settings/db2', payload);
    return response.data;
  },
  clearDb2Runtime: async () => {
    const response = await api.delete('/settings/db2');
    return response.data;
  },
};

export const analyticsService = {
  getSummary: async () => ({ ...EMPTY_ANALYTICS_SUMMARY }),
};

export const architectureService = {
  getSummary: async () => ({ ...EMPTY_ARCHITECTURE_SUMMARY }),
  getServices: async () => [],
  getViolations: async () => [],
  getModernizationOpportunities: async () => [],
};

export const securityService = {
  getSummary: async () => ({ ...EMPTY_SECURITY_SUMMARY }),
  getVulnerabilities: async () => [],
  getSecrets: async () => [],
  getDependencyRisks: async () => [],
  getVulnerabilityTrends: async () => [],
};

export const aiAgentsService = {
  getSummary: async () => ({ ...EMPTY_AI_AGENTS_SUMMARY }),
  getAgents: async () => [],
  getActivityTimeline: async () => [],
  getConfiguration: async () => ({}),
  updateConfiguration: async (config) => ({ ...config }),
};

export const teamAnalyticsService = {
  getSummary: async () => ({ ...EMPTY_TEAM_ANALYTICS }),
  getTeamMetrics: async () => EMPTY_TEAM_ANALYTICS.metrics['All Teams'],
  getTopContributors: async () => [],
  getVelocityTrends: async () => [],
  getQualityTrends: async () => [],
  getTeamComparison: async () => [],
  getAIAdoption: async () => EMPTY_TEAM_ANALYTICS.aiAdoption,
};

export const settingsService = {
  getSettings: async () => {
    let runtime;
    let ollamaOk = false;
    try {
      runtime = await runtimeSettingsService.get();
    } catch {
      runtime = null;
    }
    try {
      const health = await runtimeSettingsService.ollamaHealth();
      ollamaOk = Boolean(health?.ok);
    } catch {
      ollamaOk = false;
    }

    const ghConfigured = Boolean(runtime?.github?.configured);
    const integrations = [
      {
        name: 'GitHub',
        status: ghConfigured ? 'connected' : 'disconnected',
        detail: ghConfigured
          ? 'PAT configured for GitHub API access'
          : 'No token stored — public repositories only unless you add a PAT.',
      },
      {
        name: 'Ollama',
        status: ollamaOk ? 'connected' : 'disconnected',
        detail: ollamaOk
          ? `Reachable — chat model ${runtime?.llm?.model || 'unknown'}`
          : 'Dexter backend cannot reach Ollama at the configured URL.',
      },
      {
        name: 'Vector store',
        status: (() => {
          const t = runtime?.vector_db?.type;
          if (t === 'inmemory') return 'connected';
          if (t === 'db2') return runtime?.vector_db?.reachable ? 'connected' : 'disconnected';
          return 'standby';
        })(),
        detail:
          runtime?.vector_db?.detail ||
          `Backend: ${runtime?.vector_db?.backend || 'unknown'} (${runtime?.vector_db?.type || '—'})${
            runtime?.vector_db?.error ? ` — ${runtime.vector_db.error}` : ''
          }`,
      },
    ];

    return {
      organization: 'IBM Engineering',
      integrations,
    };
  },
  saveAccessToken: async ({ provider, token }) => {
    if (provider === 'github' && token) {
      return runtimeSettingsService.saveGithubToken(token, true);
    }
    return { provider, tokenStored: Boolean(token), status: 'pending' };
  },
  updateIntegration: async (integration) => integration,
  testConnection: async (provider) => ({ provider, status: 'unknown', message: 'Use provider-specific actions in Settings.' }),
};

export const platformService = {
  getDashboard: dashboardService.getSummary,
  getReviews: reviewService.list,
  getReviewById: reviewService.getById,
  getRepositories: repositoryService.list,
  getRepositoryById: repositoryService.getById,
  getPullRequests: pullRequestService.list,
  getPullRequestById: pullRequestService.getById,
  getKnowledgeBase: knowledgeBaseService.getSummary,
  getAnalytics: analyticsService.getSummary,
  getArchitecture: architectureService.getSummary,
  getSecurity: securityService.getSummary,
  getAIAgents: aiAgentsService.getSummary,
  getTeamAnalytics: teamAnalyticsService.getSummary,
  getSettings: settingsService.getSettings,
};

export default api;
