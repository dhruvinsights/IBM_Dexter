import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonText,
  SkeletonPlaceholder,
} from '@carbon/react';
import {
  ArrowUp,
  ArrowDown,
  CheckmarkFilled,
  WarningAltFilled,
  ErrorFilled,
} from '@carbon/icons-react';
import { reviewsAPI, repositoriesAPI } from '../../services/api';
import './Dashboard.scss';

const Dashboard = () => {
  const { data: reviews, isLoading: reviewsLoading } = useQuery({
    queryKey: ['reviews'],
    queryFn: () => reviewsAPI.getAll().then(res => res.data),
  });

  const { data: repositories, isLoading: reposLoading } = useQuery({
    queryKey: ['repositories'],
    queryFn: () => repositoriesAPI.getAll().then(res => res.data),
  });

  if (reviewsLoading || reposLoading) {
    return <DashboardSkeleton />;
  }

  const totalReviews = reviews?.length || 0;
  const totalRepos = repositories?.length || 0;
  const criticalIssues = 12;
  const resolvedIssues = 45;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your code review analytics and insights</p>
      </div>

      <Grid narrow>
        <Column sm={4} md={4} lg={4}>
          <Tile className="metrics-card gradient-card gradient-blue">
            <div className="metric-value">{totalReviews}</div>
            <div className="metric-label">Total Reviews</div>
            <div className="metric-change positive">
              <ArrowUp size={16} />
              <span>12% from last week</span>
            </div>
          </Tile>
        </Column>

        <Column sm={4} md={4} lg={4}>
          <Tile className="metrics-card gradient-card gradient-purple">
            <div className="metric-value">{totalRepos}</div>
            <div className="metric-label">Active Repositories</div>
            <div className="metric-change positive">
              <ArrowUp size={16} />
              <span>3 new this month</span>
            </div>
          </Tile>
        </Column>

        <Column sm={4} md={4} lg={4}>
          <Tile className="metrics-card gradient-card gradient-teal">
            <div className="metric-value">{criticalIssues}</div>
            <div className="metric-label">Critical Issues</div>
            <div className="metric-change negative">
              <ArrowDown size={16} />
              <span>5 resolved today</span>
            </div>
          </Tile>
        </Column>

        <Column sm={4} md={4} lg={4}>
          <Tile className="metrics-card gradient-card gradient-cyan">
            <div className="metric-value">{resolvedIssues}</div>
            <div className="metric-label">Resolved This Week</div>
            <div className="metric-change positive">
              <ArrowUp size={16} />
              <span>18% improvement</span>
            </div>
          </Tile>
        </Column>
      </Grid>

      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={8}>
          <Tile className="review-summary-tile">
            <h3>Recent Reviews</h3>
            <div className="review-list">
              {reviews?.slice(0, 5).map((review, index) => (
                <div key={index} className="review-item">
                  <div className="review-info">
                    <h4>Pull Request #{review.pull_request_id}</h4>
                    <p className="review-status">
                      <span className={`status-badge ${review.status}`}>
                        {review.status === 'completed' && <CheckmarkFilled size={16} />}
                        {review.status === 'pending' && <WarningAltFilled size={16} />}
                        {review.status === 'failed' && <ErrorFilled size={16} />}
                        {review.status}
                      </span>
                    </p>
                  </div>
                  <div className="review-findings">
                    {review.findings?.length || 0} findings
                  </div>
                </div>
              ))}
            </div>
          </Tile>
        </Column>

        <Column sm={4} md={8} lg={8}>
          <Tile className="security-tile">
            <h3>Security Overview</h3>
            <div className="security-stats">
              <div className="security-stat">
                <span className="status-badge critical">
                  <ErrorFilled size={16} />
                  Critical
                </span>
                <span className="stat-value">3</span>
              </div>
              <div className="security-stat">
                <span className="status-badge high">
                  <WarningAltFilled size={16} />
                  High
                </span>
                <span className="stat-value">8</span>
              </div>
              <div className="security-stat">
                <span className="status-badge medium">
                  <WarningAltFilled size={16} />
                  Medium
                </span>
                <span className="stat-value">15</span>
              </div>
              <div className="security-stat">
                <span className="status-badge low">
                  <CheckmarkFilled size={16} />
                  Low
                </span>
                <span className="stat-value">24</span>
              </div>
            </div>
          </Tile>
        </Column>
      </Grid>

      <Grid narrow className="dashboard-section">
        <Column sm={4} md={8} lg={16}>
          <Tile className="architecture-tile">
            <h3>Architecture Insights</h3>
            <div className="architecture-stats">
              <div className="arch-stat">
                <div className="arch-label">Code Quality Score</div>
                <div className="arch-value">87%</div>
                <div className="arch-bar">
                  <div className="arch-bar-fill" style={{ width: '87%' }}></div>
                </div>
              </div>
              <div className="arch-stat">
                <div className="arch-label">Test Coverage</div>
                <div className="arch-value">72%</div>
                <div className="arch-bar">
                  <div className="arch-bar-fill" style={{ width: '72%' }}></div>
                </div>
              </div>
              <div className="arch-stat">
                <div className="arch-label">Documentation</div>
                <div className="arch-value">65%</div>
                <div className="arch-bar">
                  <div className="arch-bar-fill" style={{ width: '65%' }}></div>
                </div>
              </div>
            </div>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

const DashboardSkeleton = () => (
  <div className="dashboard">
    <div className="page-header">
      <SkeletonText heading />
      <SkeletonText />
    </div>
    <Grid narrow>
      {[1, 2, 3, 4].map((i) => (
        <Column key={i} sm={4} md={4} lg={4}>
          <Tile>
            <SkeletonPlaceholder style={{ height: '120px' }} />
          </Tile>
        </Column>
      ))}
    </Grid>
  </div>
);

export default Dashboard;

// Made with Bob
