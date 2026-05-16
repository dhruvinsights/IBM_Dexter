import { useState } from 'react';
import PropTypes from 'prop-types';
import { Tile, IconButton } from '@carbon/react';
import { Renew, Download } from '@carbon/icons-react';
import LoadingState from './LoadingState';
import ErrorState from './ErrorState';
import './ChartContainer.scss';

/**
 * ChartContainer Component
 * Wrapper for all charts with loading, error handling, and actions
 * 
 * @param {Object} props
 * @param {string} props.title - Chart title
 * @param {boolean} props.loading - Loading state
 * @param {Error|string} props.error - Error object or message
 * @param {Function} props.onRefresh - Refresh button handler
 * @param {Function} props.onExport - Export button handler
 * @param {React.ReactNode} props.children - Chart content
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.description - Optional description text
 */
const ChartContainer = ({
  title,
  loading = false,
  error = null,
  onRefresh,
  onExport,
  children,
  className = '',
  description,
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    if (!onRefresh || isRefreshing) return;
    
    setIsRefreshing(true);
    try {
      await onRefresh();
    } finally {
      setIsRefreshing(false);
    }
  };

  const renderActions = () => {
    if (!onRefresh && !onExport) return null;

    return (
      <div className="chart-container__actions">
        {onRefresh && (
          <IconButton
            kind="ghost"
            label="Refresh"
            onClick={handleRefresh}
            disabled={loading || isRefreshing}
          >
            <Renew />
          </IconButton>
        )}
        {onExport && (
          <IconButton
            kind="ghost"
            label="Export"
            onClick={onExport}
            disabled={loading}
          >
            <Download />
          </IconButton>
        )}
      </div>
    );
  };

  const renderContent = () => {
    if (error) {
      return (
        <ErrorState
          error={error}
          onRetry={onRefresh}
        />
      );
    }

    if (loading) {
      return (
        <div className="chart-container__loading">
          <LoadingState variant="card" count={1} />
        </div>
      );
    }

    return (
      <div className="chart-container__content">
        {children}
      </div>
    );
  };

  return (
    <Tile className={`chart-container ${className}`}>
      <div className="chart-container__header">
        <div className="chart-container__header-content">
          <h4 className="chart-container__title">{title}</h4>
          {description && (
            <p className="chart-container__description">{description}</p>
          )}
        </div>
        {renderActions()}
      </div>
      {renderContent()}
    </Tile>
  );
};

ChartContainer.propTypes = {
  title: PropTypes.string.isRequired,
  loading: PropTypes.bool,
  error: PropTypes.oneOfType([
    PropTypes.instanceOf(Error),
    PropTypes.string,
  ]),
  onRefresh: PropTypes.func,
  onExport: PropTypes.func,
  children: PropTypes.node,
  className: PropTypes.string,
  description: PropTypes.string,
};

export default ChartContainer;

// Made with Bob
