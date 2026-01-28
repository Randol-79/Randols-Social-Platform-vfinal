'use client';

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Simple Bar Chart Component
function BarChart({ data, height = 200 }) {
  const maxValue = Math.max(...data.map(d => d.value));
  
  return (
    <div className="flex items-end justify-between gap-2" style={{ height }}>
      {data.map((item, idx) => (
        <div key={idx} className="flex-1 flex flex-col items-center gap-2">
          <div 
            className="w-full bg-cajun-gradient rounded-t-lg transition-all duration-500 hover:opacity-80"
            style={{ height: `${(item.value / maxValue) * 100}%`, minHeight: 4 }}
          />
          <span className="text-xs text-night/60 dark:text-cream/60">{item.label}</span>
        </div>
      ))}
    </div>
  );
}

// Line Chart Component (Simplified)
function LineChart({ data, height = 200 }) {
  const maxValue = Math.max(...data.map(d => d.value));
  const points = data.map((d, i) => ({
    x: (i / (data.length - 1)) * 100,
    y: 100 - (d.value / maxValue) * 100
  }));
  
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  
  return (
    <div className="relative" style={{ height }}>
      <svg viewBox="0 0 100 100" className="w-full h-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#C0152F" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#C0152F" stopOpacity="0" />
          </linearGradient>
        </defs>
        {/* Area fill */}
        <path 
          d={`${pathD} L 100 100 L 0 100 Z`}
          fill="url(#lineGradient)"
        />
        {/* Line */}
        <path 
          d={pathD}
          fill="none"
          stroke="#C0152F"
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
        {/* Points */}
        {points.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="3" fill="#C0152F" className="hover:r-4 transition-all" />
        ))}
      </svg>
      <div className="flex justify-between mt-2">
        {data.filter((_, i) => i % 2 === 0).map((d, i) => (
          <span key={i} className="text-xs text-night/50 dark:text-cream/50">{d.label}</span>
        ))}
      </div>
    </div>
  );
}

// Platform Card
function PlatformCard({ platform, metrics }) {
  const platformStyles = {
    instagram: { color: 'from-purple-500 to-pink-500', icon: '📸' },
    facebook: { color: 'from-blue-600 to-blue-500', icon: '👥' },
    tiktok: { color: 'from-gray-900 to-gray-700', icon: '🎵' },
    youtube: { color: 'from-red-600 to-red-500', icon: '▶️' }
  };
  
  const style = platformStyles[platform] || platformStyles.instagram;
  
  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${style.color} flex items-center justify-center text-white text-2xl`}>
          {style.icon}
        </div>
        <div>
          <h4 className="font-semibold text-night dark:text-cream capitalize">{platform}</h4>
          <p className="text-sm text-night/50 dark:text-cream/50">{metrics.followers?.toLocaleString()} followers</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-cream-warm dark:bg-night rounded-lg p-3">
          <p className="text-xs text-night/50 dark:text-cream/50">Engagement</p>
          <p className="text-lg font-bold text-night dark:text-cream">{(metrics.engagement_rate * 100).toFixed(1)}%</p>
        </div>
        <div className="bg-cream-warm dark:bg-night rounded-lg p-3">
          <p className="text-xs text-night/50 dark:text-cream/50">Reach</p>
          <p className="text-lg font-bold text-night dark:text-cream">{metrics.reach?.toLocaleString()}</p>
        </div>
        <div className="bg-cream-warm dark:bg-night rounded-lg p-3">
          <p className="text-xs text-night/50 dark:text-cream/50">Posts</p>
          <p className="text-lg font-bold text-night dark:text-cream">{metrics.posts_this_week}</p>
        </div>
        <div className="bg-cream-warm dark:bg-night rounded-lg p-3">
          <p className="text-xs text-night/50 dark:text-cream/50">Trend</p>
          <p className={`text-lg font-bold ${metrics.trend === 'up' ? 'text-marsh' : metrics.trend === 'down' ? 'text-cajun-red' : 'text-bayou'}`}>
            {metrics.trend === 'up' ? '↑' : metrics.trend === 'down' ? '↓' : '→'} {metrics.change}%
          </p>
        </div>
      </div>
    </div>
  );
}

// Recommendation Card
function RecommendationCard({ rec }) {
  const priorityColors = {
    high: 'border-cajun-red bg-cajun-red/5',
    medium: 'border-gold bg-gold/5',
    low: 'border-bayou bg-bayou/5'
  };
  
  return (
    <div className={`card border-l-4 ${priorityColors[rec.priority]}`}>
      <div className="flex items-start justify-between mb-2">
        <h4 className="font-semibold text-night dark:text-cream">{rec.title}</h4>
        <span className={`px-2 py-0.5 rounded text-xs uppercase ${
          rec.priority === 'high' ? 'bg-cajun-red/10 text-cajun-red' :
          rec.priority === 'medium' ? 'bg-gold/10 text-gold' : 'bg-bayou/10 text-bayou'
        }`}>
          {rec.priority}
        </span>
      </div>
      <p className="text-sm text-night/60 dark:text-cream/60 mb-3">{rec.description}</p>
      <div className="space-y-1">
        {rec.actions?.map((action, idx) => (
          <div key={idx} className="flex items-center gap-2 text-sm text-night/70 dark:text-cream/70">
            <span className="text-marsh">✓</span>
            <span>{action}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// Content Performance Table
function ContentPerformanceTable({ data }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-cream-dark dark:border-night">
            <th className="text-left py-3 px-4 text-sm font-medium text-night/60 dark:text-cream/60">Content Type</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-night/60 dark:text-cream/60">Posts</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-night/60 dark:text-cream/60">Engagement</th>
            <th className="text-right py-3 px-4 text-sm font-medium text-night/60 dark:text-cream/60">Best Platform</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(data).map(([type, metrics]) => (
            <tr key={type} className="border-b border-cream-dark/50 dark:border-night/50 hover:bg-cream-warm dark:hover:bg-night/50">
              <td className="py-3 px-4 text-sm font-medium text-night dark:text-cream capitalize">{type.replace('_', ' ')}</td>
              <td className="py-3 px-4 text-sm text-right text-night/70 dark:text-cream/70">{metrics.post_count}</td>
              <td className="py-3 px-4 text-sm text-right">
                <span className={`px-2 py-0.5 rounded ${metrics.avg_engagement_rate > 0.04 ? 'bg-marsh/10 text-marsh' : 'bg-gold/10 text-gold'}`}>
                  {(metrics.avg_engagement_rate * 100).toFixed(2)}%
                </span>
              </td>
              <td className="py-3 px-4 text-sm text-right text-night/70 dark:text-cream/70 capitalize">{metrics.best_platform}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('7d');
  const [analytics, setAnalytics] = useState(null);
  const [platformMetrics, setPlatformMetrics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, [period]);

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/analytics/performance?period=${period}`);
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
      
      const platformRes = await fetch(`${API_BASE}/api/analytics/platforms`);
      if (platformRes.ok) {
        const data = await platformRes.json();
        setPlatformMetrics(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Mock data
      setAnalytics({
        overall_performance: {
          avg_engagement_rate: 0.042,
          engagement_trend: 'improving',
          avg_reach: 3200,
          avg_sentiment: 0.78,
          total_posts: 28,
          performance_grade: 'B'
        },
        content_type_analysis: {
          crawfish_content: { post_count: 8, avg_engagement_rate: 0.055, best_platform: 'instagram' },
          daily_special: { post_count: 7, avg_engagement_rate: 0.038, best_platform: 'facebook' },
          event_promotion: { post_count: 6, avg_engagement_rate: 0.062, best_platform: 'tiktok' },
          morning_greeting: { post_count: 7, avg_engagement_rate: 0.032, best_platform: 'instagram' }
        },
        recommendations: [
          { type: 'performance', priority: 'high', title: 'Boost Crawfish Content', description: 'Crawfish posts outperform by 31%', actions: ['Increase crawfish posts to 3x/week', 'Add video content'] },
          { type: 'timing', priority: 'medium', title: 'Optimize Evening Posts', description: 'Evening posts get 25% more engagement', actions: ['Schedule key content for 6-8pm', 'Add live music reminders'] },
          { type: 'platform', priority: 'low', title: 'Grow TikTok Presence', description: 'Highest engagement rate at 6.1%', actions: ['Increase TikTok posting frequency', 'Create more short-form video'] }
        ]
      });
      
      setPlatformMetrics({
        instagram: { followers: 12500, engagement_rate: 0.042, reach: 45000, posts_this_week: 14, trend: 'up', change: 12 },
        facebook: { followers: 8900, engagement_rate: 0.038, reach: 32000, posts_this_week: 12, trend: 'up', change: 8 },
        tiktok: { followers: 5600, engagement_rate: 0.061, reach: 125000, posts_this_week: 8, trend: 'up', change: 24 },
        youtube: { followers: 2100, engagement_rate: 0.029, reach: 8500, posts_this_week: 2, trend: 'stable', change: 2 }
      });
    } finally {
      setLoading(false);
    }
  };

  const engagementData = [
    { label: 'Mon', value: 3.8 },
    { label: 'Tue', value: 4.2 },
    { label: 'Wed', value: 3.9 },
    { label: 'Thu', value: 4.5 },
    { label: 'Fri', value: 5.1 },
    { label: 'Sat', value: 4.8 },
    { label: 'Sun', value: 4.3 }
  ];

  const reachData = [
    { label: 'W1', value: 28000 },
    { label: 'W2', value: 32000 },
    { label: 'W3', value: 29000 },
    { label: 'W4', value: 35000 },
    { label: 'W5', value: 38000 },
    { label: 'W6', value: 42000 },
    { label: 'W7', value: 45000 }
  ];

  const overall = analytics?.overall_performance || {};

  return (
    <div className="space-y-6">
      {/* Period Selector & Overview */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-display font-bold text-night dark:text-cream">Performance Analytics</h2>
          <p className="text-night/50 dark:text-cream/50">Track your social media performance and insights</p>
        </div>
        <div className="flex bg-cream-dark dark:bg-night rounded-lg p-1">
          {['7d', '14d', '30d', '90d'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2 rounded text-sm transition-colors ${
                period === p ? 'bg-white dark:bg-night-light text-night dark:text-cream shadow-sm' : 'text-night/60 dark:text-cream/60'
              }`}
            >
              {p === '7d' ? '7 Days' : p === '14d' ? '14 Days' : p === '30d' ? '30 Days' : '90 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card text-center">
          <p className="text-4xl font-bold text-night dark:text-cream">{overall.performance_grade || 'B'}</p>
          <p className="text-sm text-night/50 dark:text-cream/50 mt-1">Performance Grade</p>
        </div>
        <div className="card text-center">
          <p className="text-4xl font-bold text-cajun-red">{((overall.avg_engagement_rate || 0.042) * 100).toFixed(1)}%</p>
          <p className="text-sm text-night/50 dark:text-cream/50 mt-1">Avg Engagement</p>
        </div>
        <div className="card text-center">
          <p className="text-4xl font-bold text-bayou">{(overall.avg_reach || 3200).toLocaleString()}</p>
          <p className="text-sm text-night/50 dark:text-cream/50 mt-1">Avg Reach</p>
        </div>
        <div className="card text-center">
          <p className="text-4xl font-bold text-marsh">{Math.round((overall.avg_sentiment || 0.78) * 100)}%</p>
          <p className="text-sm text-night/50 dark:text-cream/50 mt-1">Sentiment Score</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Engagement Rate Trend</h3>
          <LineChart data={engagementData} height={200} />
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Weekly Reach</h3>
          <BarChart data={reachData} height={200} />
        </div>
      </div>

      {/* Platform Performance */}
      <div>
        <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Platform Performance</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(platformMetrics).map(([platform, metrics]) => (
            <PlatformCard key={platform} platform={platform} metrics={metrics} />
          ))}
        </div>
      </div>

      {/* Content Performance */}
      <div className="card">
        <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Content Type Performance</h3>
        {analytics?.content_type_analysis && (
          <ContentPerformanceTable data={analytics.content_type_analysis} />
        )}
      </div>

      {/* Recommendations */}
      <div>
        <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">AI Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analytics?.recommendations?.map((rec, idx) => (
            <RecommendationCard key={idx} rec={rec} />
          ))}
        </div>
      </div>
    </div>
  );
}
