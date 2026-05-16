# IBM Dexter AI Code Reviewer - Frontend

A production-ready React frontend for IBM Dexter AI Code Reviewer, built with Vite and IBM Carbon Design System.

## 🚀 Features

- **IBM Carbon Design System** - Professional enterprise UI components
- **Theme Switching** - Light (white) and Dark (g100) themes with smooth transitions
- **IBM Gradients & Animations** - Beautiful gradient cards and subtle animations
- **Responsive Design** - Mobile-first approach with Carbon Grid system
- **Real-time Analytics** - Dashboard with metrics and insights
- **Code Review Interface** - Detailed review findings with severity indicators
- **AI Reasoning Display** - Transparent AI decision-making process
- **Accessibility** - WCAG 2.1 AA compliant with keyboard navigation

## 📦 Tech Stack

- **React 18** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **IBM Carbon React** - Complete Carbon component library
- **React Router DOM** - Client-side routing
- **Zustand** - Lightweight state management
- **React Query** - Server state management and caching
- **Axios** - HTTP client for API calls
- **Sass** - CSS preprocessing with Carbon tokens

## 🛠️ Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🌐 Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/          # Layout components (Header, SideNav)
│   │   ├── features/        # Feature-specific components
│   │   └── ui/              # Reusable UI components
│   ├── pages/
│   │   ├── Dashboard/       # Dashboard with analytics
│   │   ├── ReviewDetail/    # Pull request review page
│   │   ├── Settings/        # Settings page
│   │   └── ...
│   ├── services/
│   │   └── api.js           # API service layer
│   ├── store/
│   │   └── useThemeStore.js # Theme state management
│   ├── styles/
│   │   └── App.scss         # Global styles with Carbon tokens
│   ├── App.jsx              # Main app component with routing
│   └── main.jsx             # Application entry point
├── public/                  # Static assets
├── .env                     # Environment variables
├── vite.config.js          # Vite configuration
└── package.json            # Dependencies and scripts
```

## 🎨 IBM Carbon Components Used

### Layout
- `Header`, `HeaderName`, `HeaderGlobalBar`, `HeaderGlobalAction`
- `SideNav`, `SideNavItems`, `SideNavLink`, `SideNavMenu`
- `Grid`, `Column`
- `Content`, `Theme`

### Data Display
- `Tile` - Cards and containers
- `DataTable` - Tabular data
- `Accordion`, `AccordionItem` - Collapsible content
- `Tag` - Status indicators
- `CodeSnippet` - Code display

### Forms
- `Form`, `FormGroup`
- `TextInput`, `Select`, `SelectItem`
- `Toggle`, `Button`

### Feedback
- `SkeletonText`, `SkeletonPlaceholder` - Loading states
- `Breadcrumb`, `BreadcrumbItem` - Navigation

### Icons (from @carbon/icons-react)
- `Dashboard`, `DocumentTasks`, `Catalog`, `DataBase`
- `Settings`, `ChartLineData`, `Notification`, `UserAvatar`
- `CheckmarkFilled`, `WarningAltFilled`, `ErrorFilled`
- `ArrowUp`, `ArrowDown`, `Light`, `Asleep`

## 🎨 IBM Gradients

The application uses official IBM Design Language gradients:

```scss
.gradient-blue {
  background: linear-gradient(135deg, #0f62fe 0%, #4589ff 100%);
}

.gradient-purple {
  background: linear-gradient(135deg, #8a3ffc 0%, #a56eff 100%);
}

.gradient-teal {
  background: linear-gradient(135deg, #007d79 0%, #009d9a 100%);
}

.gradient-cyan {
  background: linear-gradient(135deg, #1192e8 0%, #33b1ff 100%);
}
```

## 🌙 Theme System

The application supports IBM Carbon themes:

- **White Theme** (default) - Light theme with white background
- **G100 Theme** - Dark theme with black background

Theme switching is handled by Zustand store with persistence:

```javascript
import useThemeStore from './store/useThemeStore';

const { theme, toggleTheme } = useThemeStore();
```

## 📱 Responsive Design

Uses Carbon Grid system with breakpoints:

- **sm** (320px+) - Mobile devices
- **md** (672px+) - Tablets
- **lg** (1056px+) - Desktop

All components are responsive with proper column spans:

```jsx
<Grid narrow>
  <Column sm={4} md={4} lg={4}>
    <Tile>Content</Tile>
  </Column>
</Grid>
```

## 🔌 API Integration

The frontend connects to the backend API through a service layer:

```javascript
import { reviewsAPI, repositoriesAPI } from './services/api';

// Get all reviews
const reviews = await reviewsAPI.getAll();

// Get specific review
const review = await reviewsAPI.getById(id);
```

## 🎯 Key Pages

### Dashboard (`/`)
- Analytics cards with IBM gradients
- Recent reviews summary
- Security overview
- Architecture insights

### Review Detail (`/reviews/:id`)
- Detailed findings with severity indicators
- Code snippets and suggestions
- AI reasoning explanation
- Breadcrumb navigation

### Settings (`/settings`)
- User preferences
- Notification settings
- Integration configuration

## 🎨 Styling Guidelines

- **Use Carbon tokens exclusively** - No hardcoded values
- **Follow IBM spacing scale** - 8px increments
- **Use Carbon typography** - Type mixins for consistency
- **Implement smooth transitions** - Professional animations
- **Maintain theme compatibility** - Support light/dark themes

## 🚀 Development

```bash
# Start development server
npm run dev

# The app will be available at http://localhost:3000
# API proxy configured to http://localhost:8000
```

## 🏗️ Build

```bash
# Build for production
npm run build

# Output will be in the `dist` directory
```

## 🧪 Testing

```bash
# Run tests (when implemented)
npm run test

# Run linting
npm run lint
```

## 📋 TODO

- [ ] Add unit tests with Vitest
- [ ] Implement error boundaries
- [ ] Add more pages (Repositories, AI Memory)
- [ ] Enhance accessibility features
- [ ] Add PWA capabilities
- [ ] Implement real-time updates

## 🤝 Contributing

1. Follow IBM Carbon design patterns
2. Use Carbon components exclusively
3. Maintain responsive design
4. Test theme switching
5. Ensure accessibility compliance

## 📄 License

This project is part of IBM Dexter AI Code Reviewer.
