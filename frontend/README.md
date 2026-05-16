# IBM Dexter - AI-Powered Code Review Platform (Frontend)

> Enterprise-grade React frontend built with IBM Carbon Design System

[![React](https://img.shields.io/badge/React-18.3-blue.svg)](https://reactjs.org/)
[![Carbon Design](https://img.shields.io/badge/Carbon-11.x-purple.svg)](https://carbondesignsystem.com/)
[![Vite](https://img.shields.io/badge/Vite-5.x-yellow.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Component Library](#component-library)
- [Testing](#testing)
- [Theming](#theming)
- [Development Workflow](#development-workflow)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

IBM Dexter Frontend is a modern, enterprise-grade React application that provides an intuitive interface for AI-powered code review and analysis. Built with IBM Carbon Design System, it delivers a consistent, accessible, and professional user experience that matches IBM Cloud Console quality standards.

### Key Highlights

- **9 Comprehensive Pages**: Dashboard, Pull Requests, Review Details, Architecture, Security, Knowledge Base, Team Analytics, AI Agents, and Settings
- **7 Reusable UI Components**: LoadingState, EmptyState, ErrorState, StatusBadge, SeverityTag, MetricCard, ChartContainer
- **Full Testing Infrastructure**: Vitest, React Testing Library, 70%+ coverage target
- **IBM Carbon Design**: Complete implementation with g100 dark theme
- **Mock Data System**: Fully functional without backend dependency
- **Responsive Design**: Mobile-first approach with breakpoints
- **Accessibility**: WCAG 2.1 AA compliant

## ✨ Features

### Core Functionality

- **Dashboard**: Real-time KPIs, trends, and activity monitoring
- **Pull Request Management**: List, filter, and review pull requests
- **Detailed Reviews**: In-depth code analysis with findings and metrics
- **Architecture Insights**: Pattern detection and dependency analysis
- **Security Scanning**: Vulnerability detection with severity levels
- **Knowledge Base**: Searchable documentation and best practices
- **Team Analytics**: Performance metrics and collaboration insights
- **AI Agents**: Multi-agent system monitoring and configuration
- **Settings**: User preferences and system configuration

### UI/UX Features

- Dark theme (g100) with light theme support
- Smooth page transitions and animations
- Loading states and skeleton screens
- Empty states with helpful messages
- Error boundaries with recovery options
- Toast notifications
- Responsive navigation
- Keyboard shortcuts

## 🛠 Technology Stack

### Core Technologies

- **React 18.3**: Modern React with hooks and concurrent features
- **Vite 5.x**: Lightning-fast build tool and dev server
- **React Router 6**: Client-side routing
- **IBM Carbon Design System 11.x**: Enterprise UI components
- **Sass**: CSS preprocessing with Carbon tokens

### Development Tools

- **Vitest**: Fast unit testing framework
- **React Testing Library**: Component testing utilities
- **ESLint**: Code linting and quality
- **Framer Motion**: Animation library (optional)
- **PropTypes**: Runtime type checking

### State Management

- **Zustand**: Lightweight state management (theme store)
- **React Hooks**: Local component state

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ or 20+
- npm 9+ or yarn 1.22+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   VITE_APP_TITLE=IBM Dexter
   VITE_ENABLE_MOCK_DATA=true
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```
   
   Open [http://localhost:5173](http://localhost:5173) in your browser.

### Quick Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run preview          # Preview production build

# Testing
npm run test             # Run tests
npm run test:ui          # Run tests with UI
npm run test:coverage    # Generate coverage report

# Code Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix ESLint issues
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── Dexter_logo.png    # App logo
│   ├── favicon.svg        # Favicon
│   └── icons.svg          # Icon sprites
├── src/
│   ├── assets/            # Images and media
│   ├── components/        # React components
│   │   ├── layout/        # Layout components
│   │   │   ├── AppHeader.jsx
│   │   │   ├── SideNav.jsx
│   │   │   └── MainLayout.jsx
│   │   ├── ui/            # Reusable UI components
│   │   │   ├── LoadingState.jsx
│   │   │   ├── EmptyState.jsx
│   │   │   ├── ErrorState.jsx
│   │   │   ├── StatusBadge.jsx
│   │   │   ├── SeverityTag.jsx
│   │   │   ├── MetricCard.jsx
│   │   │   ├── ChartContainer.jsx
│   │   │   └── index.js
│   │   └── ErrorBoundary.jsx
│   ├── pages/             # Page components
│   │   ├── Dashboard/
│   │   ├── PullRequests/
│   │   ├── ReviewDetail/
│   │   ├── Architecture/
│   │   ├── Security/
│   │   ├── KnowledgeBase/
│   │   ├── TeamAnalytics/
│   │   ├── AIAgents/
│   │   └── Settings/
│   ├── services/          # API services
│   │   ├── api.js         # API client
│   │   └── platformService.js
│   ├── mocks/             # Mock data
│   │   └── platformData.js
│   ├── store/             # State management
│   │   └── useThemeStore.js
│   ├── utils/             # Utilities
│   │   ├── animations.js
│   │   └── testUtils.jsx
│   ├── hooks/             # Custom hooks
│   ├── constants/         # Constants
│   │   └── appConstants.js
│   ├── theme/             # Theme configuration
│   │   └── carbonThemes.js
│   ├── styles/            # Global styles
│   │   └── App.scss
│   ├── App.jsx            # Root component
│   ├── main.jsx           # Entry point
│   └── setupTests.js      # Test setup
├── .env                   # Environment variables
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── eslint.config.js      # ESLint configuration
├── index.html            # HTML template
├── package.json          # Dependencies
├── vite.config.js        # Vite configuration
├── vitest.config.js      # Vitest configuration
└── README.md             # This file
```

## 🏗 Architecture

### Component Architecture

```
App (ErrorBoundary)
├── MainLayout
│   ├── AppHeader (theme toggle, user menu)
│   ├── SideNav (navigation)
│   └── Content (page routes)
│       ├── Dashboard
│       ├── PullRequests
│       ├── ReviewDetail
│       ├── Architecture
│       ├── Security
│       ├── KnowledgeBase
│       ├── TeamAnalytics
│       ├── AIAgents
│       └── Settings
```

### Data Flow

1. **Component** → Calls service method
2. **Service** → Checks if backend available
3. **Service** → Returns real data OR mock data
4. **Component** → Updates state
5. **Component** → Renders UI

### State Management

- **Global State**: Theme (Zustand)
- **Local State**: Component-specific (useState, useReducer)
- **Server State**: API data (services)

### Routing

```javascript
/ → Dashboard
/pull-requests → Pull Requests List
/pull-requests/:id → Review Detail
/architecture → Architecture Insights
/security → Security Findings
/knowledge-base → Knowledge Base
/team-analytics → Team Analytics
/ai-agents → AI Agents
/settings → Settings
```

## 🧩 Component Library

### LoadingState

Consistent loading states across the app.

```jsx
import { LoadingState } from '@/components/ui';

<LoadingState variant="card" count={3} />
<LoadingState variant="table" count={5} />
<LoadingState variant="page" />
<LoadingState variant="list" count={4} />
```

**Props:**
- `variant`: 'card' | 'table' | 'page' | 'list'
- `count`: number of skeleton items
- `className`: additional CSS classes

### EmptyState

Consistent empty states with actions.

```jsx
import { EmptyState } from '@/components/ui';

<EmptyState
  variant="no-data"
  title="No pull requests"
  message="Create your first pull request to get started"
  actionLabel="Create PR"
  onAction={() => navigate('/create')}
/>
```

**Props:**
- `variant`: 'no-data' | 'no-results' | 'no-access'
- `title`: string
- `message`: string
- `actionLabel`: string (optional)
- `onAction`: function (optional)
- `icon`: custom icon component (optional)

### ErrorState

Error handling with retry functionality.

```jsx
import { ErrorState } from '@/components/ui';

<ErrorState
  error={error}
  onRetry={handleRetry}
  showDetails={true}
/>
```

**Props:**
- `error`: Error object or string
- `onRetry`: function (optional)
- `showDetails`: boolean (default: false)

### StatusBadge

Status indicators with animations.

```jsx
import { StatusBadge } from '@/components/ui';

<StatusBadge status="success" label="Completed" />
<StatusBadge status="in-progress" label="Running" pulse />
<StatusBadge status="error" label="Failed" />
```

**Props:**
- `status`: 'success' | 'warning' | 'error' | 'info' | 'in-progress'
- `label`: string
- `icon`: custom icon (optional)
- `pulse`: boolean (default: false)

### SeverityTag

Security/issue severity indicators.

```jsx
import { SeverityTag } from '@/components/ui';

<SeverityTag severity="critical" count={3} />
<SeverityTag severity="high" showLabel />
<SeverityTag severity="medium" />
<SeverityTag severity="low" />
```

**Props:**
- `severity`: 'critical' | 'high' | 'medium' | 'low'
- `count`: number (optional)
- `showLabel`: boolean (default: true)

### MetricCard

KPI cards with trends.

```jsx
import { MetricCard } from '@/components/ui';

<MetricCard
  title="Total PRs"
  value={156}
  trend={{ direction: 'up', value: '+12%' }}
  icon={DocumentIcon}
  onClick={() => navigate('/pull-requests')}
/>
```

**Props:**
- `title`: string
- `value`: string | number
- `trend`: { direction: 'up' | 'down', value: string } (optional)
- `icon`: icon component (optional)
- `onClick`: function (optional)
- `loading`: boolean (default: false)

### ChartContainer

Wrapper for charts with loading/error states.

```jsx
import { ChartContainer } from '@/components/ui';

<ChartContainer
  title="Review Trends"
  description="Last 30 days"
  loading={loading}
  error={error}
  onRefresh={handleRefresh}
  onExport={handleExport}
>
  <YourChartComponent />
</ChartContainer>
```

**Props:**
- `title`: string
- `description`: string (optional)
- `loading`: boolean
- `error`: Error | string
- `onRefresh`: function (optional)
- `onExport`: function (optional)
- `children`: React node

### ErrorBoundary

Catches and handles React errors.

```jsx
import ErrorBoundary from '@/components/ErrorBoundary';

<ErrorBoundary
  title="Something went wrong"
  message="Please try refreshing the page"
  showDetails={true}
  onError={(error, errorInfo) => logError(error)}
>
  <YourComponent />
</ErrorBoundary>
```

**Props:**
- `children`: React node
- `fallback`: custom fallback UI (optional)
- `title`: string (optional)
- `message`: string (optional)
- `showDetails`: boolean (default: dev mode only)
- `showHomeButton`: boolean (default: true)
- `onError`: function (optional)
- `onReset`: function (optional)

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with UI
npm run test:ui

# Generate coverage report
npm run test:coverage

# Run specific test file
npm run test src/components/ui/LoadingState.test.jsx
```

### Writing Tests

```javascript
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '@/utils/testUtils';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    renderWithProviders(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });

  it('handles user interaction', async () => {
    const { user } = renderWithProviders(<MyComponent />);
    await user.click(screen.getByRole('button'));
    expect(screen.getByText('Clicked')).toBeInTheDocument();
  });
});
```

### Test Utilities

```javascript
import {
  renderWithProviders,
  renderWithTheme,
  mockData,
  mockApiResponses,
  createMockFetch,
} from '@/utils/testUtils';

// Render with router and theme
renderWithProviders(<Component />, {
  theme: 'g100',
  route: '/dashboard',
});

// Render with theme only
renderWithTheme(<Component />, { theme: 'white' });

// Use mock data
const pr = mockData.pullRequest;

// Mock API responses
fetch.mockResolvedValue(mockApiResponses.success(data));
```

### Coverage Goals

- **Lines**: 70%+
- **Functions**: 70%+
- **Branches**: 70%+
- **Statements**: 70%+

## 🎨 Theming

### Available Themes

- **g100** (default): Dark theme
- **g90**: Dark theme (lighter)
- **g10**: Light theme (darker)
- **white**: Light theme

### Using Themes

```javascript
import { useThemeStore } from '@/store/useThemeStore';

function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();
  
  return (
    <button onClick={() => setTheme(theme === 'g100' ? 'white' : 'g100')}>
      Toggle Theme
    </button>
  );
}
```

### Custom Styling

```scss
@use '@carbon/react/scss/spacing' as *;
@use '@carbon/react/scss/theme' as *;
@use '@carbon/react/scss/type' as *;

.my-component {
  padding: $spacing-05;
  background: $layer-01;
  color: $text-primary;
  
  @include type-style('heading-03');
}
```

### Carbon Tokens

- **Spacing**: `$spacing-01` to `$spacing-13`
- **Colors**: `$layer-01`, `$text-primary`, `$icon-secondary`, etc.
- **Typography**: `@include type-style('heading-03')`
- **Motion**: `$duration-fast-01`, `$duration-moderate-01`, etc.

## 💻 Development Workflow

### Code Style

- Use functional components with hooks
- Follow Carbon Design patterns
- Use PropTypes for type checking
- Write descriptive component names
- Keep components small and focused
- Use SCSS modules for styling

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
```

### Commit Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Tests
- `chore:` Maintenance

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console errors
- [ ] Accessibility checked
- [ ] Responsive design verified
- [ ] PropTypes added
- [ ] Error handling implemented

## 🚢 Deployment

### Build for Production

```bash
# Build optimized bundle
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Production `.env`:
```env
VITE_API_URL=https://api.dexter.ibm.com/api/v1
VITE_APP_TITLE=IBM Dexter
VITE_ENABLE_MOCK_DATA=false
```

### Deployment Targets

- **Vercel**: `vercel deploy`
- **Netlify**: `netlify deploy`
- **AWS S3**: Upload `dist/` folder
- **IBM Cloud**: Use Cloud Foundry or Kubernetes

### Performance Optimization

- Code splitting with React.lazy()
- Image optimization
- Bundle size monitoring
- CDN for static assets
- Gzip compression
- Cache headers

## 🔧 Troubleshooting

### Common Issues

**Issue**: `npm install` fails
```bash
# Solution: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Issue**: Port 5173 already in use
```bash
# Solution: Use different port
npm run dev -- --port 3000
```

**Issue**: Tests failing
```bash
# Solution: Clear test cache
npm run test -- --clearCache
```

**Issue**: Build errors
```bash
# Solution: Check for TypeScript/ESLint errors
npm run lint
npm run build -- --debug
```

### Debug Mode

```bash
# Enable debug logging
VITE_DEBUG=true npm run dev

# Verbose build output
npm run build -- --debug
```

### Getting Help

- Check [Carbon Design System docs](https://carbondesignsystem.com/)
- Review [React docs](https://react.dev/)
- Search [GitHub issues](https://github.com/your-repo/issues)
- Contact team on Slack

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/dexter-frontend.git
cd dexter-frontend

# Install dependencies
npm install

# Create branch
git checkout -b feature/my-feature

# Make changes and test
npm run test
npm run lint

# Commit and push
git commit -m "feat: add feature"
git push origin feature/my-feature
```

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- IBM Carbon Design System team
- React team
- Vite team
- All contributors

---

**Built with ❤️ by the IBM Dexter Team**

For more information, visit [IBM Dexter Documentation](https://dexter.ibm.com/docs)
