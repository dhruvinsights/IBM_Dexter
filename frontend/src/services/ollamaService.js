/**
 * Ollama Service - Direct client-side integration with local Ollama instance
 * This service enables free, local LLM usage without backend API calls
 */

class OllamaService {
  constructor(baseUrl = 'http://localhost:11434') {
    this.baseUrl = baseUrl;
  }

  /**
   * Chat with Ollama model
   * @param {Array} messages - Array of message objects with role and content
   * @param {string} model - Model name (default: llama2)
   * @param {Object} options - Additional options (temperature, stream, etc.)
   * @returns {Promise<Object>} Response from Ollama
   */
  async chat(messages, model = 'llama2', options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          messages,
          stream: options.stream || false,
          options: {
            temperature: options.temperature || 0.7,
            top_p: options.top_p || 0.9,
            top_k: options.top_k || 40,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434');
      }
      throw error;
    }
  }

  /**
   * Generate completion (non-chat mode)
   * @param {string} prompt - The prompt text
   * @param {string} model - Model name
   * @param {Object} options - Additional options
   * @returns {Promise<Object>} Response from Ollama
   */
  async generate(prompt, model = 'llama2', options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model,
          prompt,
          stream: options.stream || false,
          options: {
            temperature: options.temperature || 0.7,
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434');
      }
      throw error;
    }
  }

  /**
   * List available models
   * @returns {Promise<Array>} Array of available models
   */
  async listModels() {
    try {
      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data.models || [];
    } catch (error) {
      if (error.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434');
      }
      throw error;
    }
  }

  /**
   * Check if Ollama is running and accessible
   * @returns {Promise<Object>} Connection status and version info
   */
  async checkConnection() {
    try {
      const response = await fetch(`${this.baseUrl}/api/version`, {
        method: 'GET',
      });

      if (!response.ok) {
        return {
          connected: false,
          error: `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      return {
        connected: true,
        version: data.version || 'unknown',
      };
    } catch (error) {
      return {
        connected: false,
        error: error.message.includes('Failed to fetch')
          ? 'Ollama is not running. Please start Ollama and try again.'
          : error.message,
      };
    }
  }

  /**
   * Pull a model from Ollama library
   * @param {string} modelName - Name of the model to pull
   * @returns {Promise<Object>} Pull status
   */
  async pullModel(modelName) {
    try {
      const response = await fetch(`${this.baseUrl}/api/pull`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: modelName,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to pull model: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to pull model: ${error.message}`);
    }
  }

  /**
   * Delete a model
   * @param {string} modelName - Name of the model to delete
   * @returns {Promise<Object>} Delete status
   */
  async deleteModel(modelName) {
    try {
      const response = await fetch(`${this.baseUrl}/api/delete`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: modelName,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to delete model: ${response.status} ${response.statusText}`);
      }

      return { success: true };
    } catch (error) {
      throw new Error(`Failed to delete model: ${error.message}`);
    }
  }

  /**
   * Get model information
   * @param {string} modelName - Name of the model
   * @returns {Promise<Object>} Model information
   */
  async showModel(modelName) {
    try {
      const response = await fetch(`${this.baseUrl}/api/show`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: modelName,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to get model info: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(`Failed to get model info: ${error.message}`);
    }
  }
}

// Export singleton instance
export const ollamaService = new OllamaService();

// Export class for custom instances
export default OllamaService;

// Made with Bob