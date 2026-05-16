import { useMemo } from 'react';
import PropTypes from 'prop-types';
import { Tag } from '@carbon/react';
import {
  CheckmarkFilled,
  WarningFilled,
  ErrorFilled,
  InformationFilled,
  InProgress,
} from '@carbon/icons-react';
import './StatusBadge.scss';

/**
 * StatusBadge Component
 * Provides reusable status indicators with consistent styling
 * 
 * @param {Object} props
 * @param {string} props.status - Status type: 'success', 'warning', 'error', 'info', 'in-progress'
 * @param {string} props.label - Badge label text
 * @param {React.Component} props.icon - Custom icon component
 * @param {boolean} props.pulse - Whether to show pulse animation (for in-progress)
 * @param {string} props.className - Additional CSS classes
 */
const StatusBadge = ({
  status = 'info',
  label,
  icon: CustomIcon,
  pulse = false,
  className = '',
}) => {
  const IconComponent = useMemo(() => {
    if (CustomIcon) return CustomIcon;
    
    switch (status) {
      case 'success':
        return CheckmarkFilled;
      case 'warning':
        return WarningFilled;
      case 'error':
        return ErrorFilled;
      case 'in-progress':
        return InProgress;
      case 'info':
      default:
        return InformationFilled;
    }
  }, [CustomIcon, status]);

  const getTagType = () => {
    switch (status) {
      case 'success':
        return 'green';
      case 'warning':
        return 'yellow';
      case 'error':
        return 'red';
      case 'in-progress':
        return 'blue';
      case 'info':
      default:
        return 'gray';
    }
  };

  const shouldPulse = pulse || status === 'in-progress';

  return (
    <Tag
      type={getTagType()}
      className={`status-badge status-badge--${status} ${shouldPulse ? 'status-badge--pulse' : ''} ${className}`}
      renderIcon={IconComponent}
    >
      {label}
    </Tag>
  );
};

StatusBadge.propTypes = {
  status: PropTypes.oneOf(['success', 'warning', 'error', 'info', 'in-progress']),
  label: PropTypes.string.isRequired,
  icon: PropTypes.elementType,
  pulse: PropTypes.bool,
  className: PropTypes.string,
};

export default StatusBadge;

// Made with Bob
