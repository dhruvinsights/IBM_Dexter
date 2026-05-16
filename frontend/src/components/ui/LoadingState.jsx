import React from 'react';
import PropTypes from 'prop-types';
import {
  SkeletonText,
  SkeletonPlaceholder,
} from '@carbon/react';
import './LoadingState.scss';

/**
 * LoadingState Component
 * Provides consistent loading states across the application
 * 
 * @param {Object} props
 * @param {string} props.variant - Type of loading state: 'card', 'table', 'page', 'list'
 * @param {number} props.count - Number of skeleton items to display
 * @param {string} props.className - Additional CSS classes
 */
const LoadingState = ({ variant = 'card', count = 3, className = '' }) => {
  const renderCardSkeleton = () => (
    <div className="loading-state__card">
      <SkeletonPlaceholder className="loading-state__card-header" />
      <SkeletonText paragraph lineCount={3} />
    </div>
  );

  const renderTableSkeleton = () => (
    <div className="loading-state__table">
      <div className="loading-state__table-header">
        <SkeletonText heading width="30%" />
        <SkeletonText heading width="20%" />
        <SkeletonText heading width="25%" />
        <SkeletonText heading width="15%" />
      </div>
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="loading-state__table-row">
          <SkeletonText width="30%" />
          <SkeletonText width="20%" />
          <SkeletonText width="25%" />
          <SkeletonText width="15%" />
        </div>
      ))}
    </div>
  );

  const renderPageSkeleton = () => (
    <div className="loading-state__page">
      <div className="loading-state__page-header">
        <SkeletonText heading width="40%" />
        <SkeletonText width="60%" />
      </div>
      <div className="loading-state__page-content">
        <div className="loading-state__page-metrics">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="loading-state__metric">
              <SkeletonPlaceholder className="loading-state__metric-icon" />
              <SkeletonText heading width="60%" />
              <SkeletonText width="40%" />
            </div>
          ))}
        </div>
        <div className="loading-state__page-charts">
          <SkeletonPlaceholder className="loading-state__chart" />
          <SkeletonPlaceholder className="loading-state__chart" />
        </div>
      </div>
    </div>
  );

  const renderListSkeleton = () => (
    <div className="loading-state__list">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="loading-state__list-item">
          <SkeletonPlaceholder className="loading-state__list-icon" />
          <div className="loading-state__list-content">
            <SkeletonText heading width="70%" />
            <SkeletonText width="90%" />
          </div>
        </div>
      ))}
    </div>
  );

  const renderSkeleton = () => {
    switch (variant) {
      case 'card':
        return Array.from({ length: count }).map((_, index) => (
          <React.Fragment key={index}>{renderCardSkeleton()}</React.Fragment>
        ));
      case 'table':
        return renderTableSkeleton();
      case 'page':
        return renderPageSkeleton();
      case 'list':
        return renderListSkeleton();
      default:
        return renderCardSkeleton();
    }
  };

  return (
    <div className={`loading-state loading-state--${variant} ${className}`}>
      {renderSkeleton()}
    </div>
  );
};

LoadingState.propTypes = {
  variant: PropTypes.oneOf(['card', 'table', 'page', 'list']),
  count: PropTypes.number,
  className: PropTypes.string,
};

export default LoadingState;

// Made with Bob
