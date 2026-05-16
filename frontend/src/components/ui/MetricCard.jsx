import PropTypes from 'prop-types';
import { Tile } from '@carbon/react';
import { ArrowUp, ArrowDown } from '@carbon/icons-react';
import './MetricCard.scss';

/**
 * MetricCard Component
 * Reusable KPI card component with trend indicators
 * 
 * @param {Object} props
 * @param {string} props.title - Card title
 * @param {string|number} props.value - Main metric value
 * @param {Object} props.trend - Trend data: { direction: 'up'|'down', value: string }
 * @param {React.Component} props.icon - Icon component
 * @param {Function} props.onClick - Click handler (makes card clickable)
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.loading - Loading state
 */
const MetricCard = ({
  title,
  value,
  trend,
  icon: Icon,
  onClick,
  className = '',
  loading = false,
}) => {
  const isClickable = !!onClick;
  
  const renderTrend = () => {
    if (!trend) return null;
    
    const isPositive = trend.direction === 'up';
    const TrendIcon = isPositive ? ArrowUp : ArrowDown;
    
    return (
      <div className={`metric-card__trend metric-card__trend--${trend.direction}`}>
        <TrendIcon size={16} />
        <span>{trend.value}</span>
      </div>
    );
  };

  const content = (
    <>
      <div className="metric-card__header">
        {Icon && (
          <div className="metric-card__icon">
            <Icon size={24} />
          </div>
        )}
        <h4 className="metric-card__title">{title}</h4>
      </div>
      
      <div className="metric-card__body">
        <div className="metric-card__value">
          {loading ? (
            <div className="metric-card__skeleton" />
          ) : (
            value
          )}
        </div>
        {!loading && renderTrend()}
      </div>
    </>
  );

  return (
    <Tile
      className={`metric-card ${isClickable ? 'metric-card--clickable' : ''} ${className}`}
      onClick={onClick}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={isClickable ? (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      } : undefined}
    >
      {content}
    </Tile>
  );
};

MetricCard.propTypes = {
  title: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  trend: PropTypes.shape({
    direction: PropTypes.oneOf(['up', 'down']).isRequired,
    value: PropTypes.string.isRequired,
  }),
  icon: PropTypes.elementType,
  onClick: PropTypes.func,
  className: PropTypes.string,
  loading: PropTypes.bool,
};

export default MetricCard;

// Made with Bob
