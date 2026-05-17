/** Dashboard metrics from live API data only (no faker). */

export function collectFindingsFromReview(review) {
  const agentResults = review?.result?.agent_results || {};
  const findings = [];
  for (const agent of Object.values(agentResults)) {
    if (!agent || typeof agent !== 'object') continue;
    for (const f of agent.findings || []) {
      if (f && typeof f === 'object') findings.push(f);
    }
  }
  return findings;
}

export function severityBucket(sev) {
  const s = String(sev || 'low').toLowerCase();
  if (s.includes('critical') || s === 'crit') return 'critical';
  if (s.includes('high')) return 'high';
  if (s.includes('medium') || s === 'med') return 'medium';
  if (s.includes('low')) return 'low';
  return 'low';
}

const SEVERITY_RANK = { critical: 0, high: 1, medium: 2, low: 3 };

export function worstSeverity(findings) {
  if (!findings?.length) return 'low';
  let worst = 'low';
  let rank = SEVERITY_RANK.low;
  for (const f of findings) {
    const b = severityBucket(f.severity);
    const r = SEVERITY_RANK[b] ?? SEVERITY_RANK.low;
    if (r < rank) {
      rank = r;
      worst = b;
    }
  }
  return worst;
}

function aggregateSeverityCounts(reviews) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const r of reviews) {
    for (const f of collectFindingsFromReview(r)) {
      const b = severityBucket(f.severity);
      counts[b] += 1;
    }
  }
  return counts;
}

export function securityScoreFromCounts(counts) {
  const total = counts.critical + counts.high + counts.medium + counts.low;
  if (total === 0) return 100;
  const penalty = counts.critical * 15 + counts.high * 8 + counts.medium * 3 + counts.low;
  return Math.max(0, Math.min(100, 100 - Math.round(penalty)));
}

function daysLast7() {
  const now = new Date();
  const days = [];
  for (let i = 6; i >= 0; i -= 1) {
    const d = new Date(now);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - i);
    days.push(d);
  }
  return days;
}

function dayKey(d) {
  return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
}

function reviewsLast7DaysTrends(reviews) {
  const days = daysLast7();
  return days.map((d) => {
    const label = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    const y = d.getFullYear();
    const m = d.getMonth();
    const day = d.getDate();
    const value = reviews.filter((r) => {
      if (!r.completed_at) return false;
      const cd = new Date(r.completed_at);
      return cd.getFullYear() === y && cd.getMonth() === m && cd.getDate() === day;
    }).length;
    return { group: 'Reviews', date: label, value };
  });
}

function findingsLast7DaysTrends(reviews) {
  const map = new Map();
  for (const r of reviews) {
    if (!r.completed_at) continue;
    const cd = new Date(r.completed_at);
    cd.setHours(0, 0, 0, 0);
    const k = dayKey(cd);
    const n = r.result?.findings_count ?? collectFindingsFromReview(r).length;
    map.set(k, (map.get(k) || 0) + n);
  }
  const days = daysLast7();
  return days.map((d) => {
    const label = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    const value = map.get(dayKey(d)) || 0;
    return { group: 'Findings', date: label, value };
  });
}

function architectureBlock(review) {
  const ar = review?.result?.agent_results || {};
  for (const [key, val] of Object.entries(ar)) {
    if (!val || typeof val !== 'object') continue;
    if (key.includes('architecture') || val.category === 'architecture') {
      return val;
    }
  }
  return null;
}

function buildArchitectureInsights(reviews) {
  const issues = [];
  for (const r of reviews) {
    const arch = architectureBlock(r);
    if (!arch) continue;
    for (const f of arch.findings || []) {
      if (!f || typeof f !== 'object') continue;
      const title = f.message || f.title || f.file || 'Architecture finding';
      issues.push({
        title,
        severity: severityBucket(f.severity),
      });
    }
  }
  const top = issues.slice(0, 5);
  const archFindingCount = issues.length;
  const base = archFindingCount === 0 ? 100 : Math.max(40, 100 - Math.min(60, archFindingCount * 4));
  return {
    score: base,
    patternCompliance: archFindingCount === 0 ? 100 : Math.max(50, 100 - archFindingCount * 3),
    serviceCoverage: archFindingCount === 0 ? 100 : Math.max(55, 95 - archFindingCount * 2),
    modernization: archFindingCount === 0 ? 100 : Math.max(45, 90 - archFindingCount * 5),
    issues: top.length > 0 ? top : [],
  };
}

export function buildLiveDashboard({ reviews = [], repositories = [], pullRequests = [], kbStatus = null }) {
  const reviewList = Array.isArray(reviews) ? reviews : [];
  const repoList = Array.isArray(repositories) ? repositories : [];
  const prList = Array.isArray(pullRequests) ? pullRequests : [];

  const sevCounts = aggregateSeverityCounts(reviewList);
  const totalFindings =
    sevCounts.critical + sevCounts.high + sevCounts.medium + sevCounts.low;

  const openPrCount = prList.filter(
    (pr) => String(pr.state || pr.status || '').toLowerCase() === 'open'
  ).length;

  const kbChunks = kbStatus && typeof kbStatus.chunk_count === 'number' ? kbStatus.chunk_count : 0;
  const kbDocs = kbStatus && typeof kbStatus.document_count === 'number' ? kbStatus.document_count : 0;

  const kpis = [
    {
      key: 'totalReviews',
      label: 'Total reviews',
      value: reviewList.length,
      delta: 'AI runs recorded',
    },
    {
      key: 'repos',
      label: 'Repositories',
      value: repoList.length,
      delta: 'Registered in Dexter',
    },
    {
      key: 'openPRs',
      label: 'Open pull requests',
      value: openPrCount,
      delta: 'In tracked list',
    },
    {
      key: 'kbChunks',
      label: 'KB chunks indexed',
      value: kbChunks,
      delta: kbDocs ? `${kbDocs} document(s)` : 'Knowledge base',
    },
    {
      key: 'securityScore',
      label: 'Security score (from findings)',
      value: securityScoreFromCounts(sevCounts),
      delta: totalFindings ? `${totalFindings} finding(s)` : 'No findings yet',
    },
  ];

  return {
    kpis,
    reviewTrends: reviewsLast7DaysTrends(reviewList),
    productivityTrends: findingsLast7DaysTrends(reviewList),
    securityOverview: {
      score: securityScoreFromCounts(sevCounts),
      breakdown: [
        { label: 'Critical', value: sevCounts.critical },
        { label: 'High', value: sevCounts.high },
        { label: 'Medium', value: sevCounts.medium },
        { label: 'Low', value: sevCounts.low },
      ],
    },
    architecture: buildArchitectureInsights(reviewList),
  };
}
