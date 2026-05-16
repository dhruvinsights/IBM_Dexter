import PropTypes from 'prop-types';
import { Tag } from '@carbon/react';
import './SeverityTag.scss';

/**
 * SeverityTag Component
 * Provides security/issue severity indicators with consistent IBM styling
 * 
 * @param {Object} props
 * @param {string} props.severity - Severity level: 'critical', 'high', 'medium', 'low'
 * @param {number} props.count - Optional count badge
 * @param {boolean} props.showLabel - Whether to show severity label
 * @param {string} props.className - Additional CSS classes
 */
const SeverityTag = ({
  severity = 'low',
  count,
  showLabel = true,
  className = '',
}) => {
  const getSeverityConfig = () => {
    switch (severity) {
      case 'critical':
        return {
          type: 'red',
          label: 'Critical',
          color: '#da1e28', // IBM Red 60
        };
      case 'high':
        return {
          type: 'magenta',
          label: 'High',
          color: '#ee5396', // IBM Magenta 50
        };
      case 'medium':
        return {
          type: 'yellow',
          label: 'Medium',
          color: '#f1c21b', // IBM Yellow 30
        };
      case 'low':
      default:
        return {
          type: 'gray',
          label: 'Low',
          color: '#8d8d8d', // IBM Gray 60
        };
    }
  };

  const config = getSeverityConfig();
  const displayLabel = showLabel ? config.label : '';
  const displayText = count !== undefined 
    ? `${displayLabel}${displayLabel ? ' ' : ''}(${count})`
    : displayLabel;

  return (
    <Tag
      type={config.type}
      className={`severity-tag severity-tag--${severity} ${className}`}
    >
      {displayText}
    </Tag>
  );
};

SeverityTag.propTypes = {
  severity: PropTypes.oneOf(['critical', 'high', 'medium', 'low']).isRequired,
  count: PropTypes.number,
  showLabel: PropTypes.bool,
  className: PropTypes.string,
};

export default SeverityTag;

// Made with Bob
