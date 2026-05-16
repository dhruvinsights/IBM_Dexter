import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  Tag,
  SkeletonPlaceholder,
  Button,
  Accordion,
  AccordionItem,
} from '@carbon/react';
import { DocumentView, Time, View } from '@carbon/icons-react';
import { reviewService } from '../../services/platformService';
import './Reviews.scss';

const severityTag = (severity) => {
  const map = {
    critical: 'red',
    high: 'magenta',
    medium: 'yellow',
    low: 'green',
    info: 'cool-gray',
    none: 'cool-gray',
  };
  return map[(severity || 'low').toLowerCase()] || 'cool-gray';
};

const Reviews = () => {
  const {
    data: reviews,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ['reviews-list'],
    queryFn: reviewService.list,
    refetchInterval: 10000,
  });

  const list = Array.isArray(reviews) ? reviews : [];

  return (
    <div className="reviews-page">
      <div className="page-header">
        <div>
          <h1>Reviews</h1>
          <p className="page-subtitle">
            Every AI review run is recorded here — including live GitHub PR analyses you trigger from the Pull Requests page.
          </p>
        </div>
        <Button kind="tertiary" size="sm" onClick={() => refetch()}>
          Refresh
        </Button>
      </div>

      {isLoading && <SkeletonPlaceholder style={{ height: 240 }} />}

      {isError && !isLoading && (
        <Tile className="reviews-empty">
          <h3>Could not load reviews</h3>
          <p>
            {error?.response?.data?.detail ||
              error?.message ||
              'Check that the backend is running and VITE_API_URL points at /api/v1.'}
          </p>
        </Tile>
      )}

      {!isLoading && !isError && list.length === 0 && (
        <Tile className="reviews-empty">
          <DocumentView size={48} />
          <h3>No reviews yet</h3>
          <p>
            Trigger one from <strong>Pull Requests → Analyze GitHub PR</strong>. The agent pipeline result will appear here automatically.
          </p>
        </Tile>
      )}

      <Grid narrow>
        {!isLoading &&
          !isError &&
          list.map((review, index) => {
          const result = review.result || {};
          const agentResults = result.agent_results || {};
          const pr = review.pull_request || {};
          const stats = review.stats || {};
          const rowKey =
            review.completed_at ||
            pr.html_url ||
            review.pull_request_id ||
            `review-${index}`;
          return (
            <Column key={String(rowKey)} lg={16} md={8} sm={4}>
              <Tile className="review-card">
                <div className="review-card__header">
                  <div>
                    <h3>
                      {pr.html_url ? (
                        <a href={pr.html_url} target="_blank" rel="noreferrer">
                          #{pr.number || review.pull_request_id || '?'} {pr.title || 'Review'}
                        </a>
                      ) : (
                        <>Review #{review.pull_request_id || index + 1}</>
                      )}
                    </h3>
                    <div className="review-card__meta">
                      {pr.repository && <Tag type="blue" size="sm">{pr.repository}</Tag>}
                      {pr.author && <Tag type="cool-gray" size="sm">{pr.author}</Tag>}
                      {stats.file_count != null && <Tag type="purple" size="sm">{stats.file_count} files</Tag>}
                      {stats.additions != null && <Tag type="green" size="sm">+{stats.additions}</Tag>}
                      {stats.deletions != null && <Tag type="red" size="sm">-{stats.deletions}</Tag>}
                      <Tag type={result.findings_count > 0 ? 'red' : 'green'} size="sm">
                        {result.findings_count ?? 0} finding{result.findings_count === 1 ? '' : 's'}
                      </Tag>
                      {review.rag && (
                        <Tag type="teal" size="sm">
                          RAG: {review.rag.retrieved ?? 0} chunk{review.rag.retrieved === 1 ? '' : 's'}
                        </Tag>
                      )}
                    </div>
                  </div>
                  <div className="review-card__time">
                    <Time size={16} />
                    <span>{review.completed_at ? new Date(review.completed_at).toLocaleString() : '—'}</span>
                  </div>
                </div>

                <Accordion align="start">
                  {Object.entries(agentResults).map(([agentName, agent]) => (
                    <AccordionItem
                      key={agentName}
                      title={`${agent.agent || agentName}  •  ${(agent.findings || []).length} finding(s)`}
                      open={(agent.findings || []).length > 0}
                    >
                      <p style={{ marginBottom: '0.75rem' }}>{agent.summary}</p>
                      {(agent.findings || []).map((finding, idx) => (
                        <div key={idx} className={`review-finding review-finding--${(finding.severity || 'low').toLowerCase()}`}>
                          <div className="review-finding__header">
                            <Tag type={severityTag(finding.severity)} size="sm">
                              {(finding.severity || 'low').toUpperCase()}
                            </Tag>
                            <strong>{finding.file || '(general)'}</strong>
                            {finding.category && <Tag type="cool-gray" size="sm">{finding.category}</Tag>}
                          </div>
                          <p>{finding.message}</p>
                          {finding.recommendation && (
                            <p className="review-finding__rec"><strong>Fix:</strong> {finding.recommendation}</p>
                          )}
                        </div>
                      ))}
                    </AccordionItem>
                  ))}
                </Accordion>
              </Tile>
            </Column>
          );
        })}
      </Grid>
    </div>
  );
};

export default Reviews;

// Made with Bob
