import { useMemo } from 'react';
import PropTypes from 'prop-types';
import { Button } from '@carbon/react';
import {
  DataBase,
  Search,
  Locked,
  Information,
} from '@carbon/icons-react';
import './EmptyState.scss';

/**
 * EmptyState Component
 * Provides consistent empty states across the application
 *
 * @param {Object} props
 * @param {string} props.variant - Type of empty state: 'no-data', 'no-results', 'no-access'
 * @param {string} props.title - Title text
 * @param {string} props.message - Description message
 * @param {string} props.actionLabel - Label for action button
 * @param {Function} props.onAction - Action button click handler
 * @param {React.Component} props.icon - Custom icon component
 */
const EmptyState = ({
  variant = 'no-data',
  title,
  message,
  actionLabel,
  onAction,
  icon: CustomIcon,
}) => {
  const IconComponent = useMemo(() => {
    if (CustomIcon) return CustomIcon;
    
    switch (variant) {
      case 'no-data':
        return DataBase;
      case 'no-results':
        return Search;
      case 'no-access':
        return Locked;
      default:
        return Information;
    }
  }, [CustomIcon, variant]);

  const defaultContent = useMemo(() => {
    switch (variant) {
      case 'no-data':
        return {
          title: 'No data available',
          message: 'There is no data to display at this time. Try refreshing or check back later.',
        };
      case 'no-results':
        return {
          title: 'No results found',
          message: 'We couldn\'t find any results matching your search. Try adjusting your filters or search terms.',
        };
      case 'no-access':
        return {
          title: 'Access restricted',
          message: 'You don\'t have permission to view this content. Contact your administrator for access.',
        };
      default:
        return {
          title: 'Nothing here',
          message: 'There is nothing to display.',
        };
    }
  }, [variant]);

  const displayTitle = title || defaultContent.title;
  const displayMessage = message || defaultContent.message;

  return (
    <div className={`empty-state empty-state--${variant}`}>
      <div className="empty-state__content">
        <div className="empty-state__icon">
          <IconComponent size={64} />
        </div>
        <h3 className="empty-state__title">{displayTitle}</h3>
        <p className="empty-state__message">{displayMessage}</p>
        {actionLabel && onAction && (
          <Button
            kind="primary"
            onClick={onAction}
            className="empty-state__action"
          >
            {actionLabel}
          </Button>
        )}
      </div>
    </div>
  );
};

EmptyState.propTypes = {
  variant: PropTypes.oneOf(['no-data', 'no-results', 'no-access']),
  title: PropTypes.string,
  message: PropTypes.string,
  actionLabel: PropTypes.string,
  onAction: PropTypes.func,
  icon: PropTypes.elementType,
};

export default EmptyState;

// Made with Bob
