'use client';

import { useState, useEffect } from 'react';

// API Base URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Metric Card Component
function MetricCard({ icon, title, value, trend, trendValue }) {
  const trendColors = {
    positive: 'text-marsh bg-marsh/10',
    negative: 'text-cajun-red bg-cajun-red/10',
    neutral: 'text-bayou bg-bayou/10'
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="w-12 h-12 rounded-xl bg-cajun-gradient flex items-center justify-center text-white text-xl">
          {icon}
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${trendColors[trend]}`}>
          {trendValue}
        </span>
      </div>
      <div className="mt-4">
        <p className="text-sm text-night/60 dark:text-cream/60">{title}</p>
        <p className="text-2xl font-bold text-night dark:text-cream mt-1">{value}</p>
      </div>
    </div>
  );
}

// Agent Status Card
function AgentStatusCard({ name, status, lastAction, uptime, onConfigure, onRestart }) {
  const statusColors = {
    active: 'bg-marsh',
    paused: 'bg-gold',
    error: 'bg-cajun-red',
    idle: 'bg-bayou'
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-semibold text-night dark:text-cream">{name}</h4>
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${statusColors[status]} ${status === 'active' ? 'animate-pulse' : ''}`}></span>
          <span className="text-sm capitalize text-night/70 dark:text-cream/70">{status}</span>
        </div>
      </div>
      <div className="space-y-2 text-sm text-night/60 dark:text-cream/60">
        <p><span className="font-medium">Last Action:</span> {lastAction}</p>
        <p><span className="font-medium">Uptime:</span> {uptime}</p>
      </div>
      <div className="flex gap-2 mt-4">
        <button onClick={onConfigure} className="btn-outline flex-1 text-sm py-2">Configure</button>
        <button onClick={onRestart} className="btn-secondary flex-1 text-sm py-2">Restart</button>
      </div>
    </div>
  );
}

// Alert Item Component
function AlertItem({ type, message, time }) {
  const typeStyles = {
    info: { icon: 'ℹ️', bg: 'bg-bayou/10', text: 'text-bayou' },
    success: { icon: '✓', bg: 'bg-marsh/10', text: 'text-marsh' },
    warning: { icon: '⚠️', bg: 'bg-gold/10', text: 'text-gold' },
    error: { icon: '✕', bg: 'bg-cajun-red/10', text: 'text-cajun-red' }
  };

  const style = typeStyles[type] || typeStyles.info;

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg ${style.bg}`}>
      <span className={`text-lg ${style.text}`}>{style.icon}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-night dark:text-cream">{message}</p>
        <p className="text-xs text-night/50 dark:text-cream/50 mt-1">{time}</p>
      </div>
    </div>
  );
}

// Recent Post Card
function RecentPostCard({ platform, content, engagement, reach, time, status }) {
  const platformColors = {
    instagram: 'bg-gradient-to-r from-purple-500 to-pink-500',
    facebook: 'bg-blue-600',
    tiktok: 'bg-black',
    youtube: 'bg-red-600'
  };

  const statusBadge = {
    published: 'bg-marsh/10 text-marsh',
    scheduled: 'bg-gold/10 text-gold',
    pending: 'bg-bayou/10 text-bayou'
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-8 h-8 rounded-lg ${platformColors[platform]} flex items-center justify-center text-white text-sm font-bold`}>
          {platform.charAt(0).toUpperCase()}
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${statusBadge[status]}`}>
          {status}
        </span>
      </div>
      <p className="text-sm text-night dark:text-cream line-clamp-2 mb-3">{content}</p>
      <div className="flex items-center justify-between text-xs text-night/50 dark:text-cream/50">
        <div className="flex gap-3">
          <span>❤️ {engagement}</span>
          <span>👁️ {reach}</span>
        </div>
        <span>{time}</span>
      </div>
    </div>
  );
}

// Platform Performance Chart
function PerformanceChart({ data }) {
  return (
    <div className="space-y-4">
      {data.map((platform) => (
        <div key={platform.name} className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="font-medium text-night dark:text-cream">{platform.name}</span>
            <span className="text-night/60 dark:text-cream/60">{platform.engagement}%</span>
          </div>
          <div className="h-2 bg-cream-dark dark:bg-night rounded-full overflow-hidden">
            <div 
              className="h-full bg-cajun-gradient rounded-full transition-all duration-500"
              style={{ width: `${Math.min(platform.engagement * 15, 100)}%` }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}

// Quick Actions Panel
function QuickActions({ onPauseAgents, onEmergencyPost, onApproveContent, isPaused, pendingCount }) {
  return (
    <div className="flex flex-wrap gap-3">
      <button 
        onClick={onPauseAgents}
        className={`btn-outline flex items-center gap-2 ${isPaused ? 'border-marsh text-marsh' : ''}`}
      >
        {isPaused ? '▶️ Resume Agents' : '⏸️ Pause All'}
      </button>
      <button onClick={onEmergencyPost} className="btn-primary flex items-center gap-2">
        🚨 Emergency Post
      </button>
      {pendingCount > 0 && (
        <button onClick={onApproveContent} className="btn-secondary flex items-center gap-2">
          ✓ Approve Pending ({pendingCount})
        </button>
      )}
    </div>
  );
}

// Main Dashboard Component
export default function DashboardPage() {
  const [metrics, setMetrics] = useState({
    engagementRate: '4.2%',
    weeklyReach: '45,670',
    sentimentScore: '78%',
    postsScheduled: '12'
  });
  
  const [agents, setAgents] = useState([
    { name: 'Master Orchestrator', status: 'active', lastAction: 'Scheduled daily content', uptime: '99.9%' },
    { name: 'Content Generator', status: 'active', lastAction: 'Created crawfish promo', uptime: '99.5%' },
    { name: 'Brand Voice Guardian', status: 'active', lastAction: 'Validated 3 posts', uptime: '99.8%' },
    { name: 'Analytics Agent', status: 'active', lastAction: 'Generated weekly report', uptime: '99.9%' },
    { name: 'Feedback Loop', status: 'active', lastAction: 'Optimized posting times', uptime: '99.7%' }
  ]);

  const [alerts, setAlerts] = useState([
    { type: 'info', message: 'Content Generator created crawfish boil promotion', time: '2 min ago' },
    { type: 'success', message: 'Brand Voice Guardian approved 3 posts', time: '15 min ago' },
    { type: 'warning', message: 'Engagement rate dipped 5% - optimization triggered', time: '1 hour ago' }
  ]);

  const [recentPosts, setRecentPosts] = useState([
    { platform: 'instagram', content: "Fresh mudbugs just arrived! 🦞 Come get 'em while they're hot, cher!", engagement: '4.8%', reach: '3,240', time: '2h ago', status: 'published' },
    { platform: 'facebook', content: "Live zydeco tonight at 7pm! Laissez les bon temps rouler! 🎵", engagement: '3.9%', reach: '2,890', time: '4h ago', status: 'published' },
    { platform: 'tiktok', content: "POV: You just discovered the best crawfish in Louisiana 🔥", engagement: '6.2%', reach: '12,450', time: '6h ago', status: 'published' }
  ]);

  const [platformData, setPlatformData] = useState([
    { name: 'Instagram', engagement: 4.2 },
    { name: 'Facebook', engagement: 3.8 },
    { name: 'TikTok', engagement: 6.1 },
    { name: 'YouTube', engagement: 2.9 }
  ]);

  const [isPaused, setIsPaused] = useState(false);
  const [pendingCount, setPendingCount] = useState(2);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch agents status
      const agentsRes = await fetch(`${API_BASE}/api/agents/status`);
      if (agentsRes.ok) {
        const data = await agentsRes.json();
        // Process agent data
      }

      // Fetch analytics
      const analyticsRes = await fetch(`${API_BASE}/api/analytics/performance?period=7d`);
      if (analyticsRes.ok) {
        const data = await analyticsRes.json();
        // Process analytics data
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePauseAgents = async () => {
    try {
      const endpoint = isPaused ? '/api/agents/resume' : '/api/agents/pause';
      const res = await fetch(`${API_BASE}${endpoint}`, { method: 'POST' });
      if (res.ok) {
        setIsPaused(!isPaused);
        setAlerts(prev => [{
          type: isPaused ? 'success' : 'warning',
          message: isPaused ? 'All agents resumed' : 'All agents paused',
          time: 'Just now'
        }, ...prev.slice(0, 4)]);
      }
    } catch (error) {
      console.error('Error toggling agents:', error);
    }
  };

  const handleEmergencyPost = () => {
    // Open emergency post modal
    alert('Emergency post modal would open here');
  };

  const handleApproveContent = () => {
    setPendingCount(0);
    setAlerts(prev => [{
      type: 'success',
      message: 'All pending content approved',
      time: 'Just now'
    }, ...prev.slice(0, 4)]);
  };

  const handleAgentConfigure = (agentName) => {
    alert(`Configure ${agentName}`);
  };

  const handleAgentRestart = async (agentName) => {
    try {
      const res = await fetch(`${API_BASE}/api/agents/${agentName}/restart`, { method: 'POST' });
      if (res.ok) {
        setAlerts(prev => [{
          type: 'info',
          message: `${agentName} restarted successfully`,
          time: 'Just now'
        }, ...prev.slice(0, 4)]);
      }
    } catch (error) {
      console.error('Error restarting agent:', error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="card bg-cajun-gradient text-white">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-display font-bold">Today's Social Media Activity</h2>
            <p className="text-white/80 mt-1">
              {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}
            </p>
          </div>
          <QuickActions 
            onPauseAgents={handlePauseAgents}
            onEmergencyPost={handleEmergencyPost}
            onApproveContent={handleApproveContent}
            isPaused={isPaused}
            pendingCount={pendingCount}
          />
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard 
          icon="❤️"
          title="Engagement Rate"
          value={metrics.engagementRate}
          trend="positive"
          trendValue="+0.3% from last week"
        />
        <MetricCard 
          icon="👁️"
          title="Weekly Reach"
          value={metrics.weeklyReach}
          trend="positive"
          trendValue="+12% from last week"
        />
        <MetricCard 
          icon="😊"
          title="Sentiment Score"
          value={metrics.sentimentScore}
          trend="positive"
          trendValue="+5% from last week"
        />
        <MetricCard 
          icon="📅"
          title="Posts Scheduled"
          value={metrics.postsScheduled}
          trend="neutral"
          trendValue="For next 7 days"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alerts Panel */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-night dark:text-cream">System Alerts</h3>
            <span className="px-3 py-1 bg-marsh/10 text-marsh text-sm rounded-full">
              All Systems Operational
            </span>
          </div>
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <AlertItem key={index} {...alert} />
            ))}
          </div>
        </div>

        {/* Platform Performance */}
        <div className="card">
          <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Platform Performance</h3>
          <PerformanceChart data={platformData} />
        </div>
      </div>

      {/* Recent Posts */}
      <div className="card">
        <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Recent Posts Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {recentPosts.map((post, index) => (
            <RecentPostCard key={index} {...post} />
          ))}
        </div>
      </div>

      {/* Agent Status Grid */}
      <div>
        <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Agent Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent, index) => (
            <AgentStatusCard 
              key={index} 
              {...agent}
              onConfigure={() => handleAgentConfigure(agent.name)}
              onRestart={() => handleAgentRestart(agent.name.toLowerCase().replace(/\s+/g, '_'))}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
