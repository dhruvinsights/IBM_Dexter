import { useState } from 'react';
import PropTypes from 'prop-types';
import { Button, Accordion, AccordionItem } from '@carbon/react';
import { WarningAlt, Renew } from '@carbon/icons-react';
import './ErrorState.scss';

/**
 * ErrorState Component
 * Provides consistent error handling and display across the application
 * 
 * @param {Object} props
 * @param {Error|string} props.error - Error object or error message
 * @param {Function} props.onRetry - Retry button click handler
 * @param {boolean} props.showDetails - Whether to show error details
 */
const ErrorState = ({
  error,
  onRetry,
  showDetails = false,
}) => {
  const [detailsExpanded, setDetailsExpanded] = useState(false);

  const errorMessage = typeof error === 'string' 
    ? error 
    : error?.message || 'An unexpected error occurred';

  const errorStack = typeof error === 'object' && error?.stack 
    ? error.stack 
    : null;

  return (
    <div className="error-state">
      <div className="error-state__content">
        <div className="error-state__icon">
          <WarningAlt size={64} />
        </div>
        
        <h3 className="error-state__title">Something went wrong</h3>
        
        <p className="error-state__message">{errorMessage}</p>
        
        {onRetry && (
          <Button
            kind="primary"
            onClick={onRetry}
            renderIcon={Renew}
            className="error-state__retry"
          >
            Try again
          </Button>
        )}
        
        {showDetails && errorStack && (
          <div className="error-state__details">
            <Accordion>
              <AccordionItem
                title="Error details"
                open={detailsExpanded}
                onHeadingClick={() => setDetailsExpanded(!detailsExpanded)}
              >
                <pre className="error-state__stack">
                  {errorStack}
                </pre>
              </AccordionItem>
            </Accordion>
          </div>
        )}
      </div>
    </div>
  );
};

ErrorState.propTypes = {
  error: PropTypes.oneOfType([
    PropTypes.instanceOf(Error),
    PropTypes.string,
  ]).isRequired,
  onRetry: PropTypes.func,
  showDetails: PropTypes.bool,
};

export default ErrorState;

// Made with Bob
