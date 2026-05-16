import axios from 'axios';
import { API_BASE_URL, ENABLE_MOCK_FALLBACK } from '../constants/appConstants';
import { mockPlatformData } from '../mocks/platformData';

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

// Only fall back to mock data when the backend is genuinely unreachable
// (network error, no response, or 5xx server crash). Real 2xx empty results
// and 4xx client errors propagate so the UI reflects real backend state.
const shouldUseFallback = (error) => {
  if (!ENABLE_MOCK_FALLBACK) return false;
  if (!error?.response) return true; // network error / CORS / DNS / refused
  const status = error.response.status;
  return status >= 500 && status < 600;
};

const simulateResponse = async (payload) =>
  new Promise((resolve) => {
    window.setTimeout(() => resolve(payload), 220);
  });

const withFallback = async (request, fallback) => {
  try {
    const response = await request();
    return response.data;
  } catch (error) {
    if (shouldUseFallback(error)) {
      // eslint-disable-next-line no-console
      console.warn('[platformService] falling back to mock data:', error?.config?.url, error?.response?.status, error?.message);
      return simulateResponse(fallback);
    }
    throw error;
  }
};

export const integrationService = {
  health: () =>
    withFallback(
      () => axios.get(API_BASE_URL.replace('/api/v1', '/health')),
      {
        status: 'degraded',
        backend: 'offline',
        fallbackMode: true,
      }
    ),
};

export const repositoryService = {
  list: () => withFallback(() => api.get('/repositories'), mockPlatformData.repositories),
  getById: (id) =>
    withFallback(
      () => api.get(`/repositories/${id}`),
      mockPlatformData.repositories.find((item) => item.id === id)
    ),
  create: async (payload) => {
    const response = await api.post('/repositories', payload);
    return response.data;
  },
  delete: async (id) => {
    await api.delete(`/repositories/${id}`);
    return { id };
  },
};

export const pullRequestService = {
  list: () => withFallback(() => api.get('/pull-requests'), mockPlatformData.pullRequests),
  getById: (id) =>
    withFallback(
      () => api.get(`/pull-requests/${id}`),
      mockPlatformData.pullRequests.find((item) => item.id === id)
    ),
  assignDexterReviewer: async (id) =>
    withFallback(
      () => api.post(`/pull-requests/${id}/review`, { reviewer: 'IBM Dexter' }),
      {
        pullRequestId: id,
        reviewer: 'IBM Dexter',
        status: 'assigned',
        mode: 'mock',
      }
    ),
};

export const reviewService = {
  list: () => withFallback(() => api.get('/reviews'), mockPlatformData.reviews),
  getById: (id) =>
    withFallback(
      () => api.get(`/reviews/${id}`),
      mockPlatformData.reviews.find(
        (item) => item.id === id || String(item.pull_request_id) === String(id)
      )
    ),
};


export const dashboardService = {
  getSummary: async () => {
    const [reviews, repositories] = await Promise.all([
      reviewService.list(),
      repositoryService.list(),
    ]);

    return {
      ...mockPlatformData.dashboard,
      recentReviews: reviews,
      repositories,
    };
  },
};

export const knowledgeBaseService = {
  getSummary: () => simulateResponse(mockPlatformData.knowledgeBase),
  getStatus: () => withFallback(() => api.get('/knowledge-base/status'), {
    backend: 'inmemory',
    vector_db_type: 'inmemory',
    embedding_model: 'nomic-embed-text',
    embeddings_healthy: false,
    document_count: 0,
    chunk_count: 0,
  }),
  listDocuments: () => withFallback(() => api.get('/knowledge-base/documents'), []),
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
  search: async (query, limit = 4) => {
    const response = await api.post('/knowledge-base/search', { query, limit });
    return response.data;
  },
  uploadDocument: async (file) => knowledgeBaseService.uploadFile(file),
};

export const liveReviewService = {
  analyzePullRequestUrl: async ({ url, useRag = true, ragQuery, ragLimit = 4 }) => {
    const response = await api.post('/pull-requests/analyze-url', {
      url,
      use_rag: useRag,
      rag_query: ragQuery,
      rag_limit: ragLimit,
    }, { timeout: 180000 });
    return response.data;
  },
};

export const agentsService = {
  list: () => withFallback(() => api.get('/agents'), []),
  status: () => withFallback(() => api.get('/agents/status'), {
    llm_provider: 'unknown',
    llm_model: 'unknown',
    agent_count: 0,
    agents: [],
  }),
};

export const runtimeSettingsService = {
  get: () => withFallback(() => api.get('/settings'), {
    llm: { provider: 'unknown', model: 'unknown', base_url: '' },
    vector_db: { type: 'unknown', backend: 'unknown' },
    github: { configured: false, source: 'none' },
    runtime_overrides: {},
  }),
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
};

export const analyticsService = {
  getSummary: () => simulateResponse(mockPlatformData.analytics),
};

export const architectureService = {
  getSummary: () => simulateResponse(mockPlatformData.architecture),
  getServices: () => simulateResponse(mockPlatformData.architecture.services),
  getViolations: () => simulateResponse(mockPlatformData.architecture.violations),
  getModernizationOpportunities: () =>
    simulateResponse(mockPlatformData.architecture.modernizationOpportunities),
};

export const securityService = {
  getSummary: () => simulateResponse(mockPlatformData.security),
  getVulnerabilities: () => simulateResponse(mockPlatformData.security.vulnerabilities),
  getSecrets: () => simulateResponse(mockPlatformData.security.secrets),
  getDependencyRisks: () => simulateResponse(mockPlatformData.security.dependencyRisks),
  getVulnerabilityTrends: () => simulateResponse(mockPlatformData.security.vulnerabilityTrends),
};

export const aiAgentsService = {
  getSummary: () => simulateResponse(mockPlatformData.aiAgents),
  getAgents: () => simulateResponse(mockPlatformData.aiAgents.agents),
  getActivityTimeline: () => simulateResponse(mockPlatformData.aiAgents.activityTimeline),
  getConfiguration: () => simulateResponse(mockPlatformData.aiAgents.configuration),
  updateConfiguration: async (config) =>
    simulateResponse({ ...mockPlatformData.aiAgents.configuration, ...config }),
};

export const teamAnalyticsService = {
  getSummary: () => simulateResponse(mockPlatformData.teamAnalytics),
  getTeamMetrics: (team) =>
    simulateResponse(
      mockPlatformData.teamAnalytics.metrics[team] || mockPlatformData.teamAnalytics.metrics['All Teams']
    ),
  getTopContributors: () => simulateResponse(mockPlatformData.teamAnalytics.topContributors),
  getVelocityTrends: () => simulateResponse(mockPlatformData.teamAnalytics.velocityTrends),
  getQualityTrends: () => simulateResponse(mockPlatformData.teamAnalytics.qualityTrends),
  getTeamComparison: () => simulateResponse(mockPlatformData.teamAnalytics.teamComparison),
  getAIAdoption: () => simulateResponse(mockPlatformData.teamAnalytics.aiAdoption),
};

export const settingsService = {
  getSettings: () => simulateResponse(mockPlatformData.settings),
  saveAccessToken: async ({ provider, token }) =>
    simulateResponse({
      provider,
      tokenStored: Boolean(token),
      status: 'connected',
      mode: 'demo-ready',
    }),
  updateIntegration: async (integration) =>
    simulateResponse({ ...integration, status: 'connected' }),
  testConnection: async (provider) =>
    simulateResponse({ provider, status: 'success', message: 'Connection successful' }),
};

// Unified platform service export
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

// Made with Bob
