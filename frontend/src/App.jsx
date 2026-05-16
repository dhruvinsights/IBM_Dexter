import { BrowserRouter, Navigate, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard/Dashboard';
import PullRequests from './pages/PullRequests/PullRequests';
import Reviews from './pages/Reviews/Reviews';
import ReviewDetail from './pages/ReviewDetail/ReviewDetail';
import Repositories from './pages/Repositories/Repositories';
import Architecture from './pages/Architecture/Architecture';
import Security from './pages/Security/Security';
import KnowledgeBase from './pages/KnowledgeBase/KnowledgeBase';
import TeamAnalytics from './pages/TeamAnalytics/TeamAnalytics';
import AIAgents from './pages/AIAgents/AIAgents';
import Settings from './pages/Settings/Settings';
import './styles/App.scss';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Dashboard />} />
            <Route path="pull-requests" element={<PullRequests />} />
            <Route path="reviews" element={<Reviews />} />
            <Route path="reviews/:id" element={<ReviewDetail />} />
            <Route path="repositories" element={<Repositories />} />
            <Route path="architecture" element={<Architecture />} />
            <Route path="security" element={<Security />} />
            <Route path="knowledge-base" element={<KnowledgeBase />} />
            <Route path="analytics" element={<TeamAnalytics />} />
            <Route path="team-insights" element={<TeamAnalytics />} />
            <Route path="ai-agents" element={<AIAgents />} />
            <Route path="settings" element={<Settings />} />
            {/* Redirects for legacy nav items */}
            <Route path="productivity" element={<Navigate to="/analytics" replace />} />
            <Route path="integrations" element={<Navigate to="/settings" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;

// Made with Bob
