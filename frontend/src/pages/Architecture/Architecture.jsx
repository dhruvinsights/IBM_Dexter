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
  TableToolbar,
  TableToolbarContent,
  TableToolbarSearch,
  Tag,
  ProgressBar,
  Accordion,
  AccordionItem,
} from '@carbon/react';
import {
  ReferenceArchitecture,
  CheckmarkFilled,
  WarningAltFilled,
  ErrorFilled,
  Renew,
  CloudApp,
} from '@carbon/icons-react';
import { GaugeChart } from '@carbon/charts-react';
import '@carbon/charts-react/styles.css';
import { architectureService } from '../../services/platformService';
import { useCarbonChartTheme } from '../../hooks/useCarbonChartTheme';
import './Architecture.scss';

const Architecture = () => {
  const chartTheme = useCarbonChartTheme();
  const { data: architectureData, isLoading } = useQuery({
    queryKey: ['architecture'],
    queryFn: architectureService.getSummary,
  });

  if (isLoading) {
    return <ArchitectureSkeleton />;
  }

  const {
    complianceScore = 0,
    services = [],
    violations = [],
    modernizationOpportunities = [],
  } = architectureData || {};

  const violationsHeaders = [
    { key: 'service', header: 'Service' },
    { key: 'type', header: 'Violation Type' },
    { key: 'severity', header: 'Severity' },
    { key: 'impact', header: 'Impact' },
    { key: 'recommendation', header: 'Recommendation' },
  ];

  const violationsRows = violations.map((violation) => ({
    id: violation.id,
    service: violation.service,
    type: violation.type,
    severity: violation.severity,
    impact: violation.impact,
    recommendation: violation.recommendation,
  }));

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

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckmarkFilled size={20} className="status-icon status-icon--success" />;
      case 'warning':
        return <WarningAltFilled size={20} className="status-icon status-icon--warning" />;
      case 'degraded':
        return <ErrorFilled size={20} className="status-icon status-icon--error" />;
      default:
        return null;
    }
  };

  const getComplexityTag = (complexity) => {
    const complexityMap = {
      high: { type: 'red', label: 'High Complexity' },
      medium: { type: 'purple', label: 'Medium Complexity' },
      low: { type: 'green', label: 'Low Complexity' },
    };
    const config = complexityMap[complexity] || complexityMap.medium;
    return <Tag type={config.type}>{config.label}</Tag>;
  };

  const gaugeData = [
    {
      group: 'value',
      value: complianceScore,
    },
  ];

  const gaugeOptions = {
    title: 'Architecture Compliance Score',
    resizable: true,
    height: '250px',
    gauge: {
      type: 'semi',
      status: complianceScore >= 90 ? 'success' : complianceScore >= 70 ? 'warning' : 'danger',
    },
    color: {
      scale: {
        value: complianceScore >= 90 ? '#24a148' : complianceScore >= 70 ? '#f1c21b' : '#da1e28',
      },
    },
    theme: chartTheme,
  };

  return (
    <div className="architecture-page">
      <div className="page-header">
        <div className="page-header__title">
          <ReferenceArchitecture size={32} />
          <h1>Architecture</h1>
        </div>
        <p className="page-header__description">
          Monitor architecture compliance, service dependencies, and modernization opportunities
        </p>
      </div>

      <Grid className="architecture-grid" narrow>
        {/* Hero Section - Compliance Score */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="compliance-score-tile">
            <GaugeChart data={gaugeData} options={gaugeOptions} />
            <div className="compliance-score-details">
              <p className="compliance-score-label">Overall Architecture Health</p>
              <div className="compliance-metrics">
                <div className="metric">
                  <span className="metric-value">{services.length}</span>
                  <span className="metric-label">Services</span>
                </div>
                <div className="metric">
                  <span className="metric-value">{violations.length}</span>
                  <span className="metric-label">Violations</span>
                </div>
                <div className="metric">
                  <span className="metric-value">{modernizationOpportunities.length}</span>
                  <span className="metric-label">Opportunities</span>
                </div>
              </div>
            </div>
          </Tile>
        </Column>

        {/* Microservice Health Grid */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <CloudApp size={24} />
                <h2>Microservice Health</h2>
              </div>
            </div>
            <div className="service-grid">
              {services.map((service) => (
                <div key={service.id} className="service-card">
                  <div className="service-card__header">
                    <div className="service-card__title">
                      {getStatusIcon(service.status)}
                      <h3>{service.name}</h3>
                    </div>
                    <Tag type="outline" size="sm">
                      {service.language}
                    </Tag>
                  </div>
                  <div className="service-card__body">
                    <div className="service-metric">
                      <span className="service-metric__label">API Compliance</span>
                      <div className="service-metric__value">
                        <ProgressBar
                          value={service.apiCompliance}
                          max={100}
                          label={`${service.apiCompliance}%`}
                          size="sm"
                        />
                      </div>
                    </div>
                    <div className="service-metric">
                      <span className="service-metric__label">Health Score</span>
                      <div className="service-metric__value">
                        <ProgressBar
                          value={service.health}
                          max={100}
                          label={`${service.health}%`}
                          size="sm"
                        />
                      </div>
                    </div>
                    <div className="service-dependencies">
                      <span className="service-dependencies__label">Dependencies:</span>
                      <div className="service-dependencies__list">
                        {service.dependencies.map((dep, idx) => (
                          <Tag key={idx} type="cool-gray" size="sm">
                            {dep}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="service-card__footer">
                    <span className="service-version">v{service.version}</span>
                  </div>
                </div>
              ))}
            </div>
          </Tile>
        </Column>

        {/* Architecture Violations Table */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <WarningAltFilled size={24} />
                <h2>Architecture Violations</h2>
              </div>
            </div>
            <DataTable rows={violationsRows} headers={violationsHeaders}>
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
                      <TableToolbarSearch persistent placeholder="Search violations..." />
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
          </Tile>
        </Column>

        {/* Modernization Opportunities */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <Renew size={24} />
                <h2>Modernization Opportunities</h2>
              </div>
            </div>
            <Accordion>
              {modernizationOpportunities.map((opportunity) => (
                <AccordionItem
                  key={opportunity.id}
                  title={
                    <div className="modernization-title">
                      <span>{opportunity.title}</span>
                      {getComplexityTag(opportunity.complexity)}
                    </div>
                  }
                >
                  <div className="modernization-content">
                    <div className="modernization-section">
                      <h4>Legacy Pattern</h4>
                      <p>{opportunity.legacyPattern}</p>
                    </div>
                    <div className="modernization-section">
                      <h4>Modern Pattern</h4>
                      <p>{opportunity.modernPattern}</p>
                    </div>
                    <div className="modernization-section">
                      <h4>Impact</h4>
                      <p>{opportunity.impact}</p>
                    </div>
                    <div className="modernization-section">
                      <h4>Estimated Effort</h4>
                      <p>{opportunity.estimatedEffort}</p>
                    </div>
                    <div className="modernization-section">
                      <h4>Affected Services</h4>
                      <div className="service-tags">
                        {opportunity.services.map((service, idx) => (
                          <Tag key={idx} type="blue">
                            {service}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  </div>
                </AccordionItem>
              ))}
            </Accordion>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

const ArchitectureSkeleton = () => (
  <div className="architecture-page">
    <div className="page-header">
      <SkeletonText heading width="30%" />
      <SkeletonText width="50%" />
    </div>
    <Grid narrow>
      <Column lg={16} md={8} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '300px' }} />
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

export default Architecture;

// Made with Bob