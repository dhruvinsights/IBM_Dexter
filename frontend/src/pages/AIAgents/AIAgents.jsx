import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Grid,
  Column,
  Tile,
  SkeletonText,
  SkeletonPlaceholder,
  Tag,
  Toggle,
  Slider,
  Accordion,
  AccordionItem,
} from '@carbon/react';
import {
  Ai,
  CheckmarkFilled,
  WarningAltFilled,
  Time,
  Security,
  ReferenceArchitecture,
  Renew,
  Dashboard,
  Checkmark,
} from '@carbon/icons-react';
import { agentsService, aiAgentsService } from '../../services/platformService';
import './AIAgents.scss';

const AIAgents = () => {
  const [configuration, setConfiguration] = useState({
    enabledAgents: ['security', 'architecture', 'compliance', 'modernization', 'performance'],
    confidenceThreshold: 75,
    reviewFrequency: 'on_commit',
    notifications: {
      critical: true,
      high: true,
      medium: false,
      low: false,
    },
  });

  const { data: agentsData, isLoading } = useQuery({
    queryKey: ['aiAgents'],
    queryFn: aiAgentsService.getSummary,
  });

  const { data: liveAgents = [] } = useQuery({
    queryKey: ['agents-live'],
    queryFn: agentsService.list,
    refetchInterval: 10000,
  });

  const { data: liveStatus } = useQuery({
    queryKey: ['agents-status'],
    queryFn: agentsService.status,
    refetchInterval: 10000,
  });

  if (isLoading) {
    return <AIAgentsSkeleton />;
  }

  const { activityTimeline = [] } = agentsData || {};

  const agents = liveAgents.length > 0
    ? liveAgents.map((agent) => ({
        id: agent.id,
        name: agent.display_name,
        description: agent.description,
        status: agent.status,
        findings24h: '-',
        findings7d: '-',
        findingsTotal: '-',
        confidence: agent.rag_enabled ? 'RAG' : 'LLM',
        lastActivity: new Date().toISOString(),
        category: agent.category,
        llm_provider: agent.llm_provider,
      }))
    : (agentsData?.agents || []);

  const getAgentIcon = (agentName) => {
    const iconMap = {
      'Security Agent': Security,
      'Architecture Agent': ReferenceArchitecture,
      'Compliance Agent': Checkmark,
      'Modernization Agent': Renew,
      'Performance Agent': Dashboard,
    };
    return iconMap[agentName] || Ai;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <CheckmarkFilled size={20} className="status-icon status-icon--active" />;
      case 'idle':
        return <Time size={20} className="status-icon status-icon--idle" />;
      case 'processing':
        return <WarningAltFilled size={20} className="status-icon status-icon--processing" />;
      default:
        return null;
    }
  };

  const getSeverityTag = (severity) => {
    const severityMap = {
      critical: { type: 'red', label: 'Critical' },
      high: { type: 'magenta', label: 'High' },
      medium: { type: 'purple', label: 'Medium' },
      low: { type: 'blue', label: 'Low' },
      info: { type: 'cool-gray', label: 'Info' },
    };
    const config = severityMap[severity] || severityMap.info;
    return <Tag type={config.type} size="sm">{config.label}</Tag>;
  };

  const handleToggleAgent = (agentId) => {
    setConfiguration((prev) => ({
      ...prev,
      enabledAgents: prev.enabledAgents.includes(agentId)
        ? prev.enabledAgents.filter((id) => id !== agentId)
        : [...prev.enabledAgents, agentId],
    }));
  };

  const handleConfidenceChange = (value) => {
    setConfiguration((prev) => ({
      ...prev,
      confidenceThreshold: value,
    }));
  };

  const handleNotificationToggle = (level) => {
    setConfiguration((prev) => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [level]: !prev.notifications[level],
      },
    }));
  };

  return (
    <div className="ai-agents-page">
      <div className="page-header">
        <div className="page-header__title">
          <Ai size={32} />
          <h1>AI Agents</h1>
        </div>
        <p className="page-header__description">
          Monitor and configure AI agents that power intelligent code reviews
        </p>
        {liveStatus && (
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem', flexWrap: 'wrap' }}>
            <Tag type="blue" size="sm">LLM: {liveStatus.llm_provider} / {liveStatus.llm_model}</Tag>
            <Tag type="teal" size="sm">
              Embeddings: {liveStatus.embedding_provider || '—'} / {liveStatus.embedding_model || '—'}
              {liveStatus.embedding_dimension ? ` (${liveStatus.embedding_dimension}d)` : ''}
            </Tag>
            <Tag type="purple" size="sm">{liveStatus.agent_count} active agents</Tag>
          </div>
        )}
      </div>

      <Grid className="ai-agents-grid" narrow>
        {/* Agent Status Grid */}
        <Column lg={16} md={8} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <Ai size={24} />
                <h2>Agent Status</h2>
              </div>
            </div>
            <div className="agent-grid">
              {agents.map((agent) => {
                const AgentIcon = getAgentIcon(agent.name);
                const categoryClass = (agent.category || '').replace(/[^a-z0-9]+/gi, '-').toLowerCase();
                return (
                  <div
                    key={agent.id}
                    className={`agent-card agent-card--${agent.status} agent-card--cat-${categoryClass}`}
                  >
                    <div className="agent-card__header">
                      <div className="agent-card__icon">
                        <AgentIcon size={32} />
                      </div>
                      <div className="agent-card__status">
                        {getStatusIcon(agent.status)}
                      </div>
                    </div>
                    <div className="agent-card__body">
                      <h3 className="agent-card__name">{agent.name}</h3>
                      <p className="agent-card__description">{agent.description}</p>
                      <div className="agent-card__metrics">
                        <div className="metric">
                          <span className="metric__label">24h</span>
                          <span className="metric__value">{agent.findings24h}</span>
                        </div>
                        <div className="metric">
                          <span className="metric__label">7d</span>
                          <span className="metric__value">{agent.findings7d}</span>
                        </div>
                        <div className="metric">
                          <span className="metric__label">Total</span>
                          <span className="metric__value">{agent.findingsTotal}</span>
                        </div>
                      </div>
                    </div>
                    <div className="agent-card__footer">
                      <div className="confidence-score">
                        <span className="confidence-score__label">Confidence</span>
                        <span className="confidence-score__value">{agent.confidence}%</span>
                      </div>
                      <div className="last-activity">
                        <Time size={16} />
                        <span>{new Date(agent.lastActivity).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </Tile>
        </Column>

        {/* Activity Timeline */}
        <Column lg={10} md={5} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <Time size={24} />
                <h2>Activity Timeline</h2>
              </div>
            </div>
            <div className="activity-timeline">
              {activityTimeline.map((activity) => (
                <div key={activity.id} className="timeline-item">
                  <div className="timeline-item__time">{activity.time}</div>
                  <div className="timeline-item__content">
                    <div className="timeline-item__header">
                      <Tag type="blue" size="sm">
                        {activity.agent}
                      </Tag>
                      {getSeverityTag(activity.severity)}
                    </div>
                    <p className="timeline-item__action">{activity.action}</p>
                    <p className="timeline-item__result">{activity.result}</p>
                  </div>
                </div>
              ))}
            </div>
          </Tile>
        </Column>

        {/* Agent Configuration */}
        <Column lg={6} md={3} sm={4}>
          <Tile className="section-tile">
            <div className="section-header">
              <div className="section-header__title">
                <Dashboard size={24} />
                <h2>Configuration</h2>
              </div>
            </div>
            <Accordion>
              <AccordionItem title="Enable/Disable Agents">
                <div className="config-section">
                  {agents.map((agent) => (
                    <div key={agent.id} className="config-item">
                      <Toggle
                        id={`toggle-${agent.id}`}
                        labelText={agent.name}
                        toggled={configuration.enabledAgents.includes(agent.id)}
                        onToggle={() => handleToggleAgent(agent.id)}
                        size="sm"
                      />
                    </div>
                  ))}
                </div>
              </AccordionItem>

              <AccordionItem title="Confidence Threshold">
                <div className="config-section">
                  <Slider
                    id="confidence-slider"
                    labelText={`Minimum confidence: ${configuration.confidenceThreshold}%`}
                    value={configuration.confidenceThreshold}
                    min={0}
                    max={100}
                    step={5}
                    onChange={({ value }) => handleConfidenceChange(value)}
                  />
                  <p className="config-help">
                    Agents will only report findings with confidence above this threshold
                  </p>
                </div>
              </AccordionItem>

              <AccordionItem title="Review Frequency">
                <div className="config-section">
                  <div className="frequency-options">
                    <Tag
                      type={configuration.reviewFrequency === 'on_commit' ? 'blue' : 'cool-gray'}
                      onClick={() =>
                        setConfiguration((prev) => ({ ...prev, reviewFrequency: 'on_commit' }))
                      }
                    >
                      On Commit
                    </Tag>
                    <Tag
                      type={configuration.reviewFrequency === 'on_pr' ? 'blue' : 'cool-gray'}
                      onClick={() =>
                        setConfiguration((prev) => ({ ...prev, reviewFrequency: 'on_pr' }))
                      }
                    >
                      On PR
                    </Tag>
                    <Tag
                      type={configuration.reviewFrequency === 'scheduled' ? 'blue' : 'cool-gray'}
                      onClick={() =>
                        setConfiguration((prev) => ({ ...prev, reviewFrequency: 'scheduled' }))
                      }
                    >
                      Scheduled
                    </Tag>
                  </div>
                </div>
              </AccordionItem>

              <AccordionItem title="Notifications">
                <div className="config-section">
                  <div className="config-item">
                    <Toggle
                      id="notif-critical"
                      labelText="Critical findings"
                      toggled={configuration.notifications.critical}
                      onToggle={() => handleNotificationToggle('critical')}
                      size="sm"
                    />
                  </div>
                  <div className="config-item">
                    <Toggle
                      id="notif-high"
                      labelText="High severity findings"
                      toggled={configuration.notifications.high}
                      onToggle={() => handleNotificationToggle('high')}
                      size="sm"
                    />
                  </div>
                  <div className="config-item">
                    <Toggle
                      id="notif-medium"
                      labelText="Medium severity findings"
                      toggled={configuration.notifications.medium}
                      onToggle={() => handleNotificationToggle('medium')}
                      size="sm"
                    />
                  </div>
                  <div className="config-item">
                    <Toggle
                      id="notif-low"
                      labelText="Low severity findings"
                      toggled={configuration.notifications.low}
                      onToggle={() => handleNotificationToggle('low')}
                      size="sm"
                    />
                  </div>
                </div>
              </AccordionItem>
            </Accordion>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

const AIAgentsSkeleton = () => (
  <div className="ai-agents-page">
    <div className="page-header">
      <SkeletonText heading width="30%" />
      <SkeletonText width="50%" />
    </div>
    <Grid narrow>
      <Column lg={16} md={8} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '400px' }} />
        </Tile>
      </Column>
      <Column lg={10} md={5} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '500px' }} />
        </Tile>
      </Column>
      <Column lg={6} md={3} sm={4}>
        <Tile>
          <SkeletonPlaceholder style={{ height: '500px' }} />
        </Tile>
      </Column>
    </Grid>
  </div>
);

export default AIAgents;

// Made with Bob