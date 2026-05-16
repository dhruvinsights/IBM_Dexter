import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  Grid,
  Column,
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
  TableBatchActions,
  TableBatchAction,
  TableSelectAll,
  TableSelectRow,
  Button,
  Dropdown,
  Tag,
  Pagination,
  SkeletonText,
  SkeletonPlaceholder,
  Modal,
  TextInput,
  Toggle,
  InlineLoading,
  InlineNotification,
  CodeSnippet,
  Accordion,
  AccordionItem,
} from '@carbon/react';
import {
  View,
  Checkmark,
  Close,
  Filter,
  Download,
  Play,
  LogoGithub,
} from '@carbon/icons-react';
import { liveReviewService, platformService } from '../../services/platformService';
import './PullRequests.scss';

const SAMPLE_PR_URLS = [
  'https://github.com/fastapi/fastapi/pull/15540',
  'https://github.com/sindresorhus/is/pull/176',
  'https://github.com/encode/httpx/pull/3299',
];

/** Map API / mock PR objects to the shape the table and filters expect. */
function normalizePullRequest(pr, index) {
  const id =
    pr.id != null && pr.id !== ''
      ? String(pr.id)
      : `pr-${pr.number ?? index}-${index}`;
  const security = Number(pr.securityFindings);
  const architecture = Number(pr.architectureFindings);
  const compliance = Number(pr.complianceFindings);
  const findingsCount = [security, architecture, compliance].every((n) => Number.isFinite(n))
    ? security + architecture + compliance
    : 0;

  const statusRaw = pr.status ?? pr.state;
  const status = typeof statusRaw === 'string' ? statusRaw : 'open';
  const severityRaw = pr.severity;
  const severity =
    typeof severityRaw === 'string' && severityRaw.trim()
      ? severityRaw
      : 'medium';

  return {
    id,
    number: pr.number ?? '—',
    repository:
      typeof pr.repository === 'string' && pr.repository.trim()
        ? pr.repository
        : pr.repository_id != null
          ? `repo-${pr.repository_id}`
          : '—',
    title: typeof pr.title === 'string' ? pr.title : 'Untitled',
    author: typeof pr.author === 'string' ? pr.author : '—',
    severity,
    status,
    aiReviewStatus:
      typeof pr.aiReviewStatus === 'string' ? pr.aiReviewStatus : 'pending',
    securityFindings: Number.isFinite(security) ? security : 0,
    architectureFindings: Number.isFinite(architecture) ? architecture : 0,
    complianceFindings: Number.isFinite(compliance) ? compliance : 0,
    findings: String(findingsCount),
  };
}

const PullRequests = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRepository, setSelectedRepository] = useState('all');
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [isLiveModalOpen, setIsLiveModalOpen] = useState(false);
  const [liveUrl, setLiveUrl] = useState(SAMPLE_PR_URLS[0]);
  const [useRag, setUseRag] = useState(true);

  const liveAnalysis = useMutation({
    mutationFn: ({ url, useRag }) =>
      liveReviewService.analyzePullRequestUrl({ url, useRag, ragLimit: 4 }),
  });

  const { data: pullRequests, isLoading, isError, error } = useQuery({
    queryKey: ['pullRequests'],
    queryFn: () => platformService.getPullRequests(),
  });

  const { data: repositories } = useQuery({
    queryKey: ['repositories'],
    queryFn: () => platformService.getRepositories(),
  });

  if (isLoading) {
    return <PullRequestsSkeleton />;
  }

  if (isError) {
    return (
      <div className="pull-requests-page">
        <div className="page-header">
          <h1>Pull Requests</h1>
          <p className="page-subtitle">Could not load pull requests from the backend.</p>
        </div>
        <InlineNotification
          kind="error"
          title="API error"
          subtitle={
            error?.response?.data?.detail ||
            error?.message ||
            'Check that the backend is running and CORS allows this origin (VITE_API_URL).'
          }
          lowContrast
        />
      </div>
    );
  }

  const normalizedList = (pullRequests || []).map(normalizePullRequest);

  let filteredData = normalizedList;

  if (searchTerm) {
    const q = searchTerm.toLowerCase();
    filteredData = filteredData.filter(
      (pr) =>
        String(pr.title).toLowerCase().includes(q) ||
        String(pr.repository).toLowerCase().includes(q) ||
        String(pr.author).toLowerCase().includes(q)
    );
  }

  if (selectedRepository !== 'all') {
    filteredData = filteredData.filter((pr) => pr.repository === selectedRepository);
  }

  if (selectedSeverity !== 'all') {
    filteredData = filteredData.filter((pr) => pr.severity === selectedSeverity);
  }

  if (selectedStatus !== 'all') {
    filteredData = filteredData.filter((pr) => pr.status === selectedStatus);
  }

  // Pagination
  const totalItems = filteredData.length;
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = filteredData.slice(startIndex, endIndex);

  // Repository options
  const repositoryOptions = [
    { id: 'all', label: 'All Repositories' },
    ...(repositories?.map((repo) => ({
      id: repo.name || repo.full_name || String(repo.id),
      label: repo.full_name || repo.name || `Repository ${repo.id}`,
    })) || []),
  ];

  const severityOptions = [
    { id: 'all', label: 'All Severities' },
    { id: 'critical', label: 'Critical' },
    { id: 'high', label: 'High' },
    { id: 'medium', label: 'Medium' },
    { id: 'low', label: 'Low' },
  ];

  const statusOptions = [
    { id: 'all', label: 'All Statuses' },
    { id: 'open', label: 'Open' },
    { id: 'in_review', label: 'In Review' },
    { id: 'resolved', label: 'Resolved' },
    { id: 'closed', label: 'Closed' },
  ];

  // Table headers
  const headers = [
    { key: 'number', header: 'PR #' },
    { key: 'repository', header: 'Repository' },
    { key: 'title', header: 'Title' },
    { key: 'author', header: 'Author' },
    { key: 'severity', header: 'Severity' },
    { key: 'status', header: 'Status' },
    { key: 'aiReviewStatus', header: 'AI Review' },
    { key: 'findings', header: 'Findings' },
    { key: 'actions', header: 'Actions' },
  ];

  // Table rows (ids must be strings for Carbon DataTable)
  const rows = paginatedData.map((pr) => ({
    id: pr.id,
    number: pr.number,
    repository: pr.repository,
    title: pr.title,
    author: pr.author,
    severity: pr.severity,
    status: pr.status,
    aiReviewStatus: pr.aiReviewStatus,
    findings: pr.findings,
  }));

  const handleViewReview = (prId) => {
    const id = typeof prId === 'string' ? prId : String(prId);
    navigate(`/reviews/${id.replace(/^pr-/, '').replace(/^review-/, '')}`);
  };

  return (
    <div className="pull-requests-page">
      <div className="page-header pull-requests-header">
        <div>
          <h1>Pull Requests</h1>
          <p className="page-subtitle">
            Manage and review pull requests across all repositories
          </p>
        </div>
        <Button
          kind="primary"
          renderIcon={Play}
          onClick={() => { setIsLiveModalOpen(true); liveAnalysis.reset(); }}
        >
          Analyze GitHub PR
        </Button>
      </div>

      {/* Filters */}
      <Grid narrow className="filters-section">
        <Column sm={4} md={4} lg={4}>
          <Dropdown
            id="repository-filter"
            titleText="Repository"
            label="Select repository"
            items={repositoryOptions}
            itemToString={(item) => item?.label || ''}
            selectedItem={repositoryOptions.find((opt) => opt.id === selectedRepository)}
            onChange={({ selectedItem }) => setSelectedRepository(selectedItem.id)}
          />
        </Column>
        <Column sm={4} md={4} lg={4}>
          <Dropdown
            id="severity-filter"
            titleText="Severity"
            label="Select severity"
            items={severityOptions}
            itemToString={(item) => item?.label || ''}
            selectedItem={severityOptions.find((opt) => opt.id === selectedSeverity)}
            onChange={({ selectedItem }) => setSelectedSeverity(selectedItem.id)}
          />
        </Column>
        <Column sm={4} md={4} lg={4}>
          <Dropdown
            id="status-filter"
            titleText="Status"
            label="Select status"
            items={statusOptions}
            itemToString={(item) => item?.label || ''}
            selectedItem={statusOptions.find((opt) => opt.id === selectedStatus)}
            onChange={({ selectedItem }) => setSelectedStatus(selectedItem.id)}
          />
        </Column>
      </Grid>

      {/* Data Table */}
      <div className="table-section">
        <DataTable rows={rows} headers={headers} isSortable>
          {({
            rows,
            headers,
            getHeaderProps,
            getRowProps,
            getSelectionProps,
            getToolbarProps,
            getBatchActionProps,
            getTableProps,
          }) => {
            const batchActionProps = getBatchActionProps();
            const { key: _selectAllKey, ...selectAllProps } = getSelectionProps();

            return (
              <TableContainer>
                <TableToolbar {...getToolbarProps()}>
                  <TableBatchActions {...batchActionProps}>
                    <TableBatchAction
                      tabIndex={batchActionProps.shouldShowBatchActions ? 0 : -1}
                      renderIcon={Checkmark}
                      onClick={() => console.log('Approve selected')}
                    >
                      Approve
                    </TableBatchAction>
                    <TableBatchAction
                      tabIndex={batchActionProps.shouldShowBatchActions ? 0 : -1}
                      renderIcon={Close}
                      onClick={() => console.log('Request changes')}
                    >
                      Request Changes
                    </TableBatchAction>
                    <TableBatchAction
                      tabIndex={batchActionProps.shouldShowBatchActions ? 0 : -1}
                      renderIcon={Download}
                      onClick={() => console.log('Export selected')}
                    >
                      Export
                    </TableBatchAction>
                  </TableBatchActions>
                  <TableToolbarContent
                    aria-hidden={batchActionProps.shouldShowBatchActions}
                  >
                    <TableToolbarSearch
                      persistent
                      placeholder="Search pull requests..."
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    <Button
                      kind="secondary"
                      renderIcon={Filter}
                      iconDescription="Advanced filters"
                    >
                      Filters
                    </Button>
                  </TableToolbarContent>
                </TableToolbar>
                <Table {...getTableProps()}>
                  <TableHead>
                    <TableRow>
                      <TableSelectAll {...selectAllProps} />
                      {headers.map((header) => {
                        const { key: _headerKey, ...headerProps } = getHeaderProps({ header });
                        return (
                          <TableHeader key={header.key} {...headerProps}>
                            {header.header}
                          </TableHeader>
                        );
                      })}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((row) => {
                      const { key: _rowKey, ...rowProps } = getRowProps({ row });
                      const { key: _selectRowKey, ...selectRowProps } =
                        getSelectionProps({ row });
                      return (
                        <TableRow key={row.id} {...rowProps}>
                          <TableSelectRow {...selectRowProps} />
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
                            if (cell.info.header === 'aiReviewStatus') {
                              return (
                                <TableCell key={cell.id}>
                                  <AIReviewStatusTag status={cell.value} />
                                </TableCell>
                              );
                            }
                            if (cell.info.header === 'actions') {
                              return (
                                <TableCell key={cell.id}>
                                  <Button
                                    kind="ghost"
                                    size="sm"
                                    renderIcon={View}
                                    onClick={() => handleViewReview(row.id)}
                                  >
                                    View Review
                                  </Button>
                                </TableCell>
                              );
                            }
                            return <TableCell key={cell.id}>{cell.value}</TableCell>;
                          })}
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            );
          }}
        </DataTable>

        {/* Pagination */}
        <Pagination
          backwardText="Previous page"
          forwardText="Next page"
          itemsPerPageText="Items per page:"
          page={currentPage}
          pageSize={pageSize}
          pageSizes={[10, 20, 30, 40, 50]}
          totalItems={totalItems}
          onChange={({ page, pageSize }) => {
            setCurrentPage(page);
            setPageSize(pageSize);
          }}
        />
      </div>

      <LiveAnalyzeModal
        open={isLiveModalOpen}
        onClose={() => setIsLiveModalOpen(false)}
        url={liveUrl}
        onUrlChange={setLiveUrl}
        useRag={useRag}
        onUseRagChange={setUseRag}
        analysis={liveAnalysis}
      />
    </div>
  );
};

const LiveAnalyzeModal = ({ open, onClose, url, onUrlChange, useRag, onUseRagChange, analysis }) => {
  const result = analysis.data;
  const isRunning = analysis.isPending;

  return (
    <Modal
      open={open}
      onRequestClose={() => { onClose(); analysis.reset(); }}
      modalHeading="Live GitHub PR analysis"
      modalLabel="Multi-agent review with RAG"
      primaryButtonText={isRunning ? 'Analyzing...' : 'Run Analysis'}
      secondaryButtonText="Close"
      primaryButtonDisabled={isRunning || !url}
      onRequestSubmit={() => analysis.mutate({ url, useRag })}
      size="lg"
    >
      <p style={{ marginBottom: '1rem' }}>
        Paste a public GitHub PR URL. The backend fetches the diff, retrieves matching context from the Db2 knowledge base, then runs the Security, Architecture, and Compliance agents in parallel.
      </p>

      <TextInput
        id="pr-url"
        labelText="GitHub PR URL"
        placeholder="https://github.com/owner/repo/pull/123"
        value={url}
        onChange={(e) => onUrlChange(e.target.value)}
      />

      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', margin: '0.75rem 0 1rem' }}>
        {SAMPLE_PR_URLS.map((sample) => (
          <Tag
            key={sample}
            type="cool-gray"
            renderIcon={LogoGithub}
            onClick={() => onUrlChange(sample)}
            style={{ cursor: 'pointer' }}
          >
            {sample.replace('https://github.com/', '')}
          </Tag>
        ))}
      </div>

      <Toggle
        id="use-rag"
        labelText="Retrieve context from knowledge base (RAG)"
        toggled={useRag}
        onToggle={() => onUseRagChange(!useRag)}
        size="sm"
      />

      {isRunning && (
        <div style={{ marginTop: '1rem' }}>
          <InlineLoading description="Fetching PR, retrieving RAG context, running 3 agents... (typically 20–60s)" />
        </div>
      )}

      {analysis.isError && (
        <InlineNotification
          kind="error"
          title="Analysis failed"
          subtitle={analysis.error?.response?.data?.detail || analysis.error?.message || 'Unknown error'}
          hideCloseButton
          lowContrast
        />
      )}

      {result && !isRunning && <LiveAnalysisResult result={result} />}
    </Modal>
  );
};

const LiveAnalysisResult = ({ result }) => {
  const pr = result.pull_request || {};
  const rag = result.rag || {};
  const stats = result.stats || {};
  const agentResults = result.result?.agent_results || {};
  const totalFindings = result.result?.findings_count || 0;

  return (
    <div className="live-analysis-result">
      <div className="live-summary">
        <h3>
          <a href={pr.html_url} target="_blank" rel="noreferrer">#{pr.number} {pr.title}</a>
        </h3>
        <div className="live-summary__meta">
          <Tag type="blue" size="sm">{pr.repository}</Tag>
          <Tag type="cool-gray" size="sm">by {pr.author}</Tag>
          <Tag type="purple" size="sm">{stats.file_count} files</Tag>
          <Tag type="green" size="sm">+{stats.additions}</Tag>
          <Tag type="red" size="sm">-{stats.deletions}</Tag>
          <Tag type={totalFindings > 0 ? 'red' : 'green'} size="sm">
            {totalFindings} finding{totalFindings === 1 ? '' : 's'}
          </Tag>
          {rag.enabled && (
            <Tag type="teal" size="sm">
              RAG: {rag.retrieved} chunk{rag.retrieved === 1 ? '' : 's'} from {rag.backend?.backend || 'kb'}
            </Tag>
          )}
        </div>
      </div>

      <Accordion>
        {Object.entries(agentResults).map(([agentName, agent]) => (
          <AccordionItem
            key={agentName}
            title={`${agent.agent || agentName}  •  ${(agent.findings || []).length} finding(s)  •  ${agent.metadata?.overall_severity || agent.category}`}
            open={(agent.findings || []).length > 0}
          >
            <p style={{ marginBottom: '0.75rem' }}>{agent.summary}</p>
            {(agent.findings || []).length === 0 ? (
            <p style={{ marginBottom: '0.75rem', color: 'var(--cds-text-secondary)' }}>No findings.</p>
            ) : (
              <div className="finding-list">
                {agent.findings.map((finding, idx) => (
                  <div key={`${agentName}-${idx}`} className={`finding finding--${finding.severity || 'low'}`}>
                    <div className="finding__header">
                      <Tag type={severityTagType(finding.severity)} size="sm">
                        {(finding.severity || 'low').toUpperCase()}
                      </Tag>
                      <strong>{finding.file || finding.path || '(general)'}</strong>
                      {finding.category && <Tag type="cool-gray" size="sm">{finding.category}</Tag>}
                      {finding.source && <Tag type="outline" size="sm">{finding.source}</Tag>}
                    </div>
                    <p className="finding__message">{finding.message}</p>
                    {finding.recommendation && (
                      <p className="finding__rec"><strong>Fix:</strong> {finding.recommendation}</p>
                    )}
                    {finding.line_hint && (
                      <CodeSnippet type="inline">{finding.line_hint}</CodeSnippet>
                    )}
                  </div>
                ))}
              </div>
            )}
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
};

const severityTagType = (severity) => {
  switch ((severity || '').toLowerCase()) {
    case 'critical': return 'red';
    case 'high': return 'magenta';
    case 'medium': return 'yellow';
    case 'low': return 'green';
    default: return 'cool-gray';
  }
};

// Helper Components
const SeverityTag = ({ severity }) => {
  const severityConfig = {
    critical: { type: 'red' },
    high: { type: 'magenta' },
    medium: { type: 'yellow' },
    low: { type: 'green' },
  };

  const key = String(severity ?? 'low').toLowerCase();
  const config = severityConfig[key] || severityConfig.low;

  return (
    <Tag type={config.type} size="sm">
      {key}
    </Tag>
  );
};

const StatusTag = ({ status }) => {
  const statusConfig = {
    open: { type: 'blue' },
    in_review: { type: 'cyan' },
    resolved: { type: 'green' },
    closed: { type: 'gray' },
  };

  const safeStatus = String(status ?? 'open').trim() || 'open';
  const normalized = safeStatus.toLowerCase().replace(/\s+/g, '_');
  const config = statusConfig[normalized] || statusConfig.open;

  return (
    <Tag type={config.type} size="sm">
      {safeStatus.replace(/_/g, ' ')}
    </Tag>
  );
};

const AIReviewStatusTag = ({ status }) => {
  const statusConfig = {
    completed: { type: 'green', label: 'Completed' },
    running: { type: 'blue', label: 'Running' },
    pending: { type: 'gray', label: 'Pending' },
    failed: { type: 'red', label: 'Failed' },
  };

  const key = String(status ?? 'pending').toLowerCase();
  const config = statusConfig[key] || statusConfig.pending;

  return (
    <Tag type={config.type} size="sm">
      {config.label}
    </Tag>
  );
};

const PullRequestsSkeleton = () => (
  <div className="pull-requests-page">
    <div className="page-header">
      <SkeletonText heading width="200px" />
      <SkeletonText width="400px" />
    </div>
    <div className="table-section">
      <SkeletonPlaceholder style={{ height: '500px' }} />
    </div>
  </div>
);

export default PullRequests;

// Made with Bob