/**
 * LLM Store - Zustand state management for LLM provider settings
 * Persists user's LLM provider preferences and connection status
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { llmService, LLM_PROVIDERS } from '../services/llmService';

const useLLMStore = create(
  persist(
    (set, get) => ({
      // Current provider and model
      provider: LLM_PROVIDERS.OLLAMA, // Default to free tier
      model: 'llama2',
      
      // Connection status
      ollamaConnected: false,
      connectionChecking: false,
      lastConnectionCheck: null,
      
      // Available models for current provider
      availableModels: [],
      modelsLoading: false,
      
      // API keys for cloud providers (encrypted in backend)
      apiKeys: {
        [LLM_PROVIDERS.OPENAI]: null,
        [LLM_PROVIDERS.WATSONX]: null,
        [LLM_PROVIDERS.ANTHROPIC]: null,
      },
      
      // Usage statistics
      usage: {
        totalRequests: 0,
        totalTokens: 0,
        lastUsed: null,
      },

      /**
       * Set the active LLM provider
       */
      setProvider: (provider) => {
        set({ provider });
        llmService.setProvider(provider);
        
        // Load models for new provider
        get().loadModels();
        
        // Check connection for new provider
        if (provider === LLM_PROVIDERS.OLLAMA) {
          get().checkOllamaConnection();
        }
      },

      /**
       * Set the active model
       */
      setModel: (model) => {
        set({ model });
        llmService.setModel(model);
      },

      /**
       * Check Ollama connection status
       */
      checkOllamaConnection: async () => {
        set({ connectionChecking: true });
        
        try {
          const status = await llmService.ollamaService.checkConnection();
          set({
            ollamaConnected: status.connected,
            connectionChecking: false,
            lastConnectionCheck: new Date().toISOString(),
          });
          
          // If connected, load available models
          if (status.connected) {
            get().loadModels();
          }
          
          return status;
        } catch (error) {
          set({
            ollamaConnected: false,
            connectionChecking: false,
            lastConnectionCheck: new Date().toISOString(),
          });
          return { connected: false, error: error.message };
        }
      },

      /**
       * Load available models for current provider
       */
      loadModels: async () => {
        set({ modelsLoading: true });
        
        try {
          const models = await llmService.listModels();
          set({
            availableModels: models,
            modelsLoading: false,
          });
          
          // If current model is not in available models, set to first available
          const currentModel = get().model;
          const modelExists = models.some(m => m.id === currentModel);
          
          if (!modelExists && models.length > 0) {
            get().setModel(models[0].id);
          }
        } catch (error) {
          console.error('Failed to load models:', error);
          set({
            availableModels: [],
            modelsLoading: false,
          });
        }
      },

      /**
       * Set API key for a cloud provider
       */
      setApiKey: (provider, apiKey) => {
        set((state) => ({
          apiKeys: {
            ...state.apiKeys,
            [provider]: apiKey,
          },
        }));
      },

      /**
       * Clear API key for a provider
       */
      clearApiKey: (provider) => {
        set((state) => ({
          apiKeys: {
            ...state.apiKeys,
            [provider]: null,
          },
        }));
      },

      /**
       * Check if current provider has API key configured
       */
      hasApiKey: () => {
        const { provider, apiKeys } = get();
        if (provider === LLM_PROVIDERS.OLLAMA) {
          return true; // Ollama doesn't need API key
        }
        return !!apiKeys[provider];
      },

      /**
       * Update usage statistics
       */
      updateUsage: (tokens) => {
        set((state) => ({
          usage: {
            totalRequests: state.usage.totalRequests + 1,
            totalTokens: state.usage.totalTokens + tokens,
            lastUsed: new Date().toISOString(),
          },
        }));
      },

      /**
       * Reset usage statistics
       */
      resetUsage: () => {
        set({
          usage: {
            totalRequests: 0,
            totalTokens: 0,
            lastUsed: null,
          },
        });
      },

      /**
       * Get provider info
       */
      getProviderInfo: () => {
        const { provider } = get();
        return llmService.getProviderInfo(provider);
      },

      /**
       * Check if provider requires backend
       */
      requiresBackend: () => {
        const { provider } = get();
        return provider !== LLM_PROVIDERS.OLLAMA;
      },

      /**
       * Initialize store (check connection, load models)
       */
      initialize: async () => {
        const { provider } = get();
        
        // Set provider in service
        llmService.setProvider(provider);
        llmService.setModel(get().model);
        
        // Check connection if Ollama
        if (provider === LLM_PROVIDERS.OLLAMA) {
          await get().checkOllamaConnection();
        }
        
        // Load models
        await get().loadModels();
      },

      /**
       * Start auto-check for Ollama connection (every 30 seconds)
       */
      startAutoCheck: () => {
        const { provider } = get();
        
        if (provider === LLM_PROVIDERS.OLLAMA) {
          // Check immediately
          get().checkOllamaConnection();
          
          // Set up interval
          const intervalId = setInterval(() => {
            const currentProvider = get().provider;
            if (currentProvider === LLM_PROVIDERS.OLLAMA) {
              get().checkOllamaConnection();
            } else {
              // Stop checking if provider changed
              clearInterval(intervalId);
            }
          }, 30000); // 30 seconds
          
          return intervalId;
        }
        
        return null;
      },
    }),
    {
      name: 'dexter-llm-settings',
      // Don't persist connection status and loading states
      partialize: (state) => ({
        provider: state.provider,
        model: state.model,
        apiKeys: state.apiKeys,
        usage: state.usage,
      }),
    }
  )
);

export default useLLMStore;

// Made with Bob