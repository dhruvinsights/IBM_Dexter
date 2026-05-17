import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  Tabs,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Tag,
  CodeSnippet,
  SkeletonText,
  Breadcrumb,
  BreadcrumbItem,
  Button,
  ProgressBar,
  Accordion,
  AccordionItem,
} from '@carbon/react';
import {
  CheckmarkFilled,
  WarningAltFilled,
  ErrorFilled,
  Security,
  ReferenceArchitecture,
  Checkmark,
  Close,
  DocumentView,
} from '@carbon/icons-react';
import { platformService } from '../../services/platformService';
import { APP_SHELL_BASE } from '../../constants/appConstants';
import './ReviewDetail.scss';

const ReviewDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [selectedTab, setSelectedTab] = useState(0);
  
  const { data: review, isLoading } = useQuery({
    queryKey: ['review', id],
    queryFn: () => platformService.getReviewById(id),
  });

  if (isLoading) {
    return <ReviewDetailSkeleton />;
  }

  if (!review) {
    return (
      <div className="empty-state">
        <h3>Review Not Found</h3>
        <p>The review you're looking for doesn't exist.</p>
        <Button onClick={() => navigate(`${APP_SHELL_BASE}/reviews`)}>Back to Reviews</Button>
      </div>
    );
  }

  const securityFindings = review.findings?.filter(f => f.category === 'security') || [];
  const architectureFindings = review.findings?.filter(f => f.category === 'architecture') || [];
  const complianceFindings = review.findings?.filter(f => f.category === 'compliance') || [];

  return (
    <div className="review-detail">
      <Breadcrumb>
        <BreadcrumbItem href={`${APP_SHELL_BASE}/dashboard`}>Dashboard</BreadcrumbItem>
        <BreadcrumbItem href={`${APP_SHELL_BASE}/reviews`}>Reviews</BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>Review #{id}</BreadcrumbItem>
      </Breadcrumb>

      <div className="page-header">
        <div className="header-content">
          <h1>{review.title}</h1>
          <p className="repository-name">{review.repository}</p>
        </div>
        <div className="header-actions">
          <Tag type={review.status === 'completed' ? 'green' : 'blue'}>
            {review.status}
          </Tag>
          <Button kind="primary" renderIcon={Checkmark}>
            Approve
          </Button>
          <Button kind="secondary" renderIcon={Close}>
            Request Changes
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <Grid narrow className="summary-section">
        <Column sm={4} md={2} lg={3}>
          <Tile className="summary-card">
            <div className="summary-value">{review.findings?.length || 0}</div>
            <div className="summary-label">Total Findings</div>
          </Tile>
        </Column>
        <Column sm={4} md={2} lg={3}>
          <Tile className="summary-card critical">
            <div className="summary-value">{securityFindings.length}</div>
            <div className="summary-label">Security Issues</div>
          </Tile>
        </Column>
        <Column sm={4} md={2} lg={3}>
          <Tile className="summary-card high">
            <div className="summary-value">{architectureFindings.length}</div>
            <div className="summary-label">Architecture Issues</div>
          </Tile>
        </Column>
        <Column sm={4} md={2} lg={3}>
          <Tile className="summary-card medium">
            <div className="summary-value">{complianceFindings.length}</div>
            <div className="summary-label">Compliance Issues</div>
          </Tile>
        </Column>
      </Grid>

      {/* Tabs Section */}
      <div className="tabs-section">
        <Tabs selectedIndex={selectedTab} onChange={({ selectedIndex }) => setSelectedTab(selectedIndex)}>
          <TabList aria-label="Review tabs" contained>
            <Tab>Overview</Tab>
            <Tab>Files Changed</Tab>
            <Tab>Security</Tab>
            <Tab>Architecture</Tab>
            <Tab>Compliance</Tab>
          </TabList>
          <TabPanels>
            {/* Overview Tab */}
            <TabPanel>
              <OverviewTab review={review} />
            </TabPanel>

            {/* Files Changed Tab */}
            <TabPanel>
              <FilesChangedTab review={review} />
            </TabPanel>

            {/* Security Tab */}
            <TabPanel>
              <SecurityTab findings={securityFindings} />
            </TabPanel>

            {/* Architecture Tab */}
            <TabPanel>
              <ArchitectureTab findings={architectureFindings} />
            </TabPanel>

            {/* Compliance Tab */}
            <TabPanel>
              <ComplianceTab findings={complianceFindings} />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>
    </div>
  );
};

// Overview Tab Component
const OverviewTab = ({ review }) => (
  <Grid narrow className="tab-content">
    <Column sm={4} md={8} lg={10}>
      <Tile className="overview-tile">
        <h3>AI Summary</h3>
        <p className="summary-text">{review.summary}</p>
        
        <h3 className="section-heading">Key Findings</h3>
        <div className="findings-overview">
          {review.findings?.slice(0, 5).map((finding, idx) => (
            <div key={idx} className="finding-preview">
              <SeverityTag severity={finding.severity} />
              <div className="finding-info">
                <h4>{finding.title}</h4>
                <p>{finding.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Tile>
    </Column>
    
    <Column sm={4} md={8} lg={6}>
      <Tile className="agents-tile">
        <h3>AI Agents Status</h3>
        <div className="agents-list">
          {review.agents?.map((agent, idx) => (
            <div key={idx} className="agent-item">
              <div className="agent-header">
                <span className="agent-name">{agent.name}</span>
                <Tag type={agent.status === 'completed' ? 'green' : 'blue'} size="sm">
                  {agent.status}
                </Tag>
              </div>
              <div className="agent-confidence">
                <span className="confidence-label">Confidence</span>
                <ProgressBar
                  value={agent.confidence * 100}
                  max={100}
                  size="sm"
                  label={`${Math.round(agent.confidence * 100)}%`}
                />
              </div>
            </div>
          ))}
        </div>
      </Tile>
      
      <Tile className="metadata-tile">
        <h3>Review Metadata</h3>
        <div className="metadata-list">
          <div className="metadata-item">
            <span className="metadata-label">PR Number</span>
            <span className="metadata-value">#{review.pull_request_id}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Repository</span>
            <span className="metadata-value">{review.repository}</span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Created</span>
            <span className="metadata-value">
              {new Date(review.created_at).toLocaleDateString()}
            </span>
          </div>
          <div className="metadata-item">
            <span className="metadata-label">Status</span>
            <span className="metadata-value">{review.status}</span>
          </div>
        </div>
      </Tile>
    </Column>
  </Grid>
);

// Files Changed Tab Component
const FilesChangedTab = ({ review }) => (
  <div className="tab-content">
    <Tile className="files-tile">
      <h3>Changed Files</h3>
      {review.diff && review.diff.length > 0 ? (
        <Accordion>
          {review.diff.map((file, idx) => (
            <AccordionItem key={idx} title={file.file}>
              <div className="file-diff">
                <div className="diff-header">
                  <Tag type="blue" size="sm">{file.language}</Tag>
                  <span className="file-path">{file.file}</span>
                </div>
                <div className="diff-content">
                  {file.hunks?.map((hunk, hunkIdx) => (
                    <div key={hunkIdx} className={`diff-line ${hunk.type}`}>
                      <span className="line-number">{hunk.line}</span>
                      <CodeSnippet type="single" hideCopyButton>
                        {hunk.content}
                      </CodeSnippet>
                    </div>
                  ))}
                </div>
                
                {/* Inline AI Comments */}
                {review.comments?.filter(c => c.file === file.file).map((comment, cIdx) => (
                  <div key={cIdx} className="inline-comment">
                    <div className="comment-header">
                      <strong>{comment.author}</strong>
                      <Tag type="purple" size="sm">AI Comment</Tag>
                    </div>
                    <p>{comment.body}</p>
                  </div>
                ))}
              </div>
            </AccordionItem>
          ))}
        </Accordion>
      ) : (
        <p className="empty-message">No file changes available</p>
      )}
    </Tile>
  </div>
);

// Security Tab Component
const SecurityTab = ({ findings }) => (
  <div className="tab-content">
    <Tile className="findings-tile">
      <div className="tile-header">
        <Security size={24} />
        <h3>Security Findings ({findings.length})</h3>
      </div>
      
      {findings.length > 0 ? (
        <div className="findings-list">
          {findings.map((finding, idx) => (
            <FindingCard key={idx} finding={finding} />
          ))}
        </div>
      ) : (
        <div className="empty-findings">
          <CheckmarkFilled size={32} />
          <p>No security issues found</p>
        </div>
      )}
    </Tile>
  </div>
);

// Architecture Tab Component
const ArchitectureTab = ({ findings }) => (
  <div className="tab-content">
    <Tile className="findings-tile">
      <div className="tile-header">
        <ReferenceArchitecture size={24} />
        <h3>Architecture Findings ({findings.length})</h3>
      </div>
      
      {findings.length > 0 ? (
        <div className="findings-list">
          {findings.map((finding, idx) => (
            <FindingCard key={idx} finding={finding} />
          ))}
        </div>
      ) : (
        <div className="empty-findings">
          <CheckmarkFilled size={32} />
          <p>No architecture issues found</p>
        </div>
      )}
    </Tile>
  </div>
);

// Compliance Tab Component
const ComplianceTab = ({ findings }) => (
  <div className="tab-content">
    <Tile className="findings-tile">
      <div className="tile-header">
        <DocumentView size={24} />
        <h3>Compliance Findings ({findings.length})</h3>
      </div>
      
      {findings.length > 0 ? (
        <div className="findings-list">
          {findings.map((finding, idx) => (
            <FindingCard key={idx} finding={finding} />
          ))}
        </div>
      ) : (
        <div className="empty-findings">
          <CheckmarkFilled size={32} />
          <p>No compliance issues found</p>
        </div>
      )}
    </Tile>
  </div>
);

// Finding Card Component
const FindingCard = ({ finding }) => (
  <div className="finding-card">
    <div className="finding-header">
      <SeverityTag severity={finding.severity} />
      <h4>{finding.title}</h4>
    </div>
    
    <p className="finding-description">{finding.description}</p>
    
    {finding.file && (
      <div className="finding-location">
        <strong>Location:</strong> {finding.file}
        {finding.line && ` (Line ${finding.line})`}
      </div>
    )}
    
    {finding.code && (
      <div className="finding-code">
        <CodeSnippet type="multi" feedback="Copied">
          {finding.code}
        </CodeSnippet>
      </div>
    )}
    
    {finding.suggestion && (
      <div className="finding-suggestion">
        <h5>Suggested Fix:</h5>
        <p>{finding.suggestion}</p>
      </div>
    )}
    
    {finding.reasoning && (
      <div className="finding-reasoning">
        <h5>AI Reasoning:</h5>
        <p>{finding.reasoning}</p>
      </div>
    )}
  </div>
);

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

const ReviewDetailSkeleton = () => (
  <div className="review-detail">
    <SkeletonText heading width="60%" />
    <SkeletonText width="40%" />
    <Grid narrow>
      <Column sm={4} md={8} lg={16}>
        <Tile>
          <SkeletonText heading />
          <SkeletonText paragraph lineCount={10} />
        </Tile>
      </Column>
    </Grid>
  </div>
);

export default ReviewDetail;

// Made with Bob
