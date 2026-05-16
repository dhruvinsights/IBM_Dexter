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
import './Dashboard.scss';

const Dashboard = () => {
  const { data: dashboardData, isLoading: dashboardLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => platformService.getDashboard(),
  });

  const { data: reviews, isLoading: reviewsLoading } = useQuery({
    queryKey: ['reviews'],
    queryFn: () => platformService.getReviews(),
  });

  if (dashboardLoading || reviewsLoading) {
    return <DashboardSkeleton />;
  }

  const kpis = dashboardData?.kpis || [];
  const recentReviews = reviews?.slice(0, 5) || [];
  const securityOverview = dashboardData?.securityOverview || {};
  const architecture = dashboardData?.architecture || {};

  // Chart data
  const reviewTrendsData = dashboardData?.reviewTrends || [];
  const vulnerabilityData = securityOverview.breakdown?.map(item => ({
    group: item.label,
    value: item.value,
  })) || [];
  const productivityData = dashboardData?.productivityTrends || [];

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
    theme: 'g100',
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
    theme: 'g100',
  };

  const barChartOptions = {
    title: 'Team Productivity Velocity',
    axes: {
      bottom: {
        title: 'Date',
        mapsTo: 'date',
        scaleType: 'labels',
      },
      left: {
        mapsTo: 'value',
        title: 'Velocity Score',
        scaleType: 'linear',
      },
    },
    height: '300px',
    theme: 'g100',
  };

  // DataTable headers
  const reviewTableHeaders = [
    { key: 'repository', header: 'Repository' },
    { key: 'title', header: 'PR Title' },
    { key: 'severity', header: 'Severity' },
    { key: 'status', header: 'Status' },
    { key: 'findings', header: 'Findings' },
  ];

  const reviewTableRows = recentReviews.map((review) => ({
    id: review.id,
    repository: review.repository,
    title: review.title,
    severity: review.findings?.[0]?.severity || 'low',
    status: review.status,
    findings: review.findings?.length || 0,
  }));

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p className="dashboard-subtitle">
          Overview of your code review analytics and AI-powered insights
        </p>
      </div>

      {/* KPI Cards Section */}
      <Grid narrow className="dashboard-kpis">
        {kpis.map((kpi) => (
          <Column key={kpi.key} sm={4} md={4} lg={3}>
            <Tile className="kpi-card">
              <div className="kpi-content">
                <div className="kpi-value">{kpi.value}</div>
                <div className="kpi-label">{kpi.label}</div>
                <div className={`kpi-delta ${kpi.delta.includes('+') ? 'positive' : 'neutral'}`}>
                  {kpi.delta.includes('+') ? (
                    <ArrowUp size={16} />
                  ) : (
                    <ArrowDown size={16} />
                  )}
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
          <Tile className="chart-tile">
            <LineChart
              data={reviewTrendsData}
              options={lineChartOptions}
            />
          </Tile>
        </Column>

        <Column sm={4} md={8} lg={8}>
          <Tile className="chart-tile">
            <DonutChart
              data={vulnerabilityData}
              options={donutChartOptions}
            />
          </Tile>
        </Column>
      </Grid>

      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={16}>
          <Tile className="chart-tile">
            <SimpleBarChart
              data={productivityData}
              options={barChartOptions}
            />
          </Tile>
        </Column>
      </Grid>

      {/* Recent Reviews Table */}
      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={16}>
          <Tile className="table-tile">
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
          </Tile>
        </Column>
      </Grid>

      {/* Security & Architecture Panels */}
      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={8}>
          <Tile className="insight-tile security-tile">
            <div className="tile-header">
              <Security size={24} className="tile-icon" />
              <h3 className="tile-heading">Security Overview</h3>
            </div>
            <div className="security-score">
              <div className="score-value">{securityOverview.score}</div>
              <div className="score-label">Security Score</div>
            </div>
            <div className="security-breakdown">
              {securityOverview.breakdown?.map((item) => (
                <div key={item.label} className="security-item">
                  <div className="security-item-header">
                    <SeverityTag severity={item.label.toLowerCase()} />
                    <span className="security-count">{item.value}</span>
                  </div>
                  <ProgressBar
                    value={item.value}
                    max={50}
                    size="sm"
                    className={`progress-${item.label.toLowerCase()}`}
                  />
                </div>
              ))}
            </div>
          </Tile>
        </Column>

        <Column sm={4} md={8} lg={8}>
          <Tile className="insight-tile architecture-tile">
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
                    strokeDasharray={`${architecture.score * 1.26} 126`}
                  />
                </svg>
                <div className="gauge-value">{architecture.score}%</div>
              </div>
              <div className="score-label">Architecture Score</div>
            </div>
            <div className="architecture-metrics">
              <div className="metric-row">
                <span className="metric-label">Pattern Compliance</span>
                <span className="metric-value">{architecture.patternCompliance}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Service Coverage</span>
                <span className="metric-value">{architecture.serviceCoverage}%</span>
              </div>
              <div className="metric-row">
                <span className="metric-label">Modernization</span>
                <span className="metric-value">{architecture.modernization}%</span>
              </div>
            </div>
            <div className="architecture-issues">
              <h4>Top Issues</h4>
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
