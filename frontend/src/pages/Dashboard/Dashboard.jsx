import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonText,
  SkeletonPlaceholder,
  DataTable,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Tag,
  ProgressBar,
  InlineNotification,
} from '@carbon/react';
import {
  ArrowUp,
  ArrowDown,
  CheckmarkFilled,
  WarningAltFilled,
  ErrorFilled,
  Security,
  ReferenceArchitecture,
} from '@carbon/icons-react';
import { LineChart, DonutChart, SimpleBarChart } from '@carbon/charts-react';
import '@carbon/charts-react/styles.css';
import { platformService } from '../../services/platformService';
import { collectFindingsFromReview, worstSeverity, buildLiveDashboard } from '../../utils/liveDashboard';
import { useCarbonChartTheme } from '../../hooks/useCarbonChartTheme';
import './Dashboard.scss';

const Dashboard = () => {
  const chartTheme = useCarbonChartTheme();

  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => platformService.getDashboard(),
    retry: 1,
  });

  if (dashboardLoading) {
    return <DashboardSkeleton />;
  }

  const feedErrors = dashboardData?.dashboardFeedErrors;
  const baseline = buildLiveDashboard({});
  const kpis =
    Array.isArray(dashboardData?.kpis) && dashboardData.kpis.length > 0 ? dashboardData.kpis : baseline.kpis;
  const recentReviews = dashboardData?.recentReviews || [];
  const securityOverview = dashboardData?.securityOverview || {};
  const architecture = dashboardData?.architecture || {};

  // Chart data
  const emptySnapshot = baseline;
  const reviewTrendsData =
    dashboardData?.reviewTrends?.length > 0 ? dashboardData.reviewTrends : emptySnapshot.reviewTrends;
  const productivityData =
    dashboardData?.productivityTrends?.length > 0
      ? dashboardData.productivityTrends
      : emptySnapshot.productivityTrends;
  const vulnSource =
    securityOverview.breakdown?.length > 0
      ? securityOverview.breakdown
      : emptySnapshot.securityOverview.breakdown;
  const vulnerabilityData = vulnSource.map((item) => ({
    group: item.label,
    value: item.value,
  }));
  const vulnTotal = vulnerabilityData.reduce((acc, row) => acc + (Number(row.value) || 0), 0);
  const reviewTrendsMax = reviewTrendsData.reduce(
    (m, row) => Math.max(m, Number(row.value) || 0),
    0
  );
  const productivityMax = productivityData.reduce(
    (m, row) => Math.max(m, Number(row.value) || 0),
    0
  );

  const securityScore = securityOverview.score ?? 100;
  const archScore = architecture.score ?? 100;
  const archPattern = architecture.patternCompliance ?? 100;
  const archService = architecture.serviceCoverage ?? 100;
  const archModern = architecture.modernization ?? 100;

  // Chart options
  const lineChartOptions = {
    title: 'Review Trends (Last 7 Days)',
    axes: {
      bottom: {
        title: 'Date',
        mapsTo: 'date',
        scaleType: 'labels',
      },
      left: {
        mapsTo: 'value',
        title: 'Reviews',
        scaleType: 'linear',
      },
    },
    height: '300px',
    theme: chartTheme,
  };

  const donutChartOptions = {
    title: 'Vulnerability Distribution',
    resizable: true,
    donut: {
      center: {
        label: 'Total',
      },
      alignment: 'center',
    },
    height: '300px',
    theme: chartTheme,
  };

  const barChartOptions = {
    title: 'Findings per day (last 7 days)',
    axes: {
      bottom: {
        title: 'Date',
        mapsTo: 'date',
        scaleType: 'labels',
      },
      left: {
        mapsTo: 'value',
        title: 'Findings',
        scaleType: 'linear',
      },
    },
    height: '300px',
    theme: chartTheme,
  };

  // DataTable headers
  const reviewTableHeaders = [
    { key: 'repository', header: 'Repository' },
    { key: 'title', header: 'PR Title' },
    { key: 'severity', header: 'Severity' },
    { key: 'status', header: 'Status' },
    { key: 'findings', header: 'Findings' },
  ];

  const reviewTableRows = recentReviews.map((review) => {
    const pr = review.pull_request || {};
    const repo = pr.repository || {};
    const findings = collectFindingsFromReview(review);
    const repoLabel = repo.full_name || repo.name || pr.repo || '—';
    return {
      id: String(review.id ?? review.pull_request_id ?? `${repoLabel}-${pr.title}`),
      repository: repoLabel,
      title: pr.title || '—',
      severity: worstSeverity(findings),
      status: (review.status || 'completed').toLowerCase(),
      findings: review.result?.findings_count ?? findings.length,
    };
  });

  const severityMax = Math.max(
    1,
    ...(vulnSource || []).map((item) => Number(item.value) || 0)
  );

  return (
    <div className="dashboard">
      <div className="dashboard-header dashboard-header--hero">
        <h1>Intelligence console</h1>
        <p className="dashboard-subtitle">
          Live signal from Dexter reviews, knowledge base activity, and delivery health — not slideware.
        </p>
      </div>

      {feedErrors?.length > 0 && (
        <InlineNotification
          kind="warning"
          title="Some dashboard data could not be loaded"
          subtitle={`${feedErrors.length} request(s) failed. Showing zeros where needed. ${feedErrors[0] || ''}`}
          lowContrast
          hideCloseButton
        />
      )}

      {/* KPI Cards Section */}
      <Grid narrow className="dashboard-kpis">
        {kpis.map((kpi) => (
          <Column key={kpi.key} sm={4} md={4} lg={3}>
            <Tile className={`kpi-card kpi-card--${kpi.key}`}>
              <div className="kpi-content">
                <div className="kpi-value">
                  {kpi.value === null || kpi.value === undefined ? '—' : String(kpi.value)}
                </div>
                <div className="kpi-label">{kpi.label}</div>
                <div
                  className={`kpi-delta ${
                    /^\s*\+/.test(kpi.delta) ? 'positive' : /^\s*[-–]/.test(kpi.delta) ? 'negative' : 'neutral'
                  }`}
                >
                  {/^\s*\+/.test(kpi.delta) ? (
                    <ArrowUp size={16} />
                  ) : /^\s*[-–]/.test(kpi.delta) ? (
                    <ArrowDown size={16} />
                  ) : null}
                  <span>{kpi.delta}</span>
                </div>
              </div>
            </Tile>
          </Column>
        ))}
      </Grid>

      {/* Charts Section */}
      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={8}>
          <Tile className="chart-tile chart-tile--line">
            {reviewTrendsMax === 0 ? (
              <div className="dashboard-chart-empty">
                No review runs in the last 7 days yet. Complete a PR analysis and data will appear here.
              </div>
            ) : (
              <LineChart data={reviewTrendsData} options={lineChartOptions} />
            )}
          </Tile>
        </Column>

        <Column sm={4} md={8} lg={8}>
          <Tile className="chart-tile chart-tile--donut">
            {vulnTotal === 0 ? (
              <div className="dashboard-chart-empty">
                No findings recorded yet — severity breakdown will show after Dexter reviews runs with findings.
              </div>
            ) : (
              <DonutChart data={vulnerabilityData} options={donutChartOptions} />
            )}
          </Tile>
        </Column>
      </Grid>

      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={16}>
          <Tile className="chart-tile chart-tile--bar">
            {productivityMax === 0 ? (
              <div className="dashboard-chart-empty">
                No findings logged per day in this window yet. Run analyses from Pull Requests to populate this chart.
              </div>
            ) : (
              <SimpleBarChart data={productivityData} options={barChartOptions} />
            )}
          </Tile>
        </Column>
      </Grid>

      {/* Recent Reviews Table */}
      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={16}>
          <Tile className="table-tile table-tile--accent">
            <h3 className="tile-heading">Recent Reviews</h3>
            <DataTable
              rows={reviewTableRows}
              headers={reviewTableHeaders}
              isSortable
            >
              {({
                rows,
                headers,
                getHeaderProps,
                getRowProps,
                getTableProps,
              }) => (
                <TableContainer>
                  <Table {...getTableProps()}>
                    <TableHead>
                      <TableRow>
                        {headers.map((header) => (
                          <TableHeader
                            key={header.key}
                            {...getHeaderProps({ header })}
                          >
                            {header.header}
                          </TableHeader>
                        ))}
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {rows.map((row) => (
                        <TableRow key={row.id} {...getRowProps({ row })}>
                          {row.cells.map((cell) => {
                            if (cell.info.header === 'severity') {
                              return (
                                <TableCell key={cell.id}>
                                  <SeverityTag severity={cell.value} />
                                </TableCell>
                              );
                            }
                            if (cell.info.header === 'status') {
                              return (
                                <TableCell key={cell.id}>
                                  <StatusTag status={cell.value} />
                                </TableCell>
                              );
                            }
                            return <TableCell key={cell.id}>{cell.value}</TableCell>;
                          })}
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </DataTable>
            {reviewTableRows.length === 0 && (
              <p className="dashboard-table-empty">
                No reviews in history yet. Open <strong>Pull Requests</strong> and run a live analysis — completed runs
                appear here (even when findings are <strong>0</strong>).
              </p>
            )}
          </Tile>
        </Column>
      </Grid>

      {/* Security & Architecture Panels */}
      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={8}>
          <Tile className="insight-tile security-tile insight-tile--security">
            <div className="tile-header">
              <Security size={24} className="tile-icon" />
              <h3 className="tile-heading">Security Overview</h3>
            </div>
            <div className="security-score">
              <div className="score-value">{securityScore}</div>
              <div className="score-label">Security Score</div>
            </div>
            <div className="security-breakdown">
              {vulnSource.map((item) => (
                <div key={item.label} className="security-item">
                  <div className="security-item-header">
                    <SeverityTag severity={item.label.toLowerCase()} />
                    <span className="security-count">{item.value}</span>
                  </div>
                  <ProgressBar
                    value={item.value}
                    max={severityMax}
                    size="sm"
                    className={`progress-${item.label.toLowerCase()}`}
                  />
                </div>
              ))}
            </div>
          </Tile>
        </Column>

        <Column sm={4} md={8} lg={8}>
          <Tile className="insight-tile architecture-tile insight-tile--architecture">
            <div className="tile-header">
              <ReferenceArchitecture size={24} className="tile-icon" />
              <h3 className="tile-heading">Architecture Insights</h3>
            </div>
            <div className="architecture-score">
              <div className="score-gauge">
                <svg viewBox="0 0 100 50" className="gauge-svg">
                  <path
                    d="M 10 50 A 40 40 0 0 1 90 50"
                    fill="none"
                    stroke="var(--cds-layer-accent-01)"
                    strokeWidth="8"
                  />
                  <path
                    d="M 10 50 A 40 40 0 0 1 90 50"
                    fill="none"
                    stroke="var(--cds-interactive-01)"
                    strokeWidth="8"
                    strokeDasharray={`${archScore * 1.26} 126`}
                  />
                </svg>
                <div className="gauge-value">{archScore}%</div>
              </div>
              <div className="score-label">Architecture Score</div>
            </div>
            <div className="architecture-metrics">
              <div className="metric-row">
                <span className="metric-label">Pattern Compliance</span>
                <span className="metric-value">{archPattern}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Service Coverage</span>
                <span className="metric-value">{archService}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Modernization</span>
                <span className="metric-value">{archModern}%</span>
              </div>
            </div>
            <div className="architecture-issues">
              <h4>Top Issues</h4>
              {(!architecture.issues || architecture.issues.length === 0) && (
                <p className="dashboard-table-empty" style={{ borderTop: 'none', paddingTop: 0 }}>
                  No architecture findings yet — run Dexter reviews on PRs that touch structural code.
                </p>
              )}
              {architecture.issues?.map((issue, idx) => (
                <div key={idx} className="issue-item">
                  <SeverityTag severity={issue.severity} />
                  <span className="issue-title">{issue.title}</span>
                </div>
              ))}
            </div>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

// Helper Components
const SeverityTag = ({ severity }) => {
  const severityConfig = {
    critical: { type: 'red', icon: ErrorFilled },
    high: { type: 'magenta', icon: WarningAltFilled },
    medium: { type: 'yellow', icon: WarningAltFilled },
    low: { type: 'green', icon: CheckmarkFilled },
  };

  const config = severityConfig[severity] || severityConfig.low;
  const Icon = config.icon;

  return (
    <Tag type={config.type} size="sm" renderIcon={Icon}>
      {severity}
    </Tag>
  );
};

const StatusTag = ({ status }) => {
  const statusConfig = {
    completed: { type: 'green', icon: CheckmarkFilled },
    pending: { type: 'blue', icon: WarningAltFilled },
    in_review: { type: 'cyan', icon: WarningAltFilled },
    failed: { type: 'red', icon: ErrorFilled },
  };

  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <Tag type={config.type} size="sm" renderIcon={Icon}>
      {status.replace('_', ' ')}
    </Tag>
  );
};

const DashboardSkeleton = () => (
  <div className="dashboard">
    <div className="dashboard-header">
      <SkeletonText heading width="200px" />
      <SkeletonText width="400px" />
    </div>
    <Grid narrow className="dashboard-kpis">
      {[1, 2, 3, 4, 5].map((i) => (
        <Column key={i} sm={4} md={4} lg={3}>
          <Tile>
            <SkeletonPlaceholder style={{ height: '120px' }} />
          </Tile>
        </Column>
      ))}
    </Grid>
    <Grid narrow className="dashboard-section">
      <Column sm={4} md={8} lg={16}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '300px' }} />
        </Tile>
      </Column>
    </Grid>
  </div>
);

export default Dashboard;

// Made with Bob
