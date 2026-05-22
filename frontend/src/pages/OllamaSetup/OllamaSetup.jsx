/**
 * Ollama Setup Guide Page
 * Step-by-step instructions for installing and configuring Ollama
 */

import { useState } from 'react';
import {
  Grid,
  Column,
  Tile,
  Button,
  Accordion,
  AccordionItem,
  InlineNotification,
  CodeSnippet,
  OrderedList,
  ListItem,
  UnorderedList,
  Tag,
} from '@carbon/react';
import {
  Download,
  Launch,
  Checkmark,
  Terminal,
  MachineLearningModel,
} from '@carbon/icons-react';
import { useNavigate } from 'react-router-dom';
import useLLMStore from '../../store/useLLMStore';
import './OllamaSetup.scss';

const OllamaSetup = () => {
  const navigate = useNavigate();
  const { checkOllamaConnection, ollamaConnected } = useLLMStore();
  const [checking, setChecking] = useState(false);

  const handleCheckConnection = async () => {
    setChecking(true);
    await checkOllamaConnection();
    setChecking(false);
  };

  const handleGoToSettings = () => {
    navigate('/settings');
  };

  return (
    <div className="ollama-setup-page">
      <div className="page-header">
        <div className="page-header__title">
          <MachineLearningModel size={32} />
          <h1>Ollama Setup Guide</h1>
        </div>
        <p className="page-header__description">
          Get started with free, local AI using Ollama
        </p>
      </div>

      <Grid className="setup-grid" narrow>
        <Column lg={12} md={8} sm={4}>
          {/* Connection Status */}
          {ollamaConnected && (
            <InlineNotification
              kind="success"
              title="Ollama is connected!"
              subtitle="You're all set. You can now use Ollama for code reviews."
              lowContrast
              actions={
                <Button kind="tertiary" size="sm" onClick={handleGoToSettings}>
                  Go to Settings
                </Button>
              }
            />
          )}

          {/* What is Ollama */}
          <Tile className="setup-tile">
            <h2>What is Ollama?</h2>
            <p>
              Ollama is a free, open-source tool that lets you run large language models (LLMs)
              locally on your computer. With Ollama, you can:
            </p>
            <UnorderedList>
              <ListItem>Run AI models completely offline</ListItem>
              <ListItem>Keep your code and data private (nothing leaves your machine)</ListItem>
              <ListItem>Avoid API costs and usage limits</ListItem>
              <ListItem>Use powerful models like Llama 2, Mistral, and CodeLlama</ListItem>
            </UnorderedList>
          </Tile>

          {/* Installation Steps */}
          <Tile className="setup-tile">
            <h2>Installation Steps</h2>
            
            <Accordion>
              {/* Step 1: Download */}
              <AccordionItem title="Step 1: Download Ollama">
                <div className="step-content">
                  <p>Download Ollama for your operating system:</p>
                  <div className="download-buttons">
                    <Button
                      kind="primary"
                      renderIcon={Download}
                      onClick={() => window.open('https://ollama.ai/download/mac', '_blank')}
                    >
                      Download for macOS
                    </Button>
                    <Button
                      kind="primary"
                      renderIcon={Download}
                      onClick={() => window.open('https://ollama.ai/download/windows', '_blank')}
                    >
                      Download for Windows
                    </Button>
                    <Button
                      kind="primary"
                      renderIcon={Download}
                      onClick={() => window.open('https://ollama.ai/download/linux', '_blank')}
                    >
                      Download for Linux
                    </Button>
                  </div>
                  <p className="step-note">
                    <strong>System Requirements:</strong> 8GB RAM minimum, 16GB+ recommended for larger models
                  </p>
                </div>
              </AccordionItem>

              {/* Step 2: Install */}
              <AccordionItem title="Step 2: Install Ollama">
                <div className="step-content">
                  <h4>macOS</h4>
                  <OrderedList>
                    <ListItem>Open the downloaded .dmg file</ListItem>
                    <ListItem>Drag Ollama to your Applications folder</ListItem>
                    <ListItem>Launch Ollama from Applications</ListItem>
                    <ListItem>Ollama will run in the menu bar</ListItem>
                  </OrderedList>

                  <h4>Windows</h4>
                  <OrderedList>
                    <ListItem>Run the downloaded installer</ListItem>
                    <ListItem>Follow the installation wizard</ListItem>
                    <ListItem>Ollama will start automatically</ListItem>
                    <ListItem>Look for the Ollama icon in the system tray</ListItem>
                  </OrderedList>

                  <h4>Linux</h4>
                  <p>Run the installation script:</p>
                  <CodeSnippet type="single">
                    curl -fsSL https://ollama.ai/install.sh | sh
                  </CodeSnippet>
                  <p>Or install manually:</p>
                  <CodeSnippet type="multi">
{`# Download the binary
curl -L https://ollama.ai/download/ollama-linux-amd64 -o ollama
chmod +x ollama

# Move to system path
sudo mv ollama /usr/local/bin/

# Start Ollama
ollama serve`}
                  </CodeSnippet>
                </div>
              </AccordionItem>

              {/* Step 3: Pull a Model */}
              <AccordionItem title="Step 3: Download a Model">
                <div className="step-content">
                  <p>Open your terminal and pull a model. We recommend starting with one of these:</p>
                  
                  <h4>For Code Review (Recommended)</h4>
                  <CodeSnippet type="single">ollama pull codellama</CodeSnippet>
                  <p className="model-description">
                    <Tag type="blue">7B params</Tag> Specialized for code understanding and generation
                  </p>

                  <h4>General Purpose</h4>
                  <CodeSnippet type="single">ollama pull llama2</CodeSnippet>
                  <p className="model-description">
                    <Tag type="green">7B params</Tag> Good balance of speed and quality
                  </p>

                  <CodeSnippet type="single">ollama pull mistral</CodeSnippet>
                  <p className="model-description">
                    <Tag type="purple">7B params</Tag> Fast and efficient, great for quick reviews
                  </p>

                  <h4>Advanced (Requires more RAM)</h4>
                  <CodeSnippet type="single">ollama pull llama2:13b</CodeSnippet>
                  <p className="model-description">
                    <Tag type="red">13B params</Tag> Better quality, needs 16GB+ RAM
                  </p>

                  <p className="step-note">
                    <strong>Note:</strong> Model downloads can be large (4-8GB). The first download may take several minutes.
                  </p>
                </div>
              </AccordionItem>

              {/* Step 4: Verify */}
              <AccordionItem title="Step 4: Verify Installation">
                <div className="step-content">
                  <p>Test that Ollama is running correctly:</p>
                  <CodeSnippet type="single">ollama list</CodeSnippet>
                  <p>This should show the models you've downloaded.</p>

                  <p>Try a simple chat:</p>
                  <CodeSnippet type="single">ollama run llama2 "Hello, how are you?"</CodeSnippet>

                  <div className="verify-connection">
                    <p>Or verify the connection from Dexter:</p>
                    <Button
                      kind="primary"
                      renderIcon={checking ? Terminal : Checkmark}
                      onClick={handleCheckConnection}
                      disabled={checking}
                    >
                      {checking ? 'Checking...' : 'Test Connection'}
                    </Button>
                  </div>
                </div>
              </AccordionItem>
            </Accordion>
          </Tile>

          {/* Troubleshooting */}
          <Tile className="setup-tile">
            <h2>Troubleshooting</h2>
            
            <Accordion>
              <AccordionItem title="Ollama won't start">
                <div className="step-content">
                  <UnorderedList>
                    <ListItem>
                      <strong>Check if Ollama is running:</strong> Look for the Ollama icon in your menu bar (Mac) or system tray (Windows)
                    </ListItem>
                    <ListItem>
                      <strong>Restart Ollama:</strong> Quit and relaunch the application
                    </ListItem>
                    <ListItem>
                      <strong>Check port 11434:</strong> Make sure no other application is using this port
                    </ListItem>
                    <ListItem>
                      <strong>Firewall:</strong> Ensure your firewall allows Ollama to run
                    </ListItem>
                  </UnorderedList>
                </div>
              </AccordionItem>

              <AccordionItem title="Connection refused error">
                <div className="step-content">
                  <p>If you see "Cannot connect to Ollama" errors:</p>
                  <OrderedList>
                    <ListItem>Verify Ollama is running (check system tray/menu bar)</ListItem>
                    <ListItem>Try accessing http://localhost:11434 in your browser</ListItem>
                    <ListItem>Restart Ollama</ListItem>
                    <ListItem>Check if another service is using port 11434</ListItem>
                  </OrderedList>
                </div>
              </AccordionItem>

              <AccordionItem title="Model download fails">
                <div className="step-content">
                  <UnorderedList>
                    <ListItem>
                      <strong>Check internet connection:</strong> Model downloads require a stable connection
                    </ListItem>
                    <ListItem>
                      <strong>Disk space:</strong> Ensure you have enough free space (models are 4-8GB each)
                    </ListItem>
                    <ListItem>
                      <strong>Retry:</strong> Run the pull command again if it fails
                    </ListItem>
                  </UnorderedList>
                </div>
              </AccordionItem>

              <AccordionItem title="Out of memory errors">
                <div className="step-content">
                  <p>If models crash or run slowly:</p>
                  <UnorderedList>
                    <ListItem>Use smaller models (7B instead of 13B)</ListItem>
                    <ListItem>Close other applications to free up RAM</ListItem>
                    <ListItem>Consider upgrading your RAM if you frequently use AI models</ListItem>
                  </UnorderedList>
                </div>
              </AccordionItem>
            </Accordion>
          </Tile>

          {/* Recommended Models */}
          <Tile className="setup-tile">
            <h2>Recommended Models for Code Review</h2>
            <div className="models-grid">
              <div className="model-card">
                <h4>CodeLlama</h4>
                <Tag type="blue">Best for Code</Tag>
                <p>Specialized for code understanding, generation, and review</p>
                <CodeSnippet type="single">ollama pull codellama</CodeSnippet>
              </div>
              <div className="model-card">
                <h4>Mistral</h4>
                <Tag type="purple">Fast</Tag>
                <p>Quick responses, good for rapid code reviews</p>
                <CodeSnippet type="single">ollama pull mistral</CodeSnippet>
              </div>
              <div className="model-card">
                <h4>Llama 2</h4>
                <Tag type="green">Balanced</Tag>
                <p>Good all-around performance for various tasks</p>
                <CodeSnippet type="single">ollama pull llama2</CodeSnippet>
              </div>
            </div>
          </Tile>

          {/* Next Steps */}
          <Tile className="setup-tile">
            <h2>Next Steps</h2>
            <OrderedList>
              <ListItem>
                <strong>Configure Dexter:</strong> Go to Settings → AI Configuration to select your model
              </ListItem>
              <ListItem>
                <strong>Test a Review:</strong> Try reviewing a pull request to see Ollama in action
              </ListItem>
              <ListItem>
                <strong>Explore Models:</strong> Visit{' '}
                <a href="https://ollama.ai/library" target="_blank" rel="noopener noreferrer">
                  ollama.ai/library
                </a>{' '}
                to discover more models
              </ListItem>
            </OrderedList>
            <div className="next-steps-actions">
              <Button kind="primary" onClick={handleGoToSettings}>
                Go to Settings
              </Button>
              <Button
                kind="tertiary"
                renderIcon={Launch}
                onClick={() => window.open('https://ollama.ai/library', '_blank')}
              >
                Browse Models
              </Button>
            </div>
          </Tile>
        </Column>
      </Grid>
    </div>
  );
};

export default OllamaSetup;

// Made with Bob