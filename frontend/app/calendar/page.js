'use client';

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const PLATFORMS = [
  { id: 'instagram', name: 'Instagram', color: 'bg-gradient-to-r from-purple-500 to-pink-500', icon: '📸' },
  { id: 'facebook', name: 'Facebook', color: 'bg-blue-600', icon: '👥' },
  { id: 'tiktok', name: 'TikTok', color: 'bg-black', icon: '🎵' },
  { id: 'youtube', name: 'YouTube', color: 'bg-red-600', icon: '▶️' },
  { id: 'google_posts', name: 'Google Posts', color: 'bg-green-600', icon: '📍' }
];

const STATUS_COLORS = {
  scheduled: 'bg-bayou/10 text-bayou border-bayou/20',
  approved: 'bg-marsh/10 text-marsh border-marsh/20',
  pending_review: 'bg-gold/10 text-gold border-gold/20',
  published: 'bg-cajun-red/10 text-cajun-red border-cajun-red/20'
};

function CalendarHeader({ currentDate, onPrevWeek, onNextWeek, onToday, view, onViewChange }) {
  const monthYear = currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-display font-bold text-night dark:text-cream">{monthYear}</h2>
        <div className="flex items-center gap-1">
          <button onClick={onPrevWeek} className="btn-ghost p-2">←</button>
          <button onClick={onToday} className="btn-outline text-sm px-3 py-1">Today</button>
          <button onClick={onNextWeek} className="btn-ghost p-2">→</button>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div className="flex bg-cream-dark dark:bg-night rounded-lg p-1">
          {['day', 'week', 'month'].map((v) => (
            <button
              key={v}
              onClick={() => onViewChange(v)}
              className={`px-3 py-1 rounded text-sm capitalize transition-colors ${
                view === v ? 'bg-white dark:bg-night-light text-night dark:text-cream shadow-sm' : 'text-night/60 dark:text-cream/60'
              }`}
            >
              {v}
            </button>
          ))}
        </div>
        <button className="btn-primary text-sm">+ New Post</button>
      </div>
    </div>
  );
}

function PostCard({ post, onClick }) {
  const platform = PLATFORMS.find(p => p.id === post.platform);
  const statusStyle = STATUS_COLORS[post.status] || STATUS_COLORS.scheduled;
  
  return (
    <div 
      onClick={() => onClick(post)}
      className={`p-2 rounded-lg border cursor-pointer hover:shadow-md transition-shadow ${statusStyle}`}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className={`w-5 h-5 rounded ${platform?.color} flex items-center justify-center text-white text-xs`}>
          {platform?.icon || '📝'}
        </span>
        <span className="text-xs font-medium">{post.scheduled_time}</span>
      </div>
      <p className="text-xs line-clamp-2">{post.preview}</p>
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs opacity-70 capitalize">{post.content_type.replace('_', ' ')}</span>
        {post.authenticity_score && (
          <span className="text-xs bg-white/50 dark:bg-black/20 px-1.5 py-0.5 rounded">
            {Math.round(post.authenticity_score * 100)}% ✓
          </span>
        )}
      </div>
    </div>
  );
}

function DayColumn({ date, posts, isToday, onClick }) {
  const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
  const dayNum = date.getDate();
  
  return (
    <div className={`flex-1 min-w-[140px] ${isToday ? 'bg-cajun-red/5 dark:bg-cajun-red/10' : ''}`}>
      <div className={`sticky top-0 bg-white dark:bg-night-light p-3 border-b border-cream-dark dark:border-night text-center ${isToday ? 'bg-cajun-red/10' : ''}`}>
        <p className="text-xs text-night/50 dark:text-cream/50">{dayName}</p>
        <p className={`text-lg font-bold ${isToday ? 'text-cajun-red' : 'text-night dark:text-cream'}`}>{dayNum}</p>
      </div>
      <div className="p-2 space-y-2 min-h-[400px]">
        {posts.map((post, idx) => (
          <PostCard key={idx} post={post} onClick={onClick} />
        ))}
        {posts.length === 0 && (
          <div className="h-24 border-2 border-dashed border-cream-dark dark:border-night rounded-lg flex items-center justify-center">
            <span className="text-xs text-night/30 dark:text-cream/30">No posts</span>
          </div>
        )}
      </div>
    </div>
  );
}

function PostDetailModal({ post, onClose, onApprove, onEdit, onDelete }) {
  if (!post) return null;
  
  const platform = PLATFORMS.find(p => p.id === post.platform);
  
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="card max-w-lg w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className={`w-10 h-10 rounded-lg ${platform?.color} flex items-center justify-center text-white text-xl`}>
              {platform?.icon}
            </span>
            <div>
              <h3 className="font-semibold text-night dark:text-cream">{platform?.name}</h3>
              <p className="text-sm text-night/50 dark:text-cream/50">
                {post.scheduled_time} • {post.content_type.replace('_', ' ')}
              </p>
            </div>
          </div>
          <button onClick={onClose} className="btn-ghost p-2">✕</button>
        </div>
        
        <div className="bg-cream-warm dark:bg-night rounded-lg p-4 mb-4">
          <p className="text-night dark:text-cream whitespace-pre-wrap">{post.preview}</p>
        </div>
        
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-cream-dark/50 dark:bg-night rounded-lg p-3">
            <p className="text-xs text-night/50 dark:text-cream/50">Status</p>
            <p className="font-medium text-night dark:text-cream capitalize">{post.status.replace('_', ' ')}</p>
          </div>
          <div className="bg-cream-dark/50 dark:bg-night rounded-lg p-3">
            <p className="text-xs text-night/50 dark:text-cream/50">Authenticity Score</p>
            <p className="font-medium text-night dark:text-cream">{Math.round(post.authenticity_score * 100)}%</p>
          </div>
        </div>
        
        <div className="flex gap-3">
          {post.status === 'pending_review' && (
            <button onClick={() => onApprove(post)} className="btn-primary flex-1">Approve</button>
          )}
          <button onClick={() => onEdit(post)} className="btn-outline flex-1">Edit</button>
          <button onClick={() => onDelete(post)} className="btn-ghost text-cajun-red flex-1">Delete</button>
        </div>
      </div>
    </div>
  );
}

function FilterBar({ platforms, selectedPlatforms, onPlatformToggle, selectedStatus, onStatusChange }) {
  return (
    <div className="flex flex-wrap items-center gap-4 mb-6">
      <div className="flex items-center gap-2">
        <span className="text-sm text-night/60 dark:text-cream/60">Platforms:</span>
        <div className="flex gap-1">
          {PLATFORMS.map((platform) => (
            <button
              key={platform.id}
              onClick={() => onPlatformToggle(platform.id)}
              className={`w-8 h-8 rounded-lg flex items-center justify-center transition-opacity ${
                selectedPlatforms.includes(platform.id) ? platform.color + ' text-white' : 'bg-cream-dark dark:bg-night opacity-50'
              }`}
              title={platform.name}
            >
              {platform.icon}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <span className="text-sm text-night/60 dark:text-cream/60">Status:</span>
        <select 
          value={selectedStatus}
          onChange={(e) => onStatusChange(e.target.value)}
          className="px-3 py-1.5 rounded-lg bg-white dark:bg-night border border-cream-dark dark:border-night text-sm text-night dark:text-cream"
        >
          <option value="all">All</option>
          <option value="scheduled">Scheduled</option>
          <option value="approved">Approved</option>
          <option value="pending_review">Pending Review</option>
          <option value="published">Published</option>
        </select>
      </div>
    </div>
  );
}

export default function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState('week');
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [selectedPlatforms, setSelectedPlatforms] = useState(PLATFORMS.map(p => p.id));
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCalendarData();
  }, [currentDate]);

  const fetchCalendarData = async () => {
    try {
      const dateStr = currentDate.toISOString().split('T')[0];
      const res = await fetch(`${API_BASE}/api/calendar/content?date=${dateStr}&range=${view}`);
      if (res.ok) {
        const data = await res.json();
        setPosts(data.posts || []);
      }
    } catch (error) {
      console.error('Error fetching calendar:', error);
      // Use mock data
      setPosts([
        { id: 1, platform: 'instagram', scheduled_time: '09:00', content_type: 'morning_greeting', preview: "Good morning, y'all! Fresh crawfish today...", status: 'scheduled', authenticity_score: 0.87 },
        { id: 2, platform: 'facebook', scheduled_time: '11:30', content_type: 'daily_special', preview: "Today's special: Gulf Shrimp Étouffée...", status: 'approved', authenticity_score: 0.92 },
        { id: 3, platform: 'tiktok', scheduled_time: '15:00', content_type: 'event_promotion', preview: "Zydeco night tonight! Laissez les bon temps rouler!", status: 'pending_review', authenticity_score: 0.95 },
        { id: 4, platform: 'facebook', scheduled_time: '18:30', content_type: 'evening_event', preview: "Live music starting at 7pm, cher!", status: 'scheduled', authenticity_score: 0.89 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getWeekDates = () => {
    const dates = [];
    const startOfWeek = new Date(currentDate);
    startOfWeek.setDate(currentDate.getDate() - currentDate.getDay());
    
    for (let i = 0; i < 7; i++) {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      dates.push(date);
    }
    return dates;
  };

  const getPostsForDate = (date) => {
    const dateStr = date.toISOString().split('T')[0];
    return posts.filter(post => {
      const platformMatch = selectedPlatforms.includes(post.platform);
      const statusMatch = selectedStatus === 'all' || post.status === selectedStatus;
      return platformMatch && statusMatch;
    });
  };

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  const handleApprove = async (post) => {
    setPosts(prev => prev.map(p => p.id === post.id ? { ...p, status: 'approved' } : p));
    setSelectedPost(null);
  };

  const handleEdit = (post) => {
    alert(`Edit post: ${post.id}`);
    setSelectedPost(null);
  };

  const handleDelete = async (post) => {
    if (confirm('Delete this post?')) {
      setPosts(prev => prev.filter(p => p.id !== post.id));
      setSelectedPost(null);
    }
  };

  const weekDates = getWeekDates();
  const today = new Date().toDateString();

  return (
    <div className="space-y-6">
      <CalendarHeader
        currentDate={currentDate}
        onPrevWeek={() => setCurrentDate(new Date(currentDate.setDate(currentDate.getDate() - 7)))}
        onNextWeek={() => setCurrentDate(new Date(currentDate.setDate(currentDate.getDate() + 7)))}
        onToday={() => setCurrentDate(new Date())}
        view={view}
        onViewChange={setView}
      />
      
      <FilterBar
        selectedPlatforms={selectedPlatforms}
        onPlatformToggle={handlePlatformToggle}
        selectedStatus={selectedStatus}
        onStatusChange={setSelectedStatus}
      />

      {/* Stats Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {Object.entries({ scheduled: 0, approved: 0, pending_review: 0, published: 0 }).map(([status]) => {
          const count = posts.filter(p => p.status === status).length;
          return (
            <div key={status} className={`card !p-4 border ${STATUS_COLORS[status]}`}>
              <p className="text-2xl font-bold">{count}</p>
              <p className="text-sm capitalize">{status.replace('_', ' ')}</p>
            </div>
          );
        })}
      </div>

      {/* Calendar Grid */}
      <div className="card !p-0 overflow-hidden">
        <div className="flex overflow-x-auto">
          {weekDates.map((date, idx) => (
            <DayColumn
              key={idx}
              date={date}
              posts={getPostsForDate(date)}
              isToday={date.toDateString() === today}
              onClick={setSelectedPost}
            />
          ))}
        </div>
      </div>

      {/* Post Detail Modal */}
      <PostDetailModal
        post={selectedPost}
        onClose={() => setSelectedPost(null)}
        onApprove={handleApprove}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}
