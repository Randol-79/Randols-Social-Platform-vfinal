# Randol's Marketing Dashboard - Frontend

## 🦞 Overview

Next.js 14 PWA dashboard for Randol's Restaurant's agentic social media marketing platform. Features real-time monitoring, AI content generation, content calendar management, and comprehensive analytics.

## ✨ Features

- **Dashboard** - Real-time metrics, agent status, and system alerts
- **Content Management** - AI-powered content generation and editing
- **Content Calendar** - Visual scheduling and calendar view
- **Analytics** - Performance metrics, trends, and recommendations
- **Agent Monitoring** - Status, logs, and configuration for all AI agents
- **Brand Voice** - V.A.U.L.T. framework guidelines and Cajun phrase library
- **Settings** - Platform configurations and preferences

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS with custom Cajun theme
- **State Management**: Zustand + React Query
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Real-time**: Socket.IO Client
- **PWA**: Service Worker + Web App Manifest

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.js           # Root layout with navigation
│   ├── page.js             # Dashboard home
│   ├── content/            # Content management
│   ├── calendar/           # Content calendar
│   ├── analytics/          # Performance analytics
│   ├── agents/             # Agent monitoring
│   ├── brand-voice/        # Brand guidelines
│   └── settings/           # Configuration
│
├── components/             # Reusable components
│   └── ui/                 # UI component library
│       └── index.js        # Toast, Modal, Cards, etc.
│
├── lib/                    # Utilities and hooks
│   └── api.js              # API client and hooks
│
├── public/                 # Static assets
│   ├── manifest.json       # PWA manifest
│   └── icons/              # App icons
│
├── styles/                 # Global styles
│   └── globals.css         # Tailwind + custom CSS
│
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind customization
└── package.json
```

## 🎨 Design System

### Brand Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Cajun Red | `#C0152F` | Primary, CTAs |
| Rust | `#A84B2F` | Secondary |
| Bayou | `#32808D` | Accents, links |
| Gold | `#D4AF37` | Highlights |
| Marsh | `#4A7C59` | Success states |
| Night | `#1A1B26` | Dark mode bg |
| Cream | `#FDF8F3` | Light mode bg |

### Typography

- **Display**: Playfair Display (headings)
- **Body**: Inter (text)

### Components

```jsx
// Toast notifications
import { useToast } from '@/components/ui';
const { addToast } = useToast();
addToast('Content saved!', 'success');

// Modal
import { Modal } from '@/components/ui';
<Modal isOpen={open} onClose={() => setOpen(false)} title="Edit Content">
  {/* content */}
</Modal>

// Stat cards
import { StatCard } from '@/components/ui';
<StatCard
  icon="❤️"
  label="Engagement Rate"
  value="4.2%"
  trend="up"
  trendValue="+0.3%"
/>
```

## 🔌 API Integration

### Using Hooks

```jsx
import { 
  useContent, 
  useSchedule, 
  useAnalyticsRange,
  generateContent 
} from '@/lib/api';

// Fetch content
const { data, loading, error, refetch } = useContent({ status: 'approved' });

// Generate AI content
const content = await generateContent({
  content_type: 'daily_special',
  platforms: ['instagram', 'facebook']
});
```

### API Client

```jsx
import { api } from '@/lib/api';

// Direct API calls
const response = await api.post('/api/v1/content', contentData);
const analytics = await api.get('/api/v1/analytics/daily');
```

## 📱 PWA Support

The dashboard is a Progressive Web App supporting:

- **Offline access** (service worker caching)
- **Install to home screen** (mobile & desktop)
- **Push notifications** (coming soon)
- **Background sync** (coming soon)

### Installation

1. Visit the dashboard in Chrome/Edge/Safari
2. Click "Install" in the address bar or menu
3. Access from your home screen/app drawer

## 🔄 Real-time Updates

### WebSocket Connection

```jsx
import { useWebSocket } from '@/lib/api';

const { connected, lastMessage } = useWebSocket(null, {
  onMessage: (data) => console.log('Update:', data)
});
```

### Polling Fallback

```jsx
import { usePolling } from '@/lib/api';

const { data } = usePolling(
  () => api.get('/api/v1/status'),
  30000 // 30 second interval
);
```

## 🌙 Dark Mode

Toggle dark mode with the moon/sun icon in the header. Preference is saved to localStorage.

```jsx
// Manual toggle
document.documentElement.classList.toggle('dark');
localStorage.setItem('theme', 'dark');
```

## 📊 Pages

### Dashboard (`/`)
- Key metrics overview
- Agent status cards
- System alerts
- Recent posts performance
- Quick actions (pause/resume, emergency post)

### Content (`/content`)
- Content library with filtering
- AI content generator modal
- Content editor with validation
- Cajun voice enhancement
- Authenticity scoring

### Calendar (`/calendar`)
- Weekly/monthly calendar view
- Drag-and-drop scheduling
- Platform color coding
- Post previews on hover

### Analytics (`/analytics`)
- Engagement trends chart
- Platform comparison
- Content type performance
- AI recommendations
- Weekly reports

### Agents (`/agents`)
- Agent status grid
- Activity logs
- Error tracking
- Configuration panels
- Restart/pause controls

### Brand Voice (`/brand-voice`)
- V.A.U.L.T. framework display
- Approved phrases library
- Cultural references guide
- Flagged phrases to avoid
- Voice testing tool

### Settings (`/settings`)
- API configuration
- Notification preferences
- Scheduling defaults
- Platform connections
- Emergency contacts

## 🧪 Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

### Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.randols-marketing.com
NEXT_PUBLIC_WS_URL=wss://api.randols-marketing.com
```

## 📝 Contributing

1. Create feature branch
2. Make changes
3. Run tests and lint
4. Submit PR

## 📄 License

Proprietary - Randol's Restaurant

---

**Laissez les bon temps rouler!** 🦞🎵
