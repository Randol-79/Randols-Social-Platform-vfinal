'use client';

import { useState } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

function SettingsSection({ title, description, children }) {
  return (
    <div className="card">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-night dark:text-cream">{title}</h3>
        {description && <p className="text-sm text-night/50 dark:text-cream/50">{description}</p>}
      </div>
      {children}
    </div>
  );
}

function Toggle({ label, description, enabled, onChange }) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-cream-dark dark:border-night last:border-0">
      <div>
        <p className="font-medium text-night dark:text-cream">{label}</p>
        {description && <p className="text-sm text-night/50 dark:text-cream/50">{description}</p>}
      </div>
      <button 
        onClick={() => onChange(!enabled)}
        className={`w-12 h-6 rounded-full transition-colors ${enabled ? 'bg-marsh' : 'bg-cream-dark dark:bg-night'}`}
      >
        <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
      </button>
    </div>
  );
}

function SelectField({ label, value, options, onChange }) {
  return (
    <div className="py-3 border-b border-cream-dark dark:border-night last:border-0">
      <label className="block font-medium text-night dark:text-cream mb-2">{label}</label>
      <select 
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2 rounded-lg bg-cream-warm dark:bg-night border border-cream-dark dark:border-night text-night dark:text-cream"
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  );
}

function InputField({ label, value, type = 'text', placeholder, onChange }) {
  return (
    <div className="py-3 border-b border-cream-dark dark:border-night last:border-0">
      <label className="block font-medium text-night dark:text-cream mb-2">{label}</label>
      <input 
        type={type}
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2 rounded-lg bg-cream-warm dark:bg-night border border-cream-dark dark:border-night text-night dark:text-cream"
      />
    </div>
  );
}

function ApiKeyField({ label, value, onChange, onTest }) {
  const [visible, setVisible] = useState(false);
  const masked = value ? '•'.repeat(Math.min(value.length, 20)) + value.slice(-4) : '';
  
  return (
    <div className="py-3 border-b border-cream-dark dark:border-night last:border-0">
      <label className="block font-medium text-night dark:text-cream mb-2">{label}</label>
      <div className="flex gap-2">
        <input 
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Enter API key..."
          className="flex-1 px-4 py-2 rounded-lg bg-cream-warm dark:bg-night border border-cream-dark dark:border-night text-night dark:text-cream"
        />
        <button 
          onClick={() => setVisible(!visible)}
          className="btn-ghost px-3"
        >
          {visible ? '🙈' : '👁️'}
        </button>
        <button onClick={onTest} className="btn-outline">Test</button>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    // General
    autoPosting: true,
    humanApproval: true,
    emergencyAlerts: true,
    
    // Scheduling
    postingFrequency: 'moderate',
    timezone: 'America/Chicago',
    
    // Voice
    authenticityThreshold: 0.75,
    autoEnhance: true,
    
    // Notifications
    emailNotifications: true,
    slackNotifications: false,
    notificationLevel: 'important',
    
    // API Keys
    openaiKey: '',
    elevenLabsKey: '',
    canvaKey: '',
    
    // Social Media
    instagramToken: '',
    facebookToken: '',
    tiktokToken: '',
    youtubeKey: ''
  });

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    try {
      // Save settings to backend
      alert('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  };

  const handleTestApi = (apiName) => {
    alert(`Testing ${apiName} connection...`);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-display font-bold text-night dark:text-cream">Settings</h2>
        <p className="text-night/50 dark:text-cream/50">Configure your marketing platform preferences</p>
      </div>

      {/* General Settings */}
      <SettingsSection title="General" description="Core platform behavior settings">
        <Toggle 
          label="Automatic Posting"
          description="Allow agents to post content automatically"
          enabled={settings.autoPosting}
          onChange={(v) => updateSetting('autoPosting', v)}
        />
        <Toggle 
          label="Human Approval Required"
          description="Require manual approval before posting"
          enabled={settings.humanApproval}
          onChange={(v) => updateSetting('humanApproval', v)}
        />
        <Toggle 
          label="Emergency Alerts"
          description="Receive alerts for critical issues"
          enabled={settings.emergencyAlerts}
          onChange={(v) => updateSetting('emergencyAlerts', v)}
        />
      </SettingsSection>

      {/* Scheduling */}
      <SettingsSection title="Scheduling" description="Content posting schedule settings">
        <SelectField 
          label="Posting Frequency"
          value={settings.postingFrequency}
          options={[
            { value: 'conservative', label: 'Conservative (1-2 posts/day)' },
            { value: 'moderate', label: 'Moderate (3-4 posts/day)' },
            { value: 'aggressive', label: 'Aggressive (5+ posts/day)' }
          ]}
          onChange={(v) => updateSetting('postingFrequency', v)}
        />
        <SelectField 
          label="Timezone"
          value={settings.timezone}
          options={[
            { value: 'America/Chicago', label: 'Central Time (Louisiana)' },
            { value: 'America/New_York', label: 'Eastern Time' },
            { value: 'America/Los_Angeles', label: 'Pacific Time' },
            { value: 'UTC', label: 'UTC' }
          ]}
          onChange={(v) => updateSetting('timezone', v)}
        />
      </SettingsSection>

      {/* Brand Voice */}
      <SettingsSection title="Brand Voice" description="Cajun authenticity settings">
        <SelectField 
          label="Authenticity Threshold"
          value={settings.authenticityThreshold}
          options={[
            { value: 0.6, label: 'Relaxed (60%)' },
            { value: 0.75, label: 'Standard (75%)' },
            { value: 0.85, label: 'Strict (85%)' },
            { value: 0.95, label: 'Very Strict (95%)' }
          ]}
          onChange={(v) => updateSetting('authenticityThreshold', parseFloat(v))}
        />
        <Toggle 
          label="Auto-Enhance Content"
          description="Automatically add Cajun authenticity to content"
          enabled={settings.autoEnhance}
          onChange={(v) => updateSetting('autoEnhance', v)}
        />
      </SettingsSection>

      {/* Notifications */}
      <SettingsSection title="Notifications" description="Alert and notification preferences">
        <Toggle 
          label="Email Notifications"
          description="Receive alerts via email"
          enabled={settings.emailNotifications}
          onChange={(v) => updateSetting('emailNotifications', v)}
        />
        <Toggle 
          label="Slack Notifications"
          description="Send alerts to Slack channel"
          enabled={settings.slackNotifications}
          onChange={(v) => updateSetting('slackNotifications', v)}
        />
        <SelectField 
          label="Notification Level"
          value={settings.notificationLevel}
          options={[
            { value: 'all', label: 'All Events' },
            { value: 'important', label: 'Important Only' },
            { value: 'errors', label: 'Errors Only' },
            { value: 'none', label: 'None' }
          ]}
          onChange={(v) => updateSetting('notificationLevel', v)}
        />
      </SettingsSection>

      {/* API Keys */}
      <SettingsSection title="AI Services" description="Configure AI service API keys">
        <ApiKeyField 
          label="OpenAI API Key"
          value={settings.openaiKey}
          onChange={(v) => updateSetting('openaiKey', v)}
          onTest={() => handleTestApi('OpenAI')}
        />
        <ApiKeyField 
          label="ElevenLabs API Key"
          value={settings.elevenLabsKey}
          onChange={(v) => updateSetting('elevenLabsKey', v)}
          onTest={() => handleTestApi('ElevenLabs')}
        />
        <ApiKeyField 
          label="Canva API Key"
          value={settings.canvaKey}
          onChange={(v) => updateSetting('canvaKey', v)}
          onTest={() => handleTestApi('Canva')}
        />
      </SettingsSection>

      {/* Social Media */}
      <SettingsSection title="Social Media" description="Platform API credentials">
        <ApiKeyField 
          label="Instagram Access Token"
          value={settings.instagramToken}
          onChange={(v) => updateSetting('instagramToken', v)}
          onTest={() => handleTestApi('Instagram')}
        />
        <ApiKeyField 
          label="Facebook Access Token"
          value={settings.facebookToken}
          onChange={(v) => updateSetting('facebookToken', v)}
          onTest={() => handleTestApi('Facebook')}
        />
        <ApiKeyField 
          label="TikTok Access Token"
          value={settings.tiktokToken}
          onChange={(v) => updateSetting('tiktokToken', v)}
          onTest={() => handleTestApi('TikTok')}
        />
        <ApiKeyField 
          label="YouTube API Key"
          value={settings.youtubeKey}
          onChange={(v) => updateSetting('youtubeKey', v)}
          onTest={() => handleTestApi('YouTube')}
        />
      </SettingsSection>

      {/* Save Button */}
      <div className="flex justify-end gap-4">
        <button className="btn-outline">Reset to Defaults</button>
        <button onClick={handleSave} className="btn-primary">Save Changes</button>
      </div>
    </div>
  );
}
