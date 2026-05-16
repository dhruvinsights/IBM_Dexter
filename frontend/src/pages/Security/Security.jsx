import { useState } from 'react';
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
  TableExpandHeader,
  TableExpandRow,
  TableExpandedRow,
  TableToolbar,
  TableToolbarContent,
  TableToolbarSearch,
  Tag,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
} from '@carbon/react';
import {
  Security as SecurityIcon,
  WarningAltFilled,
  ErrorFilled,
  CheckmarkFilled,
  Locked,
  Unlocked,
} from '@carbon/icons-react';
import { LineChart, DonutChart } from '@carbon/charts-react';
import '@carbon/charts-react/styles.css';
import { securityService } from '../../services/platformService';
import './Security.scss';

const Security = () => {
  const [selectedTab, setSelectedTab] = useState(0);

  const { data: securityData, isLoading } = useQuery({
    queryKey: ['security'],
    queryFn: securityService.getSummary,
  });

  if (isLoading) {
    return <SecuritySkeleton />;
  }

  const {
    overview = {},
    vulnerabilities = [],
    secrets = [],
    dependencyRisks = [],
    vulnerabilityTrends = [],
  } = securityData || {};

  const getSeverityTag = (severity) => {
    const severityMap = {
      critical: { type: 'red', label: 'Critical' },
      high: { type: 'magenta', label: 'High' },
      medium: { type: 'purple', label: 'Medium' },
      low: { type: 'blue', label: 'Low' },
    };
    const config = severityMap[severity] || severityMap.low;
    return <Tag type={config.type}>{config.label}</Tag>;
  };

  const getStatusTag = (status) => {
    const statusMap = {
      active: { type: 'red', label: 'Active', icon: Unlocked },
      revoked: { type: 'green', label: 'Revoked', icon: Locked },
      false_positive: { type: 'gray', label: 'False Positive', icon: CheckmarkFilled },
    };
    const config = statusMap[status] || statusMap.active;
    const Icon = config.icon;
    return (
      <Tag type={config.type} renderIcon={Icon}>
        {config.label}
      </Tag>
    );
  };

  const vulnerabilityHeaders = [
    { key: 'cveId', header: 'CVE ID' },
    { key: 'severity', header: 'Severity' },
    { key: 'package', header: 'Package' },
    { key: 'currentVersion', header: 'Current Version' },
    { key: 'fixedVersion', header: 'Fixed Version' },
    { key: 'cvssScore', header: 'CVSS Score' },
    { key: 'fixAvailable', header: 'Fix Available' },
  ];

  const vulnerabilityRows = vulnerabilities.map((vuln) => ({
    id: vuln.id,
    cveId: vuln.cveId,
    severity: vuln.severity,
    package: vuln.package,
    currentVersion: vuln.currentVersion,
    fixedVersion: vuln.fixedVersion,
    cvssScore: vuln.cvssScore,
    fixAvailable: vuln.fixAvailable ? 'Yes' : 'No',
    description: vuln.description,
    repository: vuln.repository,
  }));

  const secretHeaders = [
    { key: 'type', header: 'Type' },
    { key: 'location', header: 'Location' },
    { key: 'repository', header: 'Repository' },
    { key: 'severity', header: 'Severity' },
    { key: 'status', header: 'Status' },
  ];

  const secretRows = secrets.map((secret) => ({
    id: secret.id,
    type: secret.type,
    location: secret.location,
    repository: secret.repository,
    severity: secret.severity,
    status: secret.status,
  }));

  const dependencyHeaders = [
    { key: 'package', header: 'Package' },
    { key: 'currentVersion', header: 'Current Version' },
    { key: 'latestVersion', header: 'Latest Version' },
    { key: 'vulnerabilities', header: 'Known Vulnerabilities' },
    { key: 'riskScore', header: 'Risk Score' },
    { key: 'recommendation', header: 'Recommendation' },
  ];

  const dependencyRows = dependencyRisks.map((dep) => ({
    id: dep.id,
    package: dep.package,
    currentVersion: dep.currentVersion,
    latestVersion: dep.latestVersion,
    vulnerabilities: dep.knownVulnerabilities,
    riskScore: dep.riskScore.toFixed(1),
    recommendation: dep.recommendation,
  }));

  // Prepare chart data
  const trendChartData = vulnerabilityTrends.slice(-14).map((trend) => ({
    group: 'Critical',
    date: trend.date,
    value: trend.critical,
  })).concat(
    vulnerabilityTrends.slice(-14).map((trend) => ({
      group: 'High',
      date: trend.date,
      value: trend.high,
    }))
  ).concat(
    vulnerabilityTrends.slice(-14).map((trend) => ({
      group: 'Medium',
      date: trend.date,
      value: trend.medium,
    }))
  );

  const trendChartOptions = {
    title: 'Vulnerability Trends (Last 14 Days)',
    axes: {
      bottom: {
        title: 'Date',
        mapsTo: 'date',
        scaleType: 'labels',
      },
      left: {
        title: 'Count',
        mapsTo: 'value',
        scaleType: 'linear',
      },
    },
    curve: 'curveMonotoneX',
    height: '300px',
  };

  const severityDonutData = [
    { group: 'Critical', value: overview.critical || 0 },
    { group: 'High', value: overview.high || 0 },
    { group: 'Medium', value: overview.medium || 0 },
    { group: 'Low', value: overview.low || 0 },
  ];

  const severityDonutOptions = {
    title: 'Vulnerabilities by Severity',
    resizable: true,
    donut: {
      center: {
        label: 'Total',
        number: overview.totalVulnerabilities || 0,
      },
    },
    height: '300px',
  };

  return (
    <div className="security-page">
      <div className="page-header">
        <div className="page-header__title">
          <SecurityIcon size={32} />
          <h1>Security</h1>
        </div>
        <p className="page-header__description">
          Monitor vulnerabilities, secrets, and security risks across your codebase
        </p>
      </div>

      <Grid className="security-grid" narrow>
        {/* Security Dashboard Metrics */}
        <Column lg={4} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--critical">
            <div className="metric-tile__icon">
              <ErrorFilled size={32} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{overview.critical || 0}</span>
              <span className="metric-tile__label">Critical</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--high">
            <div className="metric-tile__icon">
              <WarningAltFilled size={32} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{overview.high || 0}</span>
              <span className="metric-tile__label">High</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--medium">
            <div className="metric-tile__icon">
              <WarningAltFilled size={32} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{overview.medium || 0}</span>
              <span className="metric-tile__label">Medium</span>
            </div>
          </Tile>
        </Column>

        <Column lg={4} md={2} sm={2}>
          <Tile className="metric-tile metric-tile--low">
            <div className="metric-tile__icon">
              <CheckmarkFilled size={32} />
            </div>
            <div className="metric-tile__content">
              <span className="metric-tile__value">{overview.low || 0}</span>
              <span className="metric-tile__label">Low</span>
            </div>
          </Tile>
        </Column>

        {/* Charts Row */}
        <Column lg={10} md={6} sm={4}>
          <Tile className="chart-tile">
            <LineChart data={trendChartData} options={trendChartOptions} />
          </Tile>
        </Column>

        <Column lg={6} md={2} sm={4}>
          <Tile className="chart-tile">
            <DonutChart data={severityDonutData} options={severityDonutOptions} />
          </Tile>
        </Column>

        {/* Tabbed Content */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="section-tile">
            <Tabs selectedIndex={selectedTab} onChange={({ selectedIndex }) => setSelectedTab(selectedIndex)}>
              <TabList aria-label="Security sections" contained>
                <Tab>Vulnerabilities ({vulnerabilities.length})</Tab>
                <Tab>Secret Scanning ({secrets.length})</Tab>
                <Tab>Dependency Risks ({dependencyRisks.length})</Tab>
              </TabList>
              <TabPanels>
                {/* Vulnerabilities Tab */}
                <TabPanel>
                  <DataTable rows={vulnerabilityRows} headers={vulnerabilityHeaders}>
                    {({
                      rows,
                      headers,
                      getHeaderProps,
                      getRowProps,
                      getExpandHeaderProps,
                      getTableProps,
                      getTableContainerProps,
                      getToolbarProps,
                    }) => (
                      <TableContainer {...getTableContainerProps()}>
                        <TableToolbar {...getToolbarProps()}>
                          <TableToolbarContent>
                            <TableToolbarSearch persistent placeholder="Search vulnerabilities..." />
                          </TableToolbarContent>
                        </TableToolbar>
                        <Table {...getTableProps()} size="lg" useZebraStyles>
                          <TableHead>
                            <TableRow>
                              <TableExpandHeader enableToggle {...getExpandHeaderProps()} />
                              {headers.map((header) => (
                                <TableHeader key={header.key} {...getHeaderProps({ header })}>
                                  {header.header}
                                </TableHeader>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {rows.map((row) => (
                              <>
                                <TableExpandRow key={row.id} {...getRowProps({ row })}>
                                  {row.cells.map((cell) => (
                                    <TableCell key={cell.id}>
                                      {cell.info.header === 'severity'
                                        ? getSeverityTag(cell.value)
                                        : cell.value}
                                    </TableCell>
                                  ))}
                                </TableExpandRow>
                                <TableExpandedRow colSpan={headers.length + 1}>
                                  <div className="expanded-row-content">
                                    <div className="expanded-row-section">
                                      <h4>Description</h4>
                                      <p>{vulnerabilityRows.find((v) => v.id === row.id)?.description}</p>
                                    </div>
                                    <div className="expanded-row-section">
                                      <h4>Repository</h4>
                                      <p>{vulnerabilityRows.find((v) => v.id === row.id)?.repository}</p>
                                    </div>
                                  </div>
                                </TableExpandedRow>
                              </>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </DataTable>
                </TabPanel>

                {/* Secret Scanning Tab */}
                <TabPanel>
                  <DataTable rows={secretRows} headers={secretHeaders}>
                    {({
                      rows,
                      headers,
                      getHeaderProps,
                      getRowProps,
                      getTableProps,
                      getTableContainerProps,
                      getToolbarProps,
                    }) => (
                      <TableContainer {...getTableContainerProps()}>
                        <TableToolbar {...getToolbarProps()}>
                          <TableToolbarContent>
                            <TableToolbarSearch persistent placeholder="Search secrets..." />
                          </TableToolbarContent>
                        </TableToolbar>
                        <Table {...getTableProps()} size="lg" useZebraStyles>
                          <TableHead>
                            <TableRow>
                              {headers.map((header) => (
                                <TableHeader key={header.key} {...getHeaderProps({ header })}>
                                  {header.header}
                                </TableHeader>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {rows.map((row) => (
                              <TableRow key={row.id} {...getRowProps({ row })}>
                                {row.cells.map((cell) => (
                                  <TableCell key={cell.id}>
                                    {cell.info.header === 'severity'
                                      ? getSeverityTag(cell.value)
                                      : cell.info.header === 'status'
                                      ? getStatusTag(cell.value)
                                      : cell.value}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </DataTable>
                </TabPanel>

                {/* Dependency Risks Tab */}
                <TabPanel>
                  <DataTable rows={dependencyRows} headers={dependencyHeaders}>
                    {({
                      rows,
                      headers,
                      getHeaderProps,
                      getRowProps,
                      getTableProps,
                      getTableContainerProps,
                      getToolbarProps,
                    }) => (
                      <TableContainer {...getTableContainerProps()}>
                        <TableToolbar {...getToolbarProps()}>
                          <TableToolbarContent>
                            <TableToolbarSearch persistent placeholder="Search dependencies..." />
                          </TableToolbarContent>
                        </TableToolbar>
                        <Table {...getTableProps()} size="lg" useZebraStyles>
                          <TableHead>
                            <TableRow>
                              {headers.map((header) => (
                                <TableHeader key={header.key} {...getHeaderProps({ header })}>
                                  {header.header}
                                </TableHeader>
                              ))}
                            </TableRow>
                          </TableHead>
                          <TableBody>
                            {rows.map((row) => (
                              <TableRow key={row.id} {...getRowProps({ row })}>
                                {row.cells.map((cell) => (
                                  <TableCell key={cell.id}>{cell.value}</TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </TableContainer>
                    )}
                  </DataTable>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

const SecuritySkeleton = () => (
  <div className="security-page">
    <div className="page-header">
      <SkeletonText heading width="30%" />
      <SkeletonText width="50%" />
    </div>
    <Grid narrow>
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

export default Security;

// Made with Bob