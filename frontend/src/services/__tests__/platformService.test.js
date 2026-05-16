import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as platformService from '../platformService';

describe('Platform Service', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getDashboardData', () => {
    it('returns dashboard data with KPIs', async () => {
      const data = await platformService.getDashboardData();
      
      expect(data).toHaveProperty('kpis');
      expect(data.kpis).toHaveProperty('totalPRs');
      expect(data.kpis).toHaveProperty('avgReviewTime');
      expect(data.kpis).toHaveProperty('codeQualityScore');
      expect(data.kpis).toHaveProperty('securityScore');
    });

    it('returns valid KPI values', async () => {
      const data = await platformService.getDashboardData();
      
      expect(typeof data.kpis.totalPRs).toBe('number');
      expect(typeof data.kpis.avgReviewTime).toBe('string');
      expect(typeof data.kpis.codeQualityScore).toBe('number');
      expect(typeof data.kpis.securityScore).toBe('number');
    });

    it('returns recent activity array', async () => {
      const data = await platformService.getDashboardData();
      
      expect(data).toHaveProperty('recentActivity');
      expect(Array.isArray(data.recentActivity)).toBe(true);
    });
  });

  describe('getPullRequests', () => {
    it('returns array of pull requests', async () => {
      const prs = await platformService.getPullRequests();
      
      expect(Array.isArray(prs)).toBe(true);
      expect(prs.length).toBeGreaterThan(0);
    });

    it('returns pull requests with required fields', async () => {
      const prs = await platformService.getPullRequests();
      const pr = prs[0];
      
      expect(pr).toHaveProperty('id');
      expect(pr).toHaveProperty('title');
      expect(pr).toHaveProperty('number');
      expect(pr).toHaveProperty('author');
      expect(pr).toHaveProperty('status');
      expect(pr).toHaveProperty('created_at');
    });

    it('filters pull requests by status', async () => {
      const openPRs = await platformService.getPullRequests({ status: 'open' });
      
      openPRs.forEach(pr => {
        expect(pr.status).toBe('open');
      });
    });
  });

  describe('getReviewDetail', () => {
    it('returns review detail for valid ID', async () => {
      const review = await platformService.getReviewDetail(1);
      
      expect(review).toHaveProperty('id');
      expect(review).toHaveProperty('pull_request');
      expect(review).toHaveProperty('status');
      expect(review).toHaveProperty('score');
    });

    it('returns review with findings', async () => {
      const review = await platformService.getReviewDetail(1);
      
      expect(review).toHaveProperty('findings');
      expect(Array.isArray(review.findings)).toBe(true);
    });

    it('returns review with metrics', async () => {
      const review = await platformService.getReviewDetail(1);
      
      expect(review).toHaveProperty('metrics');
      expect(review.metrics).toHaveProperty('complexity');
      expect(review.metrics).toHaveProperty('maintainability');
      expect(review.metrics).toHaveProperty('security');
    });
  });

  describe('getArchitectureInsights', () => {
    it('returns architecture insights', async () => {
      const insights = await platformService.getArchitectureInsights();
      
      expect(insights).toHaveProperty('patterns');
      expect(insights).toHaveProperty('dependencies');
      expect(insights).toHaveProperty('recommendations');
    });

    it('returns valid architecture patterns', async () => {
      const insights = await platformService.getArchitectureInsights();
      
      expect(Array.isArray(insights.patterns)).toBe(true);
      insights.patterns.forEach(pattern => {
        expect(pattern).toHaveProperty('name');
        expect(pattern).toHaveProperty('usage');
      });
    });
  });

  describe('getSecurityFindings', () => {
    it('returns security findings', async () => {
      const findings = await platformService.getSecurityFindings();
      
      expect(Array.isArray(findings)).toBe(true);
    });

    it('returns findings with severity levels', async () => {
      const findings = await platformService.getSecurityFindings();
      
      findings.forEach(finding => {
        expect(finding).toHaveProperty('severity');
        expect(['critical', 'high', 'medium', 'low']).toContain(finding.severity);
      });
    });

    it('returns findings with required fields', async () => {
      const findings = await platformService.getSecurityFindings();
      const finding = findings[0];
      
      expect(finding).toHaveProperty('id');
      expect(finding).toHaveProperty('title');
      expect(finding).toHaveProperty('description');
      expect(finding).toHaveProperty('severity');
      expect(finding).toHaveProperty('status');
    });
  });

  describe('getKnowledgeBase', () => {
    it('returns knowledge base entries', async () => {
      const kb = await platformService.getKnowledgeBase();
      
      expect(Array.isArray(kb)).toBe(true);
      expect(kb.length).toBeGreaterThan(0);
    });

    it('returns entries with required fields', async () => {
      const kb = await platformService.getKnowledgeBase();
      const entry = kb[0];
      
      expect(entry).toHaveProperty('id');
      expect(entry).toHaveProperty('title');
      expect(entry).toHaveProperty('content');
      expect(entry).toHaveProperty('category');
    });

    it('filters entries by category', async () => {
      const kb = await platformService.getKnowledgeBase({ category: 'best-practices' });
      
      kb.forEach(entry => {
        expect(entry.category).toBe('best-practices');
      });
    });
  });

  describe('getTeamAnalytics', () => {
    it('returns team analytics data', async () => {
      const analytics = await platformService.getTeamAnalytics();
      
      expect(analytics).toHaveProperty('members');
      expect(analytics).toHaveProperty('metrics');
      expect(analytics).toHaveProperty('trends');
    });

    it('returns valid team member data', async () => {
      const analytics = await platformService.getTeamAnalytics();
      
      expect(Array.isArray(analytics.members)).toBe(true);
      analytics.members.forEach(member => {
        expect(member).toHaveProperty('name');
        expect(member).toHaveProperty('contributions');
        expect(member).toHaveProperty('reviewCount');
      });
    });
  });

  describe('getAIAgents', () => {
    it('returns AI agents list', async () => {
      const agents = await platformService.getAIAgents();
      
      expect(Array.isArray(agents)).toBe(true);
      expect(agents.length).toBeGreaterThan(0);
    });

    it('returns agents with required fields', async () => {
      const agents = await platformService.getAIAgents();
      const agent = agents[0];
      
      expect(agent).toHaveProperty('id');
      expect(agent).toHaveProperty('name');
      expect(agent).toHaveProperty('type');
      expect(agent).toHaveProperty('status');
    });

    it('returns agents with capabilities', async () => {
      const agents = await platformService.getAIAgents();
      const agent = agents[0];
      
      expect(agent).toHaveProperty('capabilities');
      expect(Array.isArray(agent.capabilities)).toBe(true);
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      // Mock fetch to throw error
      const originalFetch = globalThis.fetch;
      globalThis.fetch = vi.fn().mockRejectedValue(new Error('Network error'));
      
      try {
        // Should fall back to mock data instead of throwing
        const data = await platformService.getDashboardData();
        expect(data).toBeDefined();
      } finally {
        globalThis.fetch = originalFetch;
      }
    });

    it('returns mock data when API is unavailable', async () => {
      const data = await platformService.getDashboardData();
      
      // Should return valid data structure even if API fails
      expect(data).toHaveProperty('kpis');
      expect(data.kpis).toBeDefined();
    });
  });

  describe('Data Validation', () => {
    it('returns consistent data types', async () => {
      const data = await platformService.getDashboardData();
      
      expect(typeof data.kpis.totalPRs).toBe('number');
      expect(typeof data.kpis.codeQualityScore).toBe('number');
      expect(data.kpis.codeQualityScore).toBeGreaterThanOrEqual(0);
      expect(data.kpis.codeQualityScore).toBeLessThanOrEqual(100);
    });

    it('returns valid date formats', async () => {
      const prs = await platformService.getPullRequests();
      const pr = prs[0];
      
      expect(pr.created_at).toBeDefined();
      expect(new Date(pr.created_at).toString()).not.toBe('Invalid Date');
    });
  });
});

// Made with Bob
