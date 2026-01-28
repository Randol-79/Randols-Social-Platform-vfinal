'use client';

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const AGENT_INFO = {
  master_orchestrator: {
    name: 'Master Orchestrator',
    description: 'Central coordination hub for all agent activities. Manages workflow execution and cross-platform consistency.',
    icon: '🎭',
    capabilities: ['Daily workflow execution', 'Agent coordination', 'Emergency override handling', 'Content calendar management']
  },
  content_generator: {
    name: 'Content Generator',
    description: 'AI-powered content creation with authentic Cajun voice. Handles text, image prompts, and video scripts.',
    icon: '✍️',
    capabilities: ['Morning greetings', 'Daily specials', 'Event promotions', 'Crawfish content', 'Emergency posts']
  },
  brand_voice_guardian: {
    name: 'Brand Voice Guardian',
    description: 'Ensures all content maintains authentic Cajun voice using the V.A.U.L.T. framework.',
    icon: '🛡️',
    capabilities: ['Authenticity scoring', 'Cultural appropriateness', 'Tone compliance', 'Content suggestions']
  },
  analytics: {
    name: 'Analytics Agent',
    description: 'Real-time performance tracking across all platforms. Monitors engagement and sentiment.',
    icon: '📊',
    capabilities: ['Engagement tracking', 'Sentiment analysis', 'Trend identification', 'Performance reports']
  },
  feedback_loop: {
    name: 'Feedback Loop',
    description: 'Continuous optimization based on performance data. Manages A/B testing and timing optimization.',
    icon: '🔄',
    capabilities: ['A/B testing', 'Timing optimization', 'Strategy refinement', 'Recommendation generation']
  }
};

function AgentCard({ agentKey, agent, info, onRestart, onConfigure, onToggle }) {
  const statusColors = {
    active: { bg: 'bg-marsh/10', text: 'text-marsh', dot: 'bg-marsh' },
    paused: { bg: 'bg-gold/10', text: 'text-gold', dot: 'bg-gold' },
    error: { bg: 'bg-cajun-red/10', text: 'text-cajun-red', dot: 'bg-cajun-red' },
    idle: { bg: 'bg-bayou/10', text: 'text-bayou', dot: 'bg-bayou' }
  };
  
  const status = agent?.status || 'active';
  const colors = statusColors[status] || statusColors.active;

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-xl bg-cajun-gradient flex items-center justify-center text-2xl">
            {info?.icon}
          </div>
          <div>
            <h3 className="font-semibold text-night dark:text-cream">{info?.name}</h3>
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${colors.dot} ${status === 'active' ? 'animate-pulse' : ''}`}></span>
              <span className={`text-sm capitalize ${colors.text}`}>{status}</span>
            </div>
          </div>
        </div>
        <button 
          onClick={() => onToggle(agentKey)}
          className={`px-3 py-1 rounded-full text-sm ${colors.bg} ${colors.text}`}
        >
          {status === 'active' ? 'Pause' : 'Resume'}
        </button>
      </div>

      <p className="text-sm text-night/60 dark:text-cream/60 mb-4">{info?.description}</p>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-cream-warm dark:bg-night rounded-lg p-3">
          <p className="text-xs text-night/50 dark:text-cream/50">Uptime</p>
          <p className="font-semibold text-night dark:text-cream">{agent?.uptime || '99.9%'}</p>
        </div>
        <div className="bg-cream-warm dark:bg-night rounded-lg p-3">
          <p className="text-xs text-night/50 dark:text-cream/50">Health</p>
          <p className="font-semibold text-marsh">{agent?.health || 'Good'}</p>
        </div>
      </div>

      <div className="mb-4">
        <p className="text-xs text-night/50 dark:text-cream/50 mb-2">Last Action</p>
        <p className="text-sm text-night dark:text-cream">{agent?.last_action || 'System monitoring'}</p>
      </div>

      <div className="mb-4">
        <p className="text-xs text-night/50 dark:text-cream/50 mb-2">Capabilities</p>
        <div className="flex flex-wrap gap-1">
          {info?.capabilities?.map((cap, idx) => (
            <span key={idx} className="px-2 py-1 bg-cream-dark dark:bg-night rounded text-xs text-night/70 dark:text-cream/70">
              {cap}
            </span>
          ))}
        </div>
      </div>

      <div className="flex gap-2">
        <button onClick={() => onConfigure(agentKey)} className="btn-outline flex-1 text-sm py-2">Configure</button>
        <button onClick={() => onRestart(agentKey)} className="btn-secondary flex-1 text-sm py-2">Restart</button>
      </div>
    </div>
  );
}

function SystemStatusBar({ systemStatus, onPauseAll, onResumeAll }) {
  const isAllActive = systemStatus === 'active';
  
  return (
    <div className={`card ${isAllActive ? 'bg-marsh/5 border border-marsh/20' : 'bg-gold/5 border border-gold/20'}`}>
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className={`w-12 h-12 rounded-full ${isAllActive ? 'bg-marsh/20' : 'bg-gold/20'} flex items-center justify-center`}>
            <span className={`w-4 h-4 rounded-full ${isAllActive ? 'bg-marsh animate-pulse' : 'bg-gold'}`}></span>
          </div>
          <div>
            <h3 className={`font-semibold ${isAllActive ? 'text-marsh' : 'text-gold'}`}>
              System {isAllActive ? 'Active' : 'Paused'}
            </h3>
            <p className="text-sm text-night/60 dark:text-cream/60">
              {isAllActive ? 'All agents running normally' : 'Agents are paused - no automated actions'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={onPauseAll}
            className={`btn-outline ${!isAllActive ? 'opacity-50' : ''}`}
            disabled={!isAllActive}
          >
            ⏸️ Pause All
          </button>
          <button 
            onClick={onResumeAll}
            className={`btn-primary ${isAllActive ? 'opacity-50' : ''}`}
            disabled={isAllActive}
          >
            ▶️ Resume All
          </button>
        </div>
      </div>
    </div>
  );
}

function ActivityLog({ activities }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Recent Activity</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {activities.map((activity, idx) => (
          <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-cream-warm dark:bg-night">
            <span className="text-xl">{AGENT_INFO[activity.agent]?.icon || '🔹'}</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-night dark:text-cream">{activity.message}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-xs text-night/50 dark:text-cream/50">{activity.agent.replace('_', ' ')}</span>
                <span className="text-xs text-night/30 dark:text-cream/30">•</span>
                <span className="text-xs text-night/50 dark:text-cream/50">{activity.time}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ConfigModal({ agent, agentInfo, onClose, onSave }) {
  const [config, setConfig] = useState({
    enabled: true,
    auto_restart: true,
    log_level: 'info',
    notification_threshold: 'all'
  });

  if (!agent) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="card max-w-md w-full" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{agentInfo?.icon}</span>
            <h3 className="text-lg font-semibold text-night dark:text-cream">Configure {agentInfo?.name}</h3>
          </div>
          <button onClick={onClose} className="btn-ghost p-2">✕</button>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-night dark:text-cream">Enabled</p>
              <p className="text-sm text-night/50 dark:text-cream/50">Agent will process tasks when enabled</p>
            </div>
            <button 
              onClick={() => setConfig({ ...config, enabled: !config.enabled })}
              className={`w-12 h-6 rounded-full transition-colors ${config.enabled ? 'bg-marsh' : 'bg-cream-dark dark:bg-night'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${config.enabled ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-night dark:text-cream">Auto Restart</p>
              <p className="text-sm text-night/50 dark:text-cream/50">Automatically restart on failure</p>
            </div>
            <button 
              onClick={() => setConfig({ ...config, auto_restart: !config.auto_restart })}
              className={`w-12 h-6 rounded-full transition-colors ${config.auto_restart ? 'bg-marsh' : 'bg-cream-dark dark:bg-night'}`}
            >
              <div className={`w-5 h-5 rounded-full bg-white shadow-sm transform transition-transform ${config.auto_restart ? 'translate-x-6' : 'translate-x-0.5'}`} />
            </button>
          </div>

          <div>
            <label className="block font-medium text-night dark:text-cream mb-2">Log Level</label>
            <select 
              value={config.log_level}
              onChange={(e) => setConfig({ ...config, log_level: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-cream-warm dark:bg-night border border-cream-dark dark:border-night text-night dark:text-cream"
            >
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-night dark:text-cream mb-2">Notification Threshold</label>
            <select 
              value={config.notification_threshold}
              onChange={(e) => setConfig({ ...config, notification_threshold: e.target.value })}
              className="w-full px-4 py-2 rounded-lg bg-cream-warm dark:bg-night border border-cream-dark dark:border-night text-night dark:text-cream"
            >
              <option value="all">All Events</option>
              <option value="important">Important Only</option>
              <option value="errors">Errors Only</option>
              <option value="none">None</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button onClick={onClose} className="btn-outline flex-1">Cancel</button>
          <button onClick={() => { onSave(config); onClose(); }} className="btn-primary flex-1">Save Changes</button>
        </div>
      </div>
    </div>
  );
}

export default function AgentsPage() {
  const [agents, setAgents] = useState({});
  const [systemStatus, setSystemStatus] = useState('active');
  const [configAgent, setConfigAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activities, setActivities] = useState([
    { agent: 'content_generator', message: 'Created crawfish boil promotion content', time: '2 min ago' },
    { agent: 'brand_voice_guardian', message: 'Validated 3 posts - all approved', time: '15 min ago' },
    { agent: 'analytics', message: 'Generated weekly performance report', time: '1 hour ago' },
    { agent: 'feedback_loop', message: 'Optimized posting schedule based on engagement data', time: '2 hours ago' },
    { agent: 'master_orchestrator', message: 'Completed daily workflow execution', time: '3 hours ago' }
  ]);

  useEffect(() => {
    fetchAgentStatus();
  }, []);

  const fetchAgentStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/agents/status`);
      if (res.ok) {
        const data = await res.json();
        setAgents(data.agents || {});
      }
    } catch (error) {
      console.error('Error fetching agent status:', error);
      // Mock data
      setAgents({
        master_orchestrator: { status: 'active', health: 'good', uptime: '99.9%', last_action: 'System monitoring' },
        content_generator: { status: 'active', health: 'good', uptime: '99.5%', last_action: 'Created crawfish promo' },
        brand_voice_guardian: { status: 'active', health: 'good', uptime: '99.8%', last_action: 'Validated 3 posts' },
        analytics: { status: 'active', health: 'good', uptime: '99.9%', last_action: 'Generated weekly report' },
        feedback_loop: { status: 'active', health: 'good', uptime: '99.7%', last_action: 'Optimized posting times' }
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePauseAll = async () => {
    try {
      await fetch(`${API_BASE}/api/agents/pause`, { method: 'POST' });
      setSystemStatus('paused');
      setAgents(prev => {
        const updated = {};
        Object.keys(prev).forEach(key => {
          updated[key] = { ...prev[key], status: 'paused' };
        });
        return updated;
      });
    } catch (error) {
      console.error('Error pausing agents:', error);
    }
  };

  const handleResumeAll = async () => {
    try {
      await fetch(`${API_BASE}/api/agents/resume`, { method: 'POST' });
      setSystemStatus('active');
      setAgents(prev => {
        const updated = {};
        Object.keys(prev).forEach(key => {
          updated[key] = { ...prev[key], status: 'active' };
        });
        return updated;
      });
    } catch (error) {
      console.error('Error resuming agents:', error);
    }
  };

  const handleRestart = async (agentKey) => {
    try {
      await fetch(`${API_BASE}/api/agents/${agentKey}/restart`, { method: 'POST' });
      setActivities(prev => [{
        agent: agentKey,
        message: `${AGENT_INFO[agentKey]?.name} restarted successfully`,
        time: 'Just now'
      }, ...prev.slice(0, 9)]);
    } catch (error) {
      console.error('Error restarting agent:', error);
    }
  };

  const handleToggle = (agentKey) => {
    setAgents(prev => ({
      ...prev,
      [agentKey]: {
        ...prev[agentKey],
        status: prev[agentKey]?.status === 'active' ? 'paused' : 'active'
      }
    }));
  };

  const handleSaveConfig = (config) => {
    console.log('Saving config:', config);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-display font-bold text-night dark:text-cream">Agent Status</h2>
        <p className="text-night/50 dark:text-cream/50">Monitor and manage your AI agents</p>
      </div>

      <SystemStatusBar 
        systemStatus={systemStatus}
        onPauseAll={handlePauseAll}
        onResumeAll={handleResumeAll}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(AGENT_INFO).map(([key, info]) => (
              <AgentCard
                key={key}
                agentKey={key}
                agent={agents[key]}
                info={info}
                onRestart={handleRestart}
                onConfigure={setConfigAgent}
                onToggle={handleToggle}
              />
            ))}
          </div>
        </div>
        
        <div>
          <ActivityLog activities={activities} />
        </div>
      </div>

      <ConfigModal
        agent={configAgent}
        agentInfo={AGENT_INFO[configAgent]}
        onClose={() => setConfigAgent(null)}
        onSave={handleSaveConfig}
      />
    </div>
  );
}
