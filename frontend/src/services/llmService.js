/**
 * Unified LLM Service - Routes requests to Ollama (free) or backend cloud providers (paid)
 * This service abstracts the LLM provider selection and provides a consistent interface
 */

import { ollamaService } from './ollamaService';
import api from './api';

// LLM Provider types
export const LLM_PROVIDERS = {
  OLLAMA: 'ollama',
  OPENAI: 'openai',
  WATSONX: 'watsonx',
  ANTHROPIC: 'anthropic',
};

// Provider metadata
export const PROVIDER_INFO = {
  [LLM_PROVIDERS.OLLAMA]: {
    name: 'Ollama',
    description: 'Free local LLM - Requires Ollama installed',
    icon: '🆓',
    tier: 'free',
    requiresBackend: false,
    requiresApiKey: false,
    models: ['llama2', 'llama3', 'mistral', 'codellama', 'phi', 'neural-chat'],
  },
  [LLM_PROVIDERS.OPENAI]: {
    name: 'OpenAI',
    description: 'GPT-4, GPT-3.5 - Requires API key',
    icon: '💰',
    tier: 'paid',
    requiresBackend: true,
    requiresApiKey: true,
    models: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  },
  [LLM_PROVIDERS.WATSONX]: {
    name: 'IBM Watsonx',
    description: 'Enterprise AI - Requires API key',
    icon: '💰',
    tier: 'paid',
    requiresBackend: true,
    requiresApiKey: true,
    models: ['granite-13b-chat', 'granite-20b-code', 'llama-2-70b-chat'],
  },
  [LLM_PROVIDERS.ANTHROPIC]: {
    name: 'Anthropic Claude',
    description: 'Claude 3 - Requires API key',
    icon: '💰',
    tier: 'paid',
    requiresBackend: true,
    requiresApiKey: true,
    models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
  },
};

class LLMService {
  constructor() {
    this.provider = LLM_PROVIDERS.OLLAMA; // Default to free tier
    this.model = 'llama2';
    this.ollamaService = ollamaService;
  }

  /**
   * Set the active LLM provider
   * @param {string} provider - Provider name from LLM_PROVIDERS
   */
  setProvider(provider) {
    if (!Object.values(LLM_PROVIDERS).includes(provider)) {
      throw new Error(`Invalid provider: ${provider}`);
    }
    this.provider = provider;
  }

  /**
   * Set the active model
   * @param {string} model - Model name
   */
  setModel(model) {
    this.model = model;
  }

  /**
   * Get current provider
   * @returns {string} Current provider
   */
  getProvider() {
    return this.provider;
  }

  /**
   * Get current model
   * @returns {string} Current model
   */
  getModel() {
    return this.model;
  }

  /**
   * Check if current provider requires backend
   * @returns {boolean} True if backend is required
   */
  requiresBackend() {
    return PROVIDER_INFO[this.provider]?.requiresBackend || false;
  }

  /**
   * Chat with the active LLM provider
   * @param {Array} messages - Array of message objects
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} LLM response
   */
  async chat(messages, options = {}) {
    const model = options.model || this.model;
    
    if (this.provider === LLM_PROVIDERS.OLLAMA) {
      return this.chatWithOllama(messages, model, options);
    } else {
      return this.chatWithBackend(messages, model, options);
    }
  }

  /**
   * Chat with Ollama (client-side)
   * @private
   */
  async chatWithOllama(messages, model, options) {
    try {
      const response = await this.ollamaService.chat(messages, model, options);
      
      return {
        provider: LLM_PROVIDERS.OLLAMA,
        model,
        content: response.message?.content || response.response || '',
        usage: {
          prompt_tokens: response.prompt_eval_count || 0,
          completion_tokens: response.eval_count || 0,
          total_tokens: (response.prompt_eval_count || 0) + (response.eval_count || 0),
        },
        raw: response,
      };
    } catch (error) {
      throw new Error(`Ollama chat failed: ${error.message}`);
    }
  }

  /**
   * Chat with cloud provider via backend
   * @private
   */
  async chatWithBackend(messages, model, options) {
    try {
      const response = await api.post('/llm/chat', {
        provider: this.provider,
        model,
        messages,
        options,
      });

      return {
        provider: this.provider,
        model,
        content: response.data.content || '',
        usage: response.data.usage || {},
        raw: response.data,
      };
    } catch (error) {
      if (error.response?.status === 401) {
        throw new Error('API key not configured. Please add your API key in settings.');
      }
      if (error.response?.status === 402) {
        throw new Error('Insufficient credits. Please upgrade your plan.');
      }
      throw new Error(`Backend LLM chat failed: ${error.message}`);
    }
  }

  /**
   * Generate code review using active provider
   * @param {string} code - Code to review
   * @param {Object} context - Additional context
   * @returns {Promise<Object>} Review result
   */
  async reviewCode(code, context = {}) {
    const messages = [
      {
        role: 'system',
        content: 'You are an expert code reviewer. Analyze the code and provide detailed feedback on quality, security, performance, and best practices.',
      },
      {
        role: 'user',
        content: `Please review the following code:\n\n${code}\n\nContext: ${JSON.stringify(context)}`,
      },
    ];

    return this.chat(messages, { temperature: 0.3 });
  }

  /**
   * List available models for current provider
   * @returns {Promise<Array>} Array of available models
   */
  async listModels() {
    if (this.provider === LLM_PROVIDERS.OLLAMA) {
      try {
        const models = await this.ollamaService.listModels();
        return models.map(m => ({
          id: m.name,
          name: m.name,
          size: m.size,
          modified: m.modified_at,
        }));
      } catch (error) {
        // Return default models if Ollama is not running
        return PROVIDER_INFO[LLM_PROVIDERS.OLLAMA].models.map(name => ({
          id: name,
          name,
          available: false,
        }));
      }
    } else {
      // Return predefined models for cloud providers
      return PROVIDER_INFO[this.provider].models.map(name => ({
        id: name,
        name,
        available: true,
      }));
    }
  }

  /**
   * Check connection status for current provider
   * @returns {Promise<Object>} Connection status
   */
  async checkConnection() {
    if (this.provider === LLM_PROVIDERS.OLLAMA) {
      return this.ollamaService.checkConnection();
    } else {
      try {
        const response = await api.get(`/llm/status?provider=${this.provider}`);
        return {
          connected: response.data.connected || false,
          message: response.data.message,
        };
      } catch (error) {
        return {
          connected: false,
          error: error.message,
        };
      }
    }
  }

  /**
   * Get provider information
   * @param {string} provider - Provider name (optional, defaults to current)
   * @returns {Object} Provider information
   */
  getProviderInfo(provider = null) {
    const targetProvider = provider || this.provider;
    return PROVIDER_INFO[targetProvider] || null;
  }

  /**
   * Check if provider is available
   * @param {string} provider - Provider name
   * @returns {Promise<boolean>} True if available
   */
  async isProviderAvailable(provider) {
    const originalProvider = this.provider;
    this.setProvider(provider);
    
    try {
      const status = await this.checkConnection();
      return status.connected === true;
    } catch (error) {
      return false;
    } finally {
      this.setProvider(originalProvider);
    }
  }
}

// Export singleton instance
export const llmService = new LLMService();

// Export class for custom instances
export default LLMService;

// Made with Bob