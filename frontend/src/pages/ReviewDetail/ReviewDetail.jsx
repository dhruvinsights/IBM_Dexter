import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  Accordion,
  AccordionItem,
  Tag,
  CodeSnippet,
  SkeletonText,
  Breadcrumb,
  BreadcrumbItem,
} from '@carbon/react';
import {
  CheckmarkFilled,
  WarningAltFilled,
  ErrorFilled,
  InformationFilled,
} from '@carbon/icons-react';
import { reviewsAPI } from '../../services/api';
import './ReviewDetail.scss';

const ReviewDetail = () => {
  const { id } = useParams();
  
  const { data: review, isLoading } = useQuery({
    queryKey: ['review', id],
    queryFn: () => reviewsAPI.getById(id).then(res => res.data),
  });

  if (isLoading) {
    return <ReviewDetailSkeleton />;
  }

  if (!review) {
    return (
      <div className="empty-state">
        <h3>Review Not Found</h3>
        <p>The review you're looking for doesn't exist.</p>
      </div>
    );
  }

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ErrorFilled size={16} />;
      case 'high':
        return <WarningAltFilled size={16} />;
      case 'medium':
        return <InformationFilled size={16} />;
      case 'low':
        return <CheckmarkFilled size={16} />;
      default:
        return null;
    }
  };

  return (
    <div className="review-detail">
      <Breadcrumb>
        <BreadcrumbItem href="/">Dashboard</BreadcrumbItem>
        <BreadcrumbItem href="/reviews">Reviews</BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>Review #{id}</BreadcrumbItem>
      </Breadcrumb>

      <div className="page-header">
        <h1>Pull Request Review #{review.pull_request_id}</h1>
        <div className="review-meta">
          <Tag type={review.status === 'completed' ? 'green' : 'blue'}>
            {review.status}
          </Tag>
          <span className="review-date">
            {new Date(review.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <Grid narrow>
        <Column sm={4} md={8} lg={12}>
          <Tile className="findings-tile">
            <h2>Findings ({review.findings?.length || 0})</h2>
            
            {review.findings && review.findings.length > 0 ? (
              <Accordion>
                {review.findings.map((finding, index) => (
                  <AccordionItem
                    key={index}
                    title={
                      <div className="finding-title">
                        <span className={`status-badge ${finding.severity}`}>
                          {getSeverityIcon(finding.severity)}
                          {finding.severity}
                        </span>
                        <span>{finding.title || `Finding ${index + 1}`}</span>
                      </div>
                    }
                  >
                    <div className="finding-content">
                      <p className="finding-description">
                        {finding.description || 'No description available'}
                      </p>
                      
                      {finding.file && (
                        <div className="finding-location">
                          <strong>File:</strong> {finding.file}
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
                          <h4>Suggested Fix:</h4>
                          <p>{finding.suggestion}</p>
                        </div>
                      )}
                    </div>
                  </AccordionItem>
                ))}
              </Accordion>
            ) : (
              <div className="empty-findings">
                <CheckmarkFilled size={32} />
                <p>No issues found in this review</p>
              </div>
            )}
          </Tile>
        </Column>

        <Column sm={4} md={8} lg={4}>
          <Tile className="summary-tile">
            <h3>Review Summary</h3>
            
            <div className="summary-stats">
              <div className="summary-stat">
                <span className="status-badge critical">
                  <ErrorFilled size={16} />
                  Critical
                </span>
                <span className="stat-count">
                  {review.findings?.filter(f => f.severity === 'critical').length || 0}
                </span>
              </div>
              
              <div className="summary-stat">
                <span className="status-badge high">
                  <WarningAltFilled size={16} />
                  High
                </span>
                <span className="stat-count">
                  {review.findings?.filter(f => f.severity === 'high').length || 0}
                </span>
              </div>
              
              <div className="summary-stat">
                <span className="status-badge medium">
                  <InformationFilled size={16} />
                  Medium
                </span>
                <span className="stat-count">
                  {review.findings?.filter(f => f.severity === 'medium').length || 0}
                </span>
              </div>
              
              <div className="summary-stat">
                <span className="status-badge low">
                  <CheckmarkFilled size={16} />
                  Low
                </span>
                <span className="stat-count">
                  {review.findings?.filter(f => f.severity === 'low').length || 0}
                </span>
              </div>
            </div>
          </Tile>

          <Tile className="ai-reasoning-tile">
            <h3>AI Reasoning</h3>
            <p className="ai-reasoning-text">
              The AI analyzed this pull request using multiple specialized agents
              including security, architecture, and compliance checks. Each finding
              has been validated against best practices and your organization's
              coding standards.
            </p>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

const ReviewDetailSkeleton = () => (
  <div className="review-detail">
    <SkeletonText heading width="60%" />
    <SkeletonText width="40%" />
    <Grid narrow>
      <Column sm={4} md={8} lg={12}>
        <Tile>
          <SkeletonText heading />
          <SkeletonText paragraph lineCount={5} />
        </Tile>
      </Column>
      <Column sm={4} md={8} lg={4}>
        <Tile>
          <SkeletonText heading />
          <SkeletonText paragraph lineCount={3} />
        </Tile>
      </Column>
    </Grid>
  </div>
);

export default ReviewDetail;

// Made with Bob
