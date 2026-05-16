import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonText,
  SkeletonPlaceholder,
  Dropdown,
  Tag,
} from '@carbon/react';
import {
  Analytics,
  Trophy,
  ChartLineSmooth,
  UserMultiple,
  Ai,
} from '@carbon/icons-react';
import { LineChart, AreaChart, SimpleBarChart, DonutChart } from '@carbon/charts-react';
import '@carbon/charts-react/styles.css';
import { teamAnalyticsService } from '../../services/platformService';
import './TeamAnalytics.scss';

const TeamAnalytics = () => {
  const [selectedTeam, setSelectedTeam] = useState('All Teams');

  const { data: analyticsData, isLoading } = useQuery({
    queryKey: ['teamAnalytics'],
    queryFn: teamAnalyticsService.getSummary,
  });

  if (isLoading) {
    return <TeamAnalyticsSkeleton />;
  }

  const {
    teams = [],
    metrics = {},
    velocityTrends = [],
    qualityTrends = [],
    topContributors = [],
    teamComparison = [],
    aiAdoption = {},
  } = analyticsData || {};

  const currentMetrics = metrics[selectedTeam] || metrics['All Teams'] || {};

  const teamItems = teams.map((team) => ({
    id: team,
    text: team,
  }));

  // Velocity trends chart data
  const velocityChartData = velocityTrends.flatMap((trend) =>
    Object.keys(trend)
      .filter((key) => key !== 'week')
      .map((team) => ({
        group: team,
        week: trend.week,
        value: trend[team],
      }))
  );

  const velocityChartOptions = {
    title: 'Review Velocity Trends',
    axes: {
      bottom: {
        title: 'Week',
        mapsTo: 'week',
        scaleType: 'labels',
      },
      left: {
        title: 'PRs Reviewed',
        mapsTo: 'value',
        scaleType: 'linear',
      },
    },
    curve: 'curveMonotoneX',
    height: '300px',
  };

  // Quality trends chart data
  const qualityChartData = qualityTrends.map((trend) => ({
    group: 'Quality Score',
    week: trend.week,
    value: trend.score,
  }));

  const qualityChartOptions = {
    title: 'Quality Score Trends',
    axes: {
      bottom: {
        title: 'Week',
        mapsTo: 'week',
        scaleType: 'labels',
      },
      left: {
        title: 'Score',
        mapsTo: 'value',
        scaleType: 'linear',
      },
    },
    curve: 'curveMonotoneX',
    height: '300px',
  };

  // Team comparison chart data
  const comparisonChartData = teamComparison.flatMap((team) => [
    { group: 'Velocity', team: team.team, value: team.velocity },
    { group: 'Quality', team: team.team, value: team.quality },
    { group: 'AI Adoption', team: team.team, value: team.aiAdoption },
  ]);

  const comparisonChartOptions = {
    title: 'Team Comparison',
    axes: {
      bottom: {
        title: 'Team',
        mapsTo: 'team',
        scaleType: 'labels',
      },
      left: {
        title: 'Score',
        mapsTo: 'value',
        scaleType: 'linear',
      },
    },
    height: '300px',
  };

  // AI Adoption donut chart
  const aiAdoptionData = aiAdoption.breakdown || [];

  const aiAdoptionOptions = {
    title: 'AI vs Manual Reviews',
    resizable: true,
    donut: {
      center: {
        label: 'Total',
        number: aiAdoptionData.reduce((sum, item) => sum + item.value, 0),
      },
    },
    height: '300px',
  };

  return (
    <div className="team-analytics-page">
      <div className="page-header">
        <div className="page-header__title">
          <Analytics size={32} />
          <h1>Team Productivity Analytics</h1>
        </div>
        <p className="page-header__description">
          Track team performance, velocity, and AI adoption metrics
        </p>
      </div>

      <Grid className="team-analytics-grid" narrow>
        {/* Team Selector */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="selector-tile">
            <div className="team-selector">
              <label className="team-selector__label">Select Team</label>
              <Dropdown
                id="team-dropdown"
                titleText=""
                label="Select team"
                items={teamItems}
                selectedItem={teamItems.find((item) => item.text === selectedTeam)}
                onChange={({ selectedItem }) => setSelectedTeam(selectedItem.text)}
                size="lg"
              />
            </div>
          </Tile>
        </Column>

        {/* Productivity Metrics Grid */}
        <Column lg={3} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--velocity">
            <div className="metric-tile__icon">
              <ChartLineSmooth size={24} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{currentMetrics.reviewVelocity || 0}</span>
              <span className="metric-tile__label">PRs/Week</span>
            </div>
          </Tile>
        </Column>

        <Column lg={3} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--time">
            <div className="metric-tile__icon">
              <Analytics size={24} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{currentMetrics.avgReviewTime || '0m'}</span>
              <span className="metric-tile__label">Avg Review Time</span>
            </div>
          </Tile>
        </Column>

        <Column lg={3} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--resolution">
            <div className="metric-tile__icon">
              <Trophy size={24} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{currentMetrics.issueResolutionRate || 0}%</span>
              <span className="metric-tile__label">Resolution Rate</span>
            </div>
          </Tile>
        </Column>

        <Column lg={3} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--quality">
            <div className="metric-tile__icon">
              <Trophy size={24} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{currentMetrics.qualityScore || 0}%</span>
              <span className="metric-tile__label">Quality Score</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--ai">
            <div className="metric-tile__icon">
              <Ai size={24} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{currentMetrics.aiAdoptionRate || 0}%</span>
              <span className="metric-tile__label">AI Adoption</span>
            </div>
          </Tile>
        </Column>

        {/* Charts Row 1 */}
        <Column lg={10} md={6} sm={4}>
          <Tile className="chart-tile">
            <LineChart data={velocityChartData} options={velocityChartOptions} />
          </Tile>
        </Column>

        <Column lg={6} md={2} sm={4}>
          <Tile className="chart-tile">
            <AreaChart data={qualityChartData} options={qualityChartOptions} />
          </Tile>
        </Column>

        {/* Top Contributors Leaderboard */}
        <Column lg={8} md={4} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <Trophy size={24} />
                <h2>Top Contributors</h2>
              </div>
            </div>
            <div className="leaderboard">
              {topContributors.map((contributor, index) => (
                <div key={contributor.id} className="leaderboard-item">
                  <div className="leaderboard-item__rank">
                    <span className={`rank rank--${index + 1}`}>#{index + 1}</span>
                  </div>
                  <div className="leaderboard-item__info">
                    <div className="contributor-name">
                      <UserMultiple size={20} />
                      <span>{contributor.name}</span>
                    </div>
                    <div className="contributor-team">
                      <Tag type="cool-gray" size="sm">
                        {contributor.team}
                      </Tag>
                    </div>
                  </div>
                  <div className="leaderboard-item__stats">
                    <div className="stat">
                      <span className="stat__value">{contributor.prsReviewed}</span>
                      <span className="stat__label">PRs</span>
                    </div>
                    <div className="stat">
                      <span className="stat__value">{contributor.issuesFound}</span>
                      <span className="stat__label">Issues</span>
                    </div>
                    <div className="stat">
                      <span className="stat__value">{contributor.qualityScore}%</span>
                      <span className="stat__label">Quality</span>
                    </div>
                  </div>
                  <div className="leaderboard-item__badges">
                    {contributor.badges.map((badge, idx) => (
                      <Tag key={idx} type="blue" size="sm">
                        {badge}
                      </Tag>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </Tile>
        </Column>

        {/* Team Comparison and AI Adoption */}
        <Column lg={8} md={4} sm={4}>
          <Grid narrow>
            <Column lg={16} md={8} sm={4}>
              <Tile className="chart-tile">
                <SimpleBarChart data={comparisonChartData} options={comparisonChartOptions} />
              </Tile>
            </Column>
            <Column lg={16} md={8} sm={4}>
              <Tile className="chart-tile">
                <DonutChart data={aiAdoptionData} options={aiAdoptionOptions} />
                <div className="ai-adoption-stats">
                  <div className="ai-stat">
                    <span className="ai-stat__label">Suggestions Accepted</span>
                    <span className="ai-stat__value">{aiAdoption.suggestionsAccepted || 0}%</span>
                  </div>
                  <div className="ai-stat">
                    <span className="ai-stat__label">Time Saved</span>
                    <span className="ai-stat__value">{aiAdoption.timeSavedHours || 0}h</span>
                  </div>
                </div>
              </Tile>
            </Column>
          </Grid>
        </Column>
      </Grid>
    </div>
  );
};

const TeamAnalyticsSkeleton = () => (
  <div className="team-analytics-page">
    <div className="page-header">
      <SkeletonText heading width="30%" />
      <SkeletonText width="50%" />
    </div>
    <Grid narrow>
      <Column lg={16} md={8} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '60px' }} />
        </Tile>
      </Column>
      <Column lg={4} md={2} sm={2}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '100px' }} />
        </Tile>
      </Column>
      <Column lg={4} md={2} sm={2}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '100px' }} />
        </Tile>
      </Column>
      <Column lg={4} md={2} sm={2}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '100px' }} />
        </Tile>
      </Column>
      <Column lg={4} md={2} sm={2}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '100px' }} />
        </Tile>
      </Column>
      <Column lg={16} md={8} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '400px' }} />
        </Tile>
      </Column>
    </Grid>
  </div>
);

export default TeamAnalytics;

// Made with Bob