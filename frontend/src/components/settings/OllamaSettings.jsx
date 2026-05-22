/**
 * Ollama Settings Component
 * Configuration and status for local Ollama LLM provider
 */

import { useState, useEffect } from 'react';
import {
  Button,
  Select,
  SelectItem,
  InlineNotification,
  Tag,
  Link,
  SkeletonText,
} from '@carbon/react';
import {
  Checkmark,
  WarningAlt,
  Renew,
  Download,
  Launch,
} from '@carbon/icons-react';
import useLLMStore from '../../store/useLLMStore';
import './OllamaSettings.scss';

const OllamaSettings = () => {
  const {
    model,
    setModel,
    ollamaConnected,
    connectionChecking,
    lastConnectionCheck,
    availableModels,
    modelsLoading,
    checkOllamaConnection,
    loadModels,
  } = useLLMStore();

  const [testingConnection, setTestingConnection] = useState(false);

  useEffect(() => {
    // Check connection on mount
    checkOllamaConnection();
  }, [checkOllamaConnection]);

  const handleTestConnection = async () => {
    setTestingConnection(true);
    await checkOllamaConnection();
    setTestingConnection(false);
  };

  const handleRefreshModels = async () => {
    await loadModels();
  };

  const getConnectionStatus = () => {
    if (connectionChecking || testingConnection) {
      return {
        type: 'info',
        title: 'Checking connection...',
        subtitle: 'Please wait',
        icon: Renew,
      };
    }

    if (ollamaConnected) {
      return {
        type: 'success',
        title: 'Connected to Ollama',
        subtitle: lastConnectionCheck
          ? `Last checked: ${new Date(lastConnectionCheck).toLocaleTimeString()}`
          : 'Connection active',
        icon: Checkmark,
      };
    }

    return {
      type: 'error',
      title: 'Cannot connect to Ollama',
      subtitle: 'Please ensure Ollama is running on localhost:11434',
      icon: WarningAlt,
    };
  };

  const status = getConnectionStatus();

  return (
    <div className="ollama-settings">
      <div className="ollama-settings__header">
        <h4>Ollama Configuration</h4>
        <Tag type={ollamaConnected ? 'green' : 'red'} size="sm">
          {ollamaConnected ? 'Connected' : 'Disconnected'}
        </Tag>
      </div>

      {/* Connection Status */}
      <div className="ollama-settings__status">
        <InlineNotification
          kind={status.type}
          title={status.title}
          subtitle={status.subtitle}
          hideCloseButton
          lowContrast
        />
      </div>

      {/* Connection Actions */}
      <div className="ollama-settings__actions">
        <Button
          kind="tertiary"
          size="sm"
          renderIcon={Renew}
          onClick={handleTestConnection}
          disabled={testingConnection || connectionChecking}
        >
          Test Connection
        </Button>
        <Button
          kind="tertiary"
          size="sm"
          renderIcon={Download}
          onClick={handleRefreshModels}
          disabled={!ollamaConnected || modelsLoading}
        >
          Refresh Models
        </Button>
      </div>

      {/* Model Selection */}
      {ollamaConnected && (
        <div className="ollama-settings__model-select">
          <Select
            id="ollama-model-select"
            labelText="Select Model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            disabled={modelsLoading}
          >
            {modelsLoading ? (
              <SelectItem value="" text="Loading models..." />
            ) : availableModels.length > 0 ? (
              availableModels.map((m) => (
                <SelectItem
                  key={m.id}
                  value={m.id}
                  text={`${m.name}${m.size ? ` (${formatSize(m.size)})` : ''}`}
                />
              ))
            ) : (
              <SelectItem value="" text="No models available" />
            )}
          </Select>
          {modelsLoading && <SkeletonText className="model-loading-skeleton" />}
        </div>
      )}

      {/* Model Info */}
      {ollamaConnected && availableModels.length > 0 && (
        <div className="ollama-settings__model-info">
          <p className="model-count">
            {availableModels.length} model{availableModels.length !== 1 ? 's' : ''} available
          </p>
        </div>
      )}

      {/* Installation Guide */}
      {!ollamaConnected && (
        <div className="ollama-settings__install-guide">
          <h5>Getting Started with Ollama</h5>
          <ol>
            <li>
              Download Ollama from{' '}
              <Link
                href="https://ollama.ai/download"
                target="_blank"
                rel="noopener noreferrer"
                renderIcon={Launch}
              >
                ollama.ai/download
              </Link>
            </li>
            <li>Install and start Ollama on your machine</li>
            <li>
              Pull a model: <code>ollama pull llama2</code>
            </li>
            <li>Click "Test Connection" above to verify</li>
          </ol>
          <Button
            kind="primary"
            size="sm"
            renderIcon={Launch}
            onClick={() => window.open('https://ollama.ai/download', '_blank')}
          >
            Download Ollama
          </Button>
        </div>
      )}

      {/* Quick Tips */}
      <div className="ollama-settings__tips">
        <h5>💡 Tips</h5>
        <ul>
          <li>Ollama runs completely on your machine - no data leaves your computer</li>
          <li>Recommended models: llama2, mistral, codellama for code review</li>
          <li>Larger models provide better results but require more RAM</li>
          <li>Keep Ollama running in the background for best experience</li>
        </ul>
      </div>
    </div>
  );
};

// Helper function to format file size
const formatSize = (bytes) => {
  if (!bytes) return '';
  const gb = bytes / (1024 * 1024 * 1024);
  if (gb >= 1) return `${gb.toFixed(1)}GB`;
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(0)}MB`;
};

export default OllamaSettings;

// Made with Bob