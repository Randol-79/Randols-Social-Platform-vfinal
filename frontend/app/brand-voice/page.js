'use client';

import { useState, useEffect } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

// V.A.U.L.T. Framework Data
const VAULT_FRAMEWORK = {
  V: {
    title: 'Voice Foundation',
    description: 'Authentic Louisiana Cajun hospitality',
    items: ['Warm & welcoming', 'Proud of heritage', 'Musical soul', 'Family-oriented', 'Community-focused']
  },
  A: {
    title: 'Audience Resonance',
    description: 'Adapt tone for different audiences',
    items: ['Local regulars: Casual, insider', 'Tourists: Educational', 'Foodies: Technical + story', 'Families: Memory-focused']
  },
  U: {
    title: 'Unique Louisiana Flavor',
    description: 'Signature expressions and references',
    items: ["Y'all", 'Cher', 'Laissez les bon temps rouler', 'Zydeco', 'Bayou']
  },
  L: {
    title: 'Language Guidelines',
    description: 'What to use and avoid',
    items: ['Natural Cajun expressions', 'Storytelling approach', 'Avoid stereotypes', 'No corporate language']
  },
  T: {
    title: 'Tone Spectrum',
    description: 'Range of voice styles',
    items: ['Casual local', 'Welcoming tourist', 'Educational', 'Celebratory']
  }
};

const APPROVED_PHRASES = [
  { phrase: "Come see us, cher!", usage: 'high', context: 'Invitations' },
  { phrase: "Laissez les bon temps rouler!", usage: 'medium', context: 'Celebrations' },
  { phrase: "That's some kinda good!", usage: 'high', context: 'Food descriptions' },
  { phrase: "Where y'at?", usage: 'medium', context: 'Greetings' },
  { phrase: "Passed down through generations", usage: 'medium', context: 'Heritage' },
  { phrase: "Fresh from local waters", usage: 'high', context: 'Seafood' },
  { phrase: "Y'all come eat with us", usage: 'high', context: 'Invitations' },
  { phrase: "That gumbo sings!", usage: 'low', context: 'Food descriptions' }
];

const CULTURAL_EVENTS = [
  { date: 'Mar 1-4', name: 'Mardi Gras Season', type: 'holiday', content_boost: '2x' },
  { date: 'Mar-Jun', name: 'Crawfish Season', type: 'seasonal', content_boost: '1.5x' },
  { date: 'Oct', name: 'Festivals Acadiens', type: 'festival', content_boost: '1.5x' },
  { date: 'May', name: 'Breaux Bridge Crawfish Festival', type: 'local', content_boost: '2x' }
];

function VaultCard({ letter, data }) {
  const colors = {
    V: 'from-cajun-red to-roux',
    A: 'from-bayou to-teal-600',
    U: 'from-gold to-amber-500',
    L: 'from-marsh to-green-600',
    T: 'from-purple-600 to-pink-500'
  };

  return (
    <div className="card">
      <div className="flex items-start gap-4 mb-4">
        <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${colors[letter]} flex items-center justify-center text-white text-2xl font-bold shadow-lg`}>
          {letter}
        </div>
        <div>
          <h3 className="font-semibold text-night dark:text-cream">{data.title}</h3>
          <p className="text-sm text-night/60 dark:text-cream/60">{data.description}</p>
        </div>
      </div>
      <ul className="space-y-2">
        {data.items.map((item, idx) => (
          <li key={idx} className="flex items-center gap-2 text-sm text-night/70 dark:text-cream/70">
            <span className="text-marsh">✓</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function VoiceScoreCard({ score, label, threshold }) {
  const percentage = score * 100;
  const isGood = score >= threshold;
  
  return (
    <div className="bg-cream-warm dark:bg-night rounded-xl p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-night/60 dark:text-cream/60">{label}</span>
        <span className={`text-lg font-bold ${isGood ? 'text-marsh' : 'text-gold'}`}>{percentage.toFixed(0)}%</span>
      </div>
      <div className="h-2 bg-cream-dark dark:bg-night-light rounded-full overflow-hidden">
        <div 
          className={`h-full rounded-full transition-all duration-500 ${isGood ? 'bg-marsh' : 'bg-gold'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-xs text-night/40 dark:text-cream/40">0%</span>
        <span className="text-xs text-night/40 dark:text-cream/40">Threshold: {threshold * 100}%</span>
        <span className="text-xs text-night/40 dark:text-cream/40">100%</span>
      </div>
    </div>
  );
}

function PhraseCard({ phrase, usage, context }) {
  const usageColors = {
    high: 'bg-marsh/10 text-marsh',
    medium: 'bg-bayou/10 text-bayou',
    low: 'bg-gold/10 text-gold'
  };

  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-cream-warm dark:bg-night">
      <div>
        <p className="font-medium text-night dark:text-cream">"{phrase}"</p>
        <p className="text-xs text-night/50 dark:text-cream/50">{context}</p>
      </div>
      <span className={`px-2 py-1 rounded-full text-xs capitalize ${usageColors[usage]}`}>
        {usage}
      </span>
    </div>
  );
}

function ContentTester({ onTest }) {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleTest = async () => {
    if (!text.trim()) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/brand/voice-score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      }
    } catch (error) {
      console.error('Error testing content:', error);
      // Mock result
      setResult({
        score: 0.72,
        issues: ['Could use more Louisiana references'],
        recommendations: ["Add authentic phrases like 'cher' or 'y'all'", 'Include cultural references']
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEnhance = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/content/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      
      if (res.ok) {
        const data = await res.json();
        setText(data.enhanced_text);
        setResult({
          score: data.authenticity_score,
          issues: [],
          recommendations: ['Content enhanced with Cajun authenticity!']
        });
      }
    } catch (error) {
      console.error('Error enhancing content:', error);
    }
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Content Voice Tester</h3>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Enter content to test for Cajun authenticity..."
        className="w-full h-32 p-4 rounded-lg bg-cream-warm dark:bg-night border border-cream-dark dark:border-night text-night dark:text-cream resize-none"
      />
      
      <div className="flex gap-3 mt-4">
        <button 
          onClick={handleTest} 
          disabled={!text.trim() || loading}
          className="btn-primary flex-1"
        >
          {loading ? 'Testing...' : 'Test Voice'}
        </button>
        <button 
          onClick={handleEnhance}
          disabled={!text.trim() || loading}
          className="btn-outline flex-1"
        >
          Enhance Content
        </button>
      </div>

      {result && (
        <div className="mt-4 p-4 rounded-lg bg-cream-warm dark:bg-night">
          <div className="flex items-center justify-between mb-3">
            <span className="font-medium text-night dark:text-cream">Authenticity Score</span>
            <span className={`text-2xl font-bold ${result.score >= 0.75 ? 'text-marsh' : result.score >= 0.5 ? 'text-gold' : 'text-cajun-red'}`}>
              {(result.score * 100).toFixed(0)}%
            </span>
          </div>
          
          {result.issues?.length > 0 && (
            <div className="mb-3">
              <p className="text-sm font-medium text-night/70 dark:text-cream/70 mb-1">Issues:</p>
              <ul className="space-y-1">
                {result.issues.map((issue, idx) => (
                  <li key={idx} className="text-sm text-cajun-red flex items-center gap-2">
                    <span>⚠️</span> {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {result.recommendations?.length > 0 && (
            <div>
              <p className="text-sm font-medium text-night/70 dark:text-cream/70 mb-1">Recommendations:</p>
              <ul className="space-y-1">
                {result.recommendations.map((rec, idx) => (
                  <li key={idx} className="text-sm text-bayou flex items-center gap-2">
                    <span>💡</span> {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CulturalCalendar({ events }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Cultural Events Calendar</h3>
      <div className="space-y-3">
        {events.map((event, idx) => (
          <div key={idx} className="flex items-center gap-4 p-3 rounded-lg bg-cream-warm dark:bg-night">
            <div className="w-16 text-center">
              <p className="text-xs text-night/50 dark:text-cream/50">{event.date}</p>
            </div>
            <div className="flex-1">
              <p className="font-medium text-night dark:text-cream">{event.name}</p>
              <p className="text-xs text-night/50 dark:text-cream/50 capitalize">{event.type}</p>
            </div>
            <span className="px-2 py-1 bg-cajun-red/10 text-cajun-red text-xs rounded-full">
              {event.content_boost}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function BrandVoicePage() {
  const [voiceMetrics, setVoiceMetrics] = useState({
    authenticity: 0.87,
    cultural_relevance: 0.92,
    tone_consistency: 0.84
  });
  const [guidelines, setGuidelines] = useState(null);

  useEffect(() => {
    fetchBrandGuidelines();
  }, []);

  const fetchBrandGuidelines = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/brand/guidelines`);
      if (res.ok) {
        const data = await res.json();
        setGuidelines(data);
      }
    } catch (error) {
      console.error('Error fetching guidelines:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-display font-bold text-night dark:text-cream">Brand Voice Monitor</h2>
        <p className="text-night/50 dark:text-cream/50">Maintain authentic Cajun voice using the V.A.U.L.T. framework</p>
      </div>

      {/* Voice Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <VoiceScoreCard score={voiceMetrics.authenticity} label="Authenticity Score" threshold={0.75} />
        <VoiceScoreCard score={voiceMetrics.cultural_relevance} label="Cultural Relevance" threshold={0.80} />
        <VoiceScoreCard score={voiceMetrics.tone_consistency} label="Tone Consistency" threshold={0.75} />
      </div>

      {/* V.A.U.L.T. Framework */}
      <div>
        <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">V.A.U.L.T. Framework</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(VAULT_FRAMEWORK).map(([letter, data]) => (
            <VaultCard key={letter} letter={letter} data={data} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Content Tester */}
        <ContentTester />

        {/* Approved Phrases */}
        <div className="card">
          <h3 className="text-lg font-semibold text-night dark:text-cream mb-4">Approved Louisiana Phrases</h3>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {APPROVED_PHRASES.map((phrase, idx) => (
              <PhraseCard key={idx} {...phrase} />
            ))}
          </div>
        </div>
      </div>

      {/* Cultural Calendar */}
      <CulturalCalendar events={CULTURAL_EVENTS} />

      {/* Quick Reference */}
      <div className="card bg-cajun-gradient text-white">
        <h3 className="text-lg font-semibold mb-4">Quick Voice Reference</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <p className="text-white/70 text-sm mb-2">Always Use</p>
            <ul className="space-y-1 text-sm">
              <li>✓ Y'all (for groups)</li>
              <li>✓ Cher (term of endearment)</li>
              <li>✓ Louisiana references</li>
              <li>✓ Family/tradition stories</li>
            </ul>
          </div>
          <div>
            <p className="text-white/70 text-sm mb-2">Never Use</p>
            <ul className="space-y-1 text-sm">
              <li>✕ Hillbilly/redneck</li>
              <li>✕ Over-exaggerated dialect</li>
              <li>✕ Corporate language</li>
              <li>✕ Generic Southern phrases</li>
            </ul>
          </div>
          <div>
            <p className="text-white/70 text-sm mb-2">Signature Phrases</p>
            <ul className="space-y-1 text-sm">
              <li>• Laissez les bon temps rouler!</li>
              <li>• Come see us, cher!</li>
              <li>• That's some kinda good!</li>
              <li>• Where y'at?</li>
            </ul>
          </div>
          <div>
            <p className="text-white/70 text-sm mb-2">Cultural References</p>
            <ul className="space-y-1 text-sm">
              <li>• Zydeco music</li>
              <li>• Crawfish/mudbugs</li>
              <li>• Bayou/Acadiana</li>
              <li>• Mardi Gras</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
