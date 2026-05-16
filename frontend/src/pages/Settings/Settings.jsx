import {
  Grid,
  Column,
  Tile,
  Form,
  FormGroup,
  TextInput,
  Toggle,
  Button,
  Select,
  SelectItem,
} from '@carbon/react';
import { Save } from '@carbon/icons-react';
import './Settings.scss';

const Settings = () => {
  return (
    <div className="settings">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Manage your preferences and integrations</p>
      </div>

      <Grid narrow>
        <Column sm={4} md={8} lg={10}>
          <Tile className="settings-tile">
            <h3>User Preferences</h3>
            <Form>
              <FormGroup legendText="">
                <TextInput
                  id="username"
                  labelText="Username"
                  placeholder="Enter your username"
                  defaultValue="developer@ibm.com"
                />
                
                <TextInput
                  id="email"
                  labelText="Email"
                  type="email"
                  placeholder="Enter your email"
                  defaultValue="developer@ibm.com"
                />
                
                <Select
                  id="language"
                  labelText="Language"
                  defaultValue="en"
                >
                  <SelectItem value="en" text="English" />
                  <SelectItem value="es" text="Spanish" />
                  <SelectItem value="fr" text="French" />
                  <SelectItem value="de" text="German" />
                </Select>
              </FormGroup>
            </Form>
          </Tile>

          <Tile className="settings-tile">
            <h3>Notification Settings</h3>
            <Form>
              <FormGroup legendText="">
                <Toggle
                  id="email-notifications"
                  labelText="Email Notifications"
                  labelA="Off"
                  labelB="On"
                  defaultToggled
                />
                
                <Toggle
                  id="review-notifications"
                  labelText="Review Completion Notifications"
                  labelA="Off"
                  labelB="On"
                  defaultToggled
                />
                
                <Toggle
                  id="security-alerts"
                  labelText="Security Alert Notifications"
                  labelA="Off"
                  labelB="On"
                  defaultToggled
                />
                
                <Toggle
                  id="weekly-summary"
                  labelText="Weekly Summary Email"
                  labelA="Off"
                  labelB="On"
                />
              </FormGroup>
            </Form>
          </Tile>

          <Tile className="settings-tile">
            <h3>Integration Settings</h3>
            <Form>
              <FormGroup legendText="">
                <TextInput
                  id="github-token"
                  labelText="GitHub Personal Access Token"
                  type="password"
                  placeholder="ghp_xxxxxxxxxxxx"
                  helperText="Required for GitHub integration"
                />
                
                <TextInput
                  id="gitlab-token"
                  labelText="GitLab Personal Access Token"
                  type="password"
                  placeholder="glpat-xxxxxxxxxxxx"
                  helperText="Required for GitLab integration"
                />
                
                <Select
                  id="default-platform"
                  labelText="Default Platform"
                  defaultValue="github"
                >
                  <SelectItem value="github" text="GitHub" />
                  <SelectItem value="gitlab" text="GitLab" />
                </Select>
              </FormGroup>
            </Form>
          </Tile>

          <div className="settings-actions">
            <Button
              kind="primary"
              renderIcon={Save}
              className="animated-button"
            >
              Save Settings
            </Button>
            <Button kind="secondary">
              Reset to Defaults
            </Button>
          </div>
        </Column>
      </Grid>
    </div>
  );
};

export default Settings;

// Made with Bob
