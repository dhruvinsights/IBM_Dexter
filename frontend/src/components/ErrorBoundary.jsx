import { Component } from 'react';
import PropTypes from 'prop-types';
import { Button } from '@carbon/react';
import { Renew, WarningAlt } from '@carbon/icons-react';
import './ErrorBoundary.scss';

/**
 * ErrorBoundary Component
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo,
    });

    // You can also log the error to an error reporting service here
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="error-boundary">
          <div className="error-boundary__content">
            <div className="error-boundary__icon">
              <WarningAlt size={64} />
            </div>
            
            <h1 className="error-boundary__title">
              {this.props.title || 'Something went wrong'}
            </h1>
            
            <p className="error-boundary__message">
              {this.props.message || 
                'An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.'}
            </p>

            {this.state.error && this.props.showDetails && (
              <details className="error-boundary__details">
                <summary>Error details</summary>
                <pre className="error-boundary__stack">
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className="error-boundary__actions">
              <Button
                kind="primary"
                renderIcon={Renew}
                onClick={this.handleReset}
              >
                Try again
              </Button>
              
              {this.props.showHomeButton && (
                <Button
                  kind="secondary"
                  onClick={() => window.location.href = '/'}
                >
                  Go to home
                </Button>
              )}
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.node,
  title: PropTypes.string,
  message: PropTypes.string,
  showDetails: PropTypes.bool,
  showHomeButton: PropTypes.bool,
  onError: PropTypes.func,
  onReset: PropTypes.func,
};

ErrorBoundary.defaultProps = {
  showDetails: import.meta.env.DEV,
  showHomeButton: true,
};

export default ErrorBoundary;

// Made with Bob
