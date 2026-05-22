/**
 * Ollama Status Indicator
 * Shows connection status in the header with auto-check functionality
 */

import { useState, useEffect } from 'react';
import { Button, Tooltip } from '@carbon/react';
import { Chip, ChipFilled, Settings } from '@carbon/icons-react';
import { useNavigate } from 'react-router-dom';
import useLLMStore from '../../store/useLLMStore';
import { LLM_PROVIDERS } from '../../services/llmService';
import './OllamaStatus.scss';

const OllamaStatus = () => {
  const navigate = useNavigate();
  const {
    provider,
    ollamaConnected,
    connectionChecking,
    checkOllamaConnection,
    startAutoCheck,
  } = useLLMStore();

  const [autoCheckInterval, setAutoCheckInterval] = useState(null);

  // Only show for Ollama provider
  const isOllamaProvider = provider === LLM_PROVIDERS.OLLAMA;

  useEffect(() => {
    if (isOllamaProvider) {
      // Start auto-check
      const intervalId = startAutoCheck();
      setAutoCheckInterval(intervalId);

      return () => {
        if (intervalId) {
          clearInterval(intervalId);
        }
      };
    } else {
      // Clear interval if provider changed
      if (autoCheckInterval) {
        clearInterval(autoCheckInterval);
        setAutoCheckInterval(null);
      }
    }
  }, [isOllamaProvider, startAutoCheck]);

  const handleClick = () => {
    navigate('/settings');
  };

  const getStatusInfo = () => {
    if (connectionChecking) {
      return {
        icon: Chip,
        color: 'checking',
        label: 'Checking...',
        tooltip: 'Checking Ollama connection',
      };
    }

    if (ollamaConnected) {
      return {
        icon: ChipFilled,
        color: 'connected',
        label: 'Ollama',
        tooltip: 'Connected to Ollama (localhost:11434)',
      };
    }

    return {
      icon: Chip,
      color: 'disconnected',
      label: 'Ollama',
      tooltip: 'Ollama not connected. Click to configure.',
    };
  };

  // Don't show if not using Ollama
  if (!isOllamaProvider) {
    return null;
  }

  const status = getStatusInfo();
  const StatusIcon = status.icon;

  return (
    <Tooltip
      align="bottom"
      label={status.tooltip}
      className="ollama-status-tooltip"
    >
      <Button
        kind="ghost"
        size="sm"
        className={`ollama-status ollama-status--${status.color}`}
        onClick={handleClick}
        hasIconOnly
        iconDescription={status.tooltip}
        renderIcon={StatusIcon}
      >
        <span className="ollama-status__label">{status.label}</span>
      </Button>
    </Tooltip>
  );
};

export default OllamaStatus;

// Made with Bob