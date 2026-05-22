import { useState } from 'react';
import PropTypes from 'prop-types';
import { Button, Accordion, AccordionItem } from '@carbon/react';
import { WarningAlt, Renew, Video } from '@carbon/icons-react';
import './ErrorState.scss';

/**
 * ErrorState Component
 * Provides consistent error handling and display across the application
 *
 * @param {Object} props
 * @param {Error|string} props.error - Error object or error message
 * @param {Function} props.onRetry - Retry button click handler
 * @param {boolean} props.showDetails - Whether to show error details
 * @param {string} props.demoVideoUrl - URL to demonstration video (optional)
 */
const ErrorState = ({
  error,
  onRetry,
  showDetails = false,
  demoVideoUrl = '#demo-video',
}) => {
  const [detailsExpanded, setDetailsExpanded] = useState(false);

  const errorMessage = typeof error === 'string'
    ? error
    : error?.message || 'An unexpected error occurred';

  const errorStack = typeof error === 'object' && error?.stack
    ? error.stack
    : null;

  // Check if this is a network/API/backend error
  const isBackendError =
    errorMessage.toLowerCase().includes('network') ||
    errorMessage.toLowerCase().includes('api') ||
    errorMessage.toLowerCase().includes('backend') ||
    errorMessage.toLowerCase().includes('could not load') ||
    errorMessage.toLowerCase().includes('failed to fetch') ||
    errorMessage.toLowerCase().includes('connection') ||
    (error?.response?.status >= 500);

  return (
    <div className="error-state">
      <div className="error-state__content">
        <div className={`error-state__icon ${isBackendError ? 'error-state__icon--info' : ''}`}>
          <WarningAlt size={64} />
        </div>
        
        {isBackendError ? (
          <>
            <h3 className="error-state__title">Service Coming Soon!</h3>
            
            <p className="error-state__message error-state__message--friendly">
              Our service is not live right now but will be live soon!
            </p>
            
            <p className="error-state__message error-state__message--secondary">
              For now, please refer to our demonstration video to see IBM Dexter in action.
            </p>
            
            <Button
              kind="primary"
              onClick={() => window.open(demoVideoUrl, '_blank')}
              renderIcon={Video}
              className="error-state__demo-button"
            >
              Watch Demo Video
            </Button>
            
            {onRetry && (
              <Button
                kind="tertiary"
                onClick={onRetry}
                renderIcon={Renew}
                className="error-state__retry"
              >
                Try again
              </Button>
            )}
          </>
        ) : (
          <>
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
          </>
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
  demoVideoUrl: PropTypes.string,
};

export default ErrorState;

// Made with Bob
