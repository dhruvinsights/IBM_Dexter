/**
 * Cloud Provider Settings Component
 * Configuration for paid cloud LLM providers (OpenAI, Watsonx, Anthropic)
 */

import { useState } from 'react';
import {
  TextInput,
  Button,
  Select,
  SelectItem,
  InlineNotification,
  Tag,
  PasswordInput,
  Accordion,
  AccordionItem,
} from '@carbon/react';
import {
  Locked,
  Unlocked,
  Save,
  TrashCan,
  Information,
} from '@carbon/icons-react';
import useLLMStore from '../../store/useLLMStore';
import { PROVIDER_INFO, LLM_PROVIDERS } from '../../services/llmService';
import './CloudProviderSettings.scss';

const CloudProviderSettings = ({ provider }) => {
  const {
    model,
    setModel,
    apiKeys,
    setApiKey,
    clearApiKey,
    usage,
    availableModels,
  } = useLLMStore();

  const [apiKeyInput, setApiKeyInput] = useState('');
  const [showApiKey, setShowApiKey] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);

  const providerInfo = PROVIDER_INFO[provider];
  const hasApiKey = !!apiKeys[provider];

  const handleSaveApiKey = () => {
    if (!apiKeyInput.trim()) {
      setSaveStatus({ type: 'error', message: 'API key cannot be empty' });
      return;
    }

    setApiKey(provider, apiKeyInput.trim());
    setSaveStatus({ type: 'success', message: 'API key saved successfully' });
    setApiKeyInput('');
    
    // Clear status after 3 seconds
    setTimeout(() => setSaveStatus(null), 3000);
  };

  const handleClearApiKey = () => {
    clearApiKey(provider);
    setApiKeyInput('');
    setSaveStatus({ type: 'info', message: 'API key cleared' });
    setTimeout(() => setSaveStatus(null), 3000);
  };

  const getProviderInstructions = () => {
    switch (provider) {
      case LLM_PROVIDERS.OPENAI:
        return {
          title: 'OpenAI API Key',
          steps: [
            'Go to https://platform.openai.com/api-keys',
            'Sign in or create an account',
            'Click "Create new secret key"',
            'Copy the key and paste it below',
          ],
          link: 'https://platform.openai.com/api-keys',
        };
      case LLM_PROVIDERS.WATSONX:
        return {
          title: 'IBM Watsonx API Key',
          steps: [
            'Go to IBM Cloud console',
            'Navigate to Watsonx.ai service',
            'Generate API key from IAM',
            'Copy the key and paste it below',
          ],
          link: 'https://cloud.ibm.com/iam/apikeys',
        };
      case LLM_PROVIDERS.ANTHROPIC:
        return {
          title: 'Anthropic API Key',
          steps: [
            'Go to https://console.anthropic.com/settings/keys',
            'Sign in or create an account',
            'Click "Create Key"',
            'Copy the key and paste it below',
          ],
          link: 'https://console.anthropic.com/settings/keys',
        };
      default:
        return null;
    }
  };

  const instructions = getProviderInstructions();

  return (
    <div className="cloud-provider-settings">
      <div className="cloud-provider-settings__header">
        <div className="provider-info">
          <h4>
            {providerInfo.icon} {providerInfo.name}
          </h4>
          <p className="provider-description">{providerInfo.description}</p>
        </div>
        <Tag type={hasApiKey ? 'green' : 'red'} size="sm" renderIcon={hasApiKey ? Locked : Unlocked}>
          {hasApiKey ? 'Configured' : 'Not Configured'}
        </Tag>
      </div>

      {/* API Key Configuration */}
      <div className="cloud-provider-settings__api-key">
        <h5>API Key Configuration</h5>
        
        {saveStatus && (
          <InlineNotification
            kind={saveStatus.type}
            title={saveStatus.message}
            hideCloseButton
            lowContrast
            className="save-status"
          />
        )}

        {hasApiKey ? (
          <div className="api-key-status">
            <InlineNotification
              kind="success"
              title="API Key Configured"
              subtitle="Your API key is securely stored"
              hideCloseButton
              lowContrast
            />
            <div className="api-key-actions">
              <Button
                kind="danger--tertiary"
                size="sm"
                renderIcon={TrashCan}
                onClick={handleClearApiKey}
              >
                Clear API Key
              </Button>
            </div>
          </div>
        ) : (
          <div className="api-key-input">
            <PasswordInput
              id={`${provider}-api-key`}
              labelText="API Key"
              placeholder="Enter your API key"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              showPasswordLabel="Show key"
              hidePasswordLabel="Hide key"
            />
            <Button
              kind="primary"
              size="sm"
              renderIcon={Save}
              onClick={handleSaveApiKey}
              disabled={!apiKeyInput.trim()}
            >
              Save API Key
            </Button>
          </div>
        )}
      </div>

      {/* Instructions */}
      {instructions && !hasApiKey && (
        <Accordion>
          <AccordionItem title="How to get an API key">
            <div className="api-key-instructions">
              <ol>
                {instructions.steps.map((step, index) => (
                  <li key={index}>{step}</li>
                ))}
              </ol>
              <Button
                kind="tertiary"
                size="sm"
                onClick={() => window.open(instructions.link, '_blank')}
              >
                Open {providerInfo.name} Console
              </Button>
            </div>
          </AccordionItem>
        </Accordion>
      )}

      {/* Model Selection */}
      {hasApiKey && (
        <div className="cloud-provider-settings__model-select">
          <Select
            id={`${provider}-model-select`}
            labelText="Select Model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            {providerInfo.models.map((modelName) => (
              <SelectItem key={modelName} value={modelName} text={modelName} />
            ))}
          </Select>
        </div>
      )}

      {/* Usage Statistics */}
      {hasApiKey && usage.totalRequests > 0 && (
        <div className="cloud-provider-settings__usage">
          <h5>Usage Statistics</h5>
          <div className="usage-stats">
            <div className="stat">
              <span className="stat-label">Total Requests</span>
              <span className="stat-value">{usage.totalRequests.toLocaleString()}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Total Tokens</span>
              <span className="stat-value">{usage.totalTokens.toLocaleString()}</span>
            </div>
            {usage.lastUsed && (
              <div className="stat">
                <span className="stat-label">Last Used</span>
                <span className="stat-value">
                  {new Date(usage.lastUsed).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Important Notes */}
      <div className="cloud-provider-settings__notes">
        <div className="note-header">
          <Information size={20} />
          <h5>Important Notes</h5>
        </div>
        <ul>
          <li>API keys are stored securely and never shared</li>
          <li>You will be charged by {providerInfo.name} based on usage</li>
          <li>Monitor your usage in the {providerInfo.name} console</li>
          <li>Set spending limits in your {providerInfo.name} account</li>
        </ul>
      </div>
    </div>
  );
};

export default CloudProviderSettings;

// Made with Bob