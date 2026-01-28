'use client';

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// Platform Icons
const PlatformIcon = ({ platform, className = 'w-5 h-5' }) => {
  const icons = {
    instagram: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
      </svg>
    ),
    facebook: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    ),
    tiktok: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
      </svg>
    ),
    youtube: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    ),
    google_posts: (
      <svg className={className} viewBox="0 0 24 24" fill="currentColor">
        <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
        <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
    )
  };
  return icons[platform] || null;
};

// Status Badge Component
const StatusBadge = ({ status }) => {
  const styles = {
    draft: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300',
    pending_review: 'bg-gold/10 text-gold',
    approved: 'bg-marsh/10 text-marsh',
    rejected: 'bg-cajun-red/10 text-cajun-red',
    scheduled: 'bg-bayou/10 text-bayou',
    published: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
    failed: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  };

  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${styles[status] || styles.draft}`}>
      {status?.replace('_', ' ')}
    </span>
  );
};

// Content Type Badge
const ContentTypeBadge = ({ type }) => {
  const labels = {
    morning_greeting: '🌅 Morning',
    daily_special: '🍽️ Special',
    evening_event: '🎵 Event',
    crawfish_content: '🦞 Crawfish',
    event_promotion: '🎉 Promo',
    weekend_special: '🎭 Weekend',
    seasonal: '🌸 Seasonal'
  };

  return (
    <span className="px-2 py-0.5 bg-cream-dark dark:bg-night rounded text-xs">
      {labels[type] || type}
    </span>
  );
};

// Authenticity Score Meter
const AuthenticityMeter = ({ score }) => {
  const percentage = Math.round(score * 100);
  const color = percentage >= 75 ? 'bg-marsh' : percentage >= 50 ? 'bg-gold' : 'bg-cajun-red';
  
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-night/60 dark:text-cream/60">Cajun Authenticity</span>
        <span className={`font-medium ${percentage >= 75 ? 'text-marsh' : percentage >= 50 ? 'text-gold' : 'text-cajun-red'}`}>
          {percentage}%
        </span>
      </div>
      <div className="h-2 bg-cream-dark dark:bg-night rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full transition-all duration-500`} style={{ width: `${percentage}%` }} />
      </div>
    </div>
  );
};

// Content Card Component
const ContentCard = ({ content, onEdit, onDelete, onSchedule, onValidate }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="card hover:shadow-lg transition-all duration-300">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <ContentTypeBadge type={content.content_type} />
          <StatusBadge status={content.status} />
        </div>
        <div className="flex gap-1">
          {content.platforms?.map(platform => (
            <div key={platform} className="w-6 h-6 rounded bg-cream-dark dark:bg-night flex items-center justify-center">
              <PlatformIcon platform={platform} className="w-4 h-4 text-night/60 dark:text-cream/60" />
            </div>
          ))}
        </div>
      </div>

      {/* Content Preview */}
      <p className={`text-sm text-night dark:text-cream mb-3 ${expanded ? '' : 'line-clamp-3'}`}>
        {content.text}
      </p>
      {content.text?.length > 150 && (
        <button 
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-bayou hover:text-bayou/80 mb-3"
        >
          {expanded ? 'Show less' : 'Show more'}
        </button>
      )}

      {/* Validation Score */}
      {content.validation?.authenticity_score && (
        <div className="mb-4">
          <AuthenticityMeter score={content.validation.authenticity_score} />
        </div>
      )}

      {/* Hashtags */}
      {content.hashtags?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {content.hashtags.slice(0, 5).map((tag, i) => (
            <span key={i} className="px-2 py-0.5 bg-bayou/10 text-bayou text-xs rounded-full">
              {tag}
            </span>
          ))}
          {content.hashtags.length > 5 && (
            <span className="px-2 py-0.5 bg-cream-dark dark:bg-night text-night/50 dark:text-cream/50 text-xs rounded-full">
              +{content.hashtags.length - 5} more
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-cream-dark dark:border-night">
        <span className="text-xs text-night/50 dark:text-cream/50">
          {new Date(content.created_at).toLocaleDateString()}
        </span>
        <div className="flex gap-2">
          {content.status === 'draft' && (
            <button onClick={() => onValidate(content.id)} className="btn-ghost text-xs px-2 py-1">
              ✓ Validate
            </button>
          )}
          {content.status === 'approved' && (
            <button onClick={() => onSchedule(content.id)} className="btn-ghost text-xs px-2 py-1 text-bayou">
              📅 Schedule
            </button>
          )}
          <button onClick={() => onEdit(content)} className="btn-ghost text-xs px-2 py-1">
            ✏️ Edit
          </button>
          <button onClick={() => onDelete(content.id)} className="btn-ghost text-xs px-2 py-1 text-cajun-red">
            🗑️
          </button>
        </div>
      </div>
    </div>
  );
};

// AI Content Generator Modal
const ContentGeneratorModal = ({ isOpen, onClose, onGenerate }) => {
  const [contentType, setContentType] = useState('daily_special');
  const [platforms, setPlatforms] = useState(['instagram', 'facebook']);
  const [context, setContext] = useState('');
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState(null);

  const contentTypes = [
    { value: 'morning_greeting', label: '🌅 Morning Greeting' },
    { value: 'daily_special', label: '🍽️ Daily Special' },
    { value: 'evening_event', label: '🎵 Evening Event' },
    { value: 'crawfish_content', label: '🦞 Crawfish Content' },
    { value: 'event_promotion', label: '🎉 Event Promotion' },
    { value: 'weekend_special', label: '🎭 Weekend Special' }
  ];

  const platformOptions = [
    { value: 'instagram', label: 'Instagram' },
    { value: 'facebook', label: 'Facebook' },
    { value: 'tiktok', label: 'TikTok' },
    { value: 'youtube', label: 'YouTube' },
    { value: 'google_posts', label: 'Google Posts' }
  ];

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/content/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content_type: contentType,
          platforms,
          context: { additional_context: context }
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setGeneratedContent(data);
      }
    } catch (error) {
      console.error('Error generating content:', error);
    } finally {
      setGenerating(false);
    }
  };

  const handleSave = () => {
    if (generatedContent) {
      onGenerate(generatedContent);
      setGeneratedContent(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-night-light rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-cream-dark dark:border-night">
          <div>
            <h3 className="text-xl font-display font-bold text-night dark:text-cream">
              🤖 AI Content Generator
            </h3>
            <p className="text-sm text-night/60 dark:text-cream/60 mt-1">
              Generate authentic Cajun content with AI
            </p>
          </div>
          <button onClick={onClose} className="btn-ghost p-2 rounded-lg">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {!generatedContent ? (
            <>
              {/* Content Type */}
              <div>
                <label className="block text-sm font-medium text-night dark:text-cream mb-2">
                  Content Type
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {contentTypes.map(type => (
                    <button
                      key={type.value}
                      onClick={() => setContentType(type.value)}
                      className={`p-3 rounded-lg border-2 text-sm transition-all ${
                        contentType === type.value
                          ? 'border-cajun-red bg-cajun-red/5 text-cajun-red'
                          : 'border-cream-dark dark:border-night hover:border-cajun-red/50'
                      }`}
                    >
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Platforms */}
              <div>
                <label className="block text-sm font-medium text-night dark:text-cream mb-2">
                  Target Platforms
                </label>
                <div className="flex flex-wrap gap-2">
                  {platformOptions.map(platform => (
                    <button
                      key={platform.value}
                      onClick={() => {
                        setPlatforms(prev => 
                          prev.includes(platform.value)
                            ? prev.filter(p => p !== platform.value)
                            : [...prev, platform.value]
                        );
                      }}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg border-2 transition-all ${
                        platforms.includes(platform.value)
                          ? 'border-bayou bg-bayou/5 text-bayou'
                          : 'border-cream-dark dark:border-night hover:border-bayou/50'
                      }`}
                    >
                      <PlatformIcon platform={platform.value} className="w-4 h-4" />
                      <span className="text-sm">{platform.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Additional Context */}
              <div>
                <label className="block text-sm font-medium text-night dark:text-cream mb-2">
                  Additional Context (Optional)
                </label>
                <textarea
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="e.g., Tonight's band is Beausoleil, featuring special guest..."
                  className="w-full px-4 py-3 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream placeholder-night/40 dark:placeholder-cream/40 focus:ring-2 focus:ring-cajun-red focus:border-transparent"
                  rows={3}
                />
              </div>
            </>
          ) : (
            /* Generated Content Preview */
            <div className="space-y-4">
              <div className="p-4 bg-marsh/5 dark:bg-marsh/10 rounded-lg border border-marsh/20">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-marsh">✨</span>
                  <span className="text-sm font-medium text-marsh">Generated Content</span>
                </div>
                <p className="text-night dark:text-cream">{generatedContent.text}</p>
              </div>

              {/* Validation Preview */}
              {generatedContent.validation && (
                <div className="space-y-3">
                  <AuthenticityMeter score={generatedContent.validation?.authenticity_score || 0.8} />
                  
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2">
                      <span className={generatedContent.validation?.tone_compliance ? 'text-marsh' : 'text-cajun-red'}>
                        {generatedContent.validation?.tone_compliance ? '✓' : '✕'}
                      </span>
                      <span className="text-night/60 dark:text-cream/60">Tone Compliance</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={generatedContent.validation?.cultural_appropriateness ? 'text-marsh' : 'text-cajun-red'}>
                        {generatedContent.validation?.cultural_appropriateness ? '✓' : '✕'}
                      </span>
                      <span className="text-night/60 dark:text-cream/60">Cultural Fit</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Hashtags */}
              {generatedContent.hashtags?.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {generatedContent.hashtags.map((tag, i) => (
                    <span key={i} className="px-2 py-1 bg-bayou/10 text-bayou text-xs rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 p-6 border-t border-cream-dark dark:border-night">
          {!generatedContent ? (
            <>
              <button onClick={onClose} className="btn-outline">
                Cancel
              </button>
              <button
                onClick={handleGenerate}
                disabled={generating || platforms.length === 0}
                className="btn-primary flex items-center gap-2"
              >
                {generating ? (
                  <>
                    <span className="animate-spin">⚙️</span>
                    Generating...
                  </>
                ) : (
                  <>
                    ✨ Generate Content
                  </>
                )}
              </button>
            </>
          ) : (
            <>
              <button 
                onClick={() => setGeneratedContent(null)} 
                className="btn-outline"
              >
                ← Regenerate
              </button>
              <button onClick={handleSave} className="btn-primary">
                ✓ Save Content
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// Content Editor Modal
const ContentEditorModal = ({ isOpen, onClose, content, onSave }) => {
  const [editedContent, setEditedContent] = useState(content || {
    text: '',
    content_type: 'daily_special',
    platforms: ['instagram', 'facebook'],
    hashtags: []
  });
  const [hashtagInput, setHashtagInput] = useState('');
  const [validating, setValidating] = useState(false);
  const [validation, setValidation] = useState(null);

  useEffect(() => {
    if (content) {
      setEditedContent(content);
    }
  }, [content]);

  const handleValidate = async () => {
    setValidating(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/content/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: editedContent.text })
      });
      
      if (res.ok) {
        const data = await res.json();
        setValidation(data);
      }
    } catch (error) {
      console.error('Error validating:', error);
    } finally {
      setValidating(false);
    }
  };

  const handleEnhance = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/content/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: editedContent.text,
          keywords: editedContent.hashtags.map(h => h.replace('#', ''))
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        setEditedContent(prev => ({
          ...prev,
          text: data.enhanced,
          hashtags: [...new Set([...prev.hashtags, ...data.suggested_hashtags])]
        }));
        setValidation(data.validation);
      }
    } catch (error) {
      console.error('Error enhancing:', error);
    }
  };

  const addHashtag = () => {
    if (hashtagInput.trim()) {
      const tag = hashtagInput.startsWith('#') ? hashtagInput : `#${hashtagInput}`;
      setEditedContent(prev => ({
        ...prev,
        hashtags: [...new Set([...prev.hashtags, tag])]
      }));
      setHashtagInput('');
    }
  };

  const removeHashtag = (tag) => {
    setEditedContent(prev => ({
      ...prev,
      hashtags: prev.hashtags.filter(h => h !== tag)
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-night-light rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-cream-dark dark:border-night">
          <h3 className="text-xl font-display font-bold text-night dark:text-cream">
            {content?.id ? '✏️ Edit Content' : '📝 Create Content'}
          </h3>
          <button onClick={onClose} className="btn-ghost p-2 rounded-lg">
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Text Content */}
          <div>
            <label className="block text-sm font-medium text-night dark:text-cream mb-2">
              Content
            </label>
            <textarea
              value={editedContent.text}
              onChange={(e) => setEditedContent(prev => ({ ...prev, text: e.target.value }))}
              placeholder="Write your content here... Include authentic Cajun phrases like 'cher', 'y'all', 'laissez les bon temps rouler!'"
              className="w-full px-4 py-3 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream placeholder-night/40 dark:placeholder-cream/40 focus:ring-2 focus:ring-cajun-red focus:border-transparent"
              rows={5}
            />
            <div className="flex justify-between mt-2">
              <span className="text-xs text-night/50 dark:text-cream/50">
                {editedContent.text?.length || 0} characters
              </span>
              <button onClick={handleEnhance} className="text-xs text-bayou hover:text-bayou/80">
                ✨ Enhance with Cajun Voice
              </button>
            </div>
          </div>

          {/* Validation Results */}
          {validation && (
            <div className="p-4 bg-cream-warm dark:bg-night rounded-lg space-y-3">
              <AuthenticityMeter score={validation.authenticity_score} />
              
              <div className="grid grid-cols-3 gap-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className={validation.tone_compliance ? 'text-marsh' : 'text-cajun-red'}>
                    {validation.tone_compliance ? '✓' : '✕'}
                  </span>
                  <span className="text-night/60 dark:text-cream/60">Tone</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={validation.cultural_appropriateness ? 'text-marsh' : 'text-cajun-red'}>
                    {validation.cultural_appropriateness ? '✓' : '✕'}
                  </span>
                  <span className="text-night/60 dark:text-cream/60">Culture</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={validation.brand_consistency ? 'text-marsh' : 'text-cajun-red'}>
                    {validation.brand_consistency ? '✓' : '✕'}
                  </span>
                  <span className="text-night/60 dark:text-cream/60">Brand</span>
                </div>
              </div>

              {validation.suggestions?.length > 0 && (
                <div className="text-xs text-night/60 dark:text-cream/60">
                  💡 {validation.suggestions[0]}
                </div>
              )}
            </div>
          )}

          {/* Hashtags */}
          <div>
            <label className="block text-sm font-medium text-night dark:text-cream mb-2">
              Hashtags
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={hashtagInput}
                onChange={(e) => setHashtagInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addHashtag()}
                placeholder="Add hashtag"
                className="flex-1 px-4 py-2 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream"
              />
              <button onClick={addHashtag} className="btn-secondary px-4">
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {editedContent.hashtags?.map((tag, i) => (
                <span 
                  key={i} 
                  className="px-2 py-1 bg-bayou/10 text-bayou text-sm rounded-full flex items-center gap-1"
                >
                  {tag}
                  <button onClick={() => removeHashtag(tag)} className="hover:text-cajun-red">
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-between gap-3 p-6 border-t border-cream-dark dark:border-night">
          <button
            onClick={handleValidate}
            disabled={validating}
            className="btn-outline flex items-center gap-2"
          >
            {validating ? '⚙️ Validating...' : '✓ Validate'}
          </button>
          <div className="flex gap-3">
            <button onClick={onClose} className="btn-ghost">
              Cancel
            </button>
            <button 
              onClick={() => onSave(editedContent)} 
              className="btn-primary"
              disabled={!editedContent.text}
            >
              Save Content
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main Content Management Page
export default function ContentPage() {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showGenerator, setShowGenerator] = useState(false);
  const [showEditor, setShowEditor] = useState(false);
  const [editingContent, setEditingContent] = useState(null);

  useEffect(() => {
    fetchContent();
  }, [filter]);

  const fetchContent = async () => {
    setLoading(true);
    try {
      let url = `${API_BASE}/api/v1/content`;
      if (filter !== 'all') {
        url += `?status=${filter}`;
      }
      
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setContent(data.content || []);
      }
    } catch (error) {
      console.error('Error fetching content:', error);
      // Use mock data in development
      setContent([
        {
          id: '1',
          text: "Fresh mudbugs just arrived from Louisiana waters! 🦞 Seasoned with our family's secret blend since 1973. Come get 'em while they're hot, cher!",
          content_type: 'crawfish_content',
          platforms: ['instagram', 'facebook', 'tiktok'],
          status: 'approved',
          hashtags: ['#CrawfishSeason', '#Mudbugs', '#CajunFood', '#Louisiana'],
          validation: { authenticity_score: 0.94 },
          created_at: new Date().toISOString()
        },
        {
          id: '2',
          text: "Live zydeco tonight starting at 7pm! Bring your dancing shoes and an appetite. Laissez les bon temps rouler! 🎵",
          content_type: 'evening_event',
          platforms: ['facebook', 'instagram'],
          status: 'scheduled',
          hashtags: ['#LiveMusic', '#Zydeco', '#BreauxBridge'],
          validation: { authenticity_score: 0.88 },
          created_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: '3',
          text: "Good morning, cher! The coffee's hot and the roux is bubbling. Come start your day with us!",
          content_type: 'morning_greeting',
          platforms: ['instagram', 'facebook'],
          status: 'draft',
          hashtags: ['#GoodMorning', '#CajunBreakfast'],
          validation: { authenticity_score: 0.72 },
          created_at: new Date(Date.now() - 172800000).toISOString()
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratedContent = async (generatedContent) => {
    // Save the generated content
    try {
      const res = await fetch(`${API_BASE}/api/v1/content`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(generatedContent)
      });
      
      if (res.ok) {
        fetchContent();
      }
    } catch (error) {
      console.error('Error saving content:', error);
    }
  };

  const handleSaveContent = async (editedContent) => {
    try {
      const method = editedContent.id ? 'PUT' : 'POST';
      const url = editedContent.id 
        ? `${API_BASE}/api/v1/content/${editedContent.id}`
        : `${API_BASE}/api/v1/content`;
      
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editedContent)
      });
      
      if (res.ok) {
        fetchContent();
        setShowEditor(false);
        setEditingContent(null);
      }
    } catch (error) {
      console.error('Error saving content:', error);
    }
  };

  const handleEdit = (content) => {
    setEditingContent(content);
    setShowEditor(true);
  };

  const handleDelete = async (contentId) => {
    if (confirm('Are you sure you want to delete this content?')) {
      try {
        await fetch(`${API_BASE}/api/v1/content/${contentId}`, { method: 'DELETE' });
        fetchContent();
      } catch (error) {
        console.error('Error deleting content:', error);
      }
    }
  };

  const handleValidate = async (contentId) => {
    // Trigger validation
    fetchContent();
  };

  const handleSchedule = (contentId) => {
    // Open schedule modal
    alert(`Schedule content: ${contentId}`);
  };

  const filteredContent = content.filter(c => {
    if (searchQuery) {
      return c.text?.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  const statusCounts = {
    all: content.length,
    draft: content.filter(c => c.status === 'draft').length,
    pending_review: content.filter(c => c.status === 'pending_review').length,
    approved: content.filter(c => c.status === 'approved').length,
    scheduled: content.filter(c => c.status === 'scheduled').length,
    published: content.filter(c => c.status === 'published').length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-bold text-night dark:text-cream">
            Content Management
          </h1>
          <p className="text-night/60 dark:text-cream/60 mt-1">
            Create, edit, and manage your social media content
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => {
              setEditingContent(null);
              setShowEditor(true);
            }}
            className="btn-outline flex items-center gap-2"
          >
            📝 Create Manual
          </button>
          <button 
            onClick={() => setShowGenerator(true)}
            className="btn-primary flex items-center gap-2"
          >
            ✨ AI Generate
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="card !p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search content..."
              className="w-full px-4 py-2 rounded-lg border border-cream-dark dark:border-night bg-white dark:bg-night text-night dark:text-cream"
            />
          </div>
          
          {/* Status Filter */}
          <div className="flex flex-wrap gap-2">
            {Object.entries(statusCounts).map(([status, count]) => (
              <button
                key={status}
                onClick={() => setFilter(status)}
                className={`px-3 py-2 rounded-lg text-sm transition-all ${
                  filter === status
                    ? 'bg-cajun-red text-white'
                    : 'bg-cream-dark dark:bg-night text-night/70 dark:text-cream/70 hover:bg-cream-warm dark:hover:bg-night-light'
                }`}
              >
                {status === 'all' ? 'All' : status.replace('_', ' ')} ({count})
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <div key={i} className="card animate-pulse">
              <div className="h-4 bg-cream-dark dark:bg-night rounded w-1/3 mb-4"></div>
              <div className="h-20 bg-cream-dark dark:bg-night rounded mb-4"></div>
              <div className="h-2 bg-cream-dark dark:bg-night rounded w-full mb-2"></div>
              <div className="h-8 bg-cream-dark dark:bg-night rounded w-2/3"></div>
            </div>
          ))}
        </div>
      ) : filteredContent.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredContent.map(item => (
            <ContentCard
              key={item.id}
              content={item}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onSchedule={handleSchedule}
              onValidate={handleValidate}
            />
          ))}
        </div>
      ) : (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">📝</div>
          <h3 className="text-lg font-semibold text-night dark:text-cream mb-2">
            No content found
          </h3>
          <p className="text-night/60 dark:text-cream/60 mb-4">
            {searchQuery ? 'Try a different search term' : 'Create your first piece of content'}
          </p>
          <button 
            onClick={() => setShowGenerator(true)}
            className="btn-primary"
          >
            ✨ Generate Content with AI
          </button>
        </div>
      )}

      {/* Modals */}
      <ContentGeneratorModal
        isOpen={showGenerator}
        onClose={() => setShowGenerator(false)}
        onGenerate={handleGeneratedContent}
      />
      
      <ContentEditorModal
        isOpen={showEditor}
        onClose={() => {
          setShowEditor(false);
          setEditingContent(null);
        }}
        content={editingContent}
        onSave={handleSaveContent}
      />
    </div>
  );
}
