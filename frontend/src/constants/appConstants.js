export const APP_NAME = 'IBM Dexter';
export const APP_SUBTITLE = 'AI Code Reviewer';
export const DEFAULT_ORGANIZATION = 'IBM Engineering';
export const DEFAULT_THEME = 'g100';

/** Browser path prefix for the main Carbon shell (landing stays at `/`). */
export const APP_SHELL_BASE = '/app';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Mock fallback only when the backend is unreachable (no response or 5xx).
// Default false so a running backend is always shown; set VITE_ENABLE_MOCK_FALLBACK=true for offline demos.
export const ENABLE_MOCK_FALLBACK =
  (import.meta.env.VITE_ENABLE_MOCK_FALLBACK || 'false') === 'true';

export const DEMO_FLAGS = {
  enableBackendStatus: true,
  enableKnowledgeBaseUpload: true,
  enableAgentTimeline: true,
  enableProductivityMetrics: true,
  enableDb2VectorContext: true,
};

export const NAVIGATION_ITEMS = [
  { key: 'dashboard', label: 'Dashboard', href: '/app/dashboard' },
  { key: 'pullRequests', label: 'Pull Requests', href: '/app/pull-requests' },
  { key: 'reviews', label: 'Reviews', href: '/app/reviews' },
  { key: 'repositories', label: 'Repositories', href: '/app/repositories' },
  { key: 'knowledgeBase', label: 'Knowledge Base', href: '/app/knowledge-base' },
  { key: 'aiAgents', label: 'AI Agents', href: '/app/ai-agents' },
  { key: 'architecture', label: 'Architecture', href: '/app/architecture' },
  { key: 'security', label: 'Security', href: '/app/security' },
  { key: 'analytics', label: 'Analytics', href: '/app/analytics' },
  { key: 'settings', label: 'Settings', href: '/app/settings' },
];

export const REVIEW_SEVERITIES = ['critical', 'high', 'medium', 'low'];

export const AGENT_TYPES = [
  'Security',
  'Architecture',
  'Compliance',
  'Modernization',
  'Performance',
];

export const TEAM_NAMES = ['Db2', 'OpenShift', 'API Platform'];

// Made with Bob
