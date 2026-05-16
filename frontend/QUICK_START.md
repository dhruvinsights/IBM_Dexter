# IBM Dexter Frontend - Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
The `.env` file is already configured with default values:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

### 3. Start Development Server
```bash
npm run dev
```

The application will be available at **http://localhost:3000**

## 🎯 What You'll See

### Dashboard (Home Page)
- **4 Gradient Metric Cards** - Total Reviews, Active Repos, Critical Issues, Resolved Issues
- **Recent Reviews** - List of latest code reviews with status
- **Security Overview** - Breakdown by severity (Critical, High, Medium, Low)
- **Architecture Insights** - Code quality, test coverage, documentation scores

### Navigation
- **Dashboard** - Analytics and overview
- **Reviews** - All reviews, pending, completed
- **Repositories** - Connected repositories
- **AI Memory** - Historical patterns
- **Analytics** - Detailed metrics
- **Settings** - User preferences

### Theme Toggle
Click the **moon/sun icon** in the header to switch between:
- ☀️ **Light Theme** (white) - Default
- 🌙 **Dark Theme** (g100) - Dark mode

## 🔧 Development Commands

```bash
# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint
```

## 📱 Responsive Testing

The app is fully responsive. Test at these breakpoints:
- **Mobile**: 375px (iPhone)
- **Tablet**: 768px (iPad)
- **Desktop**: 1280px+ (Standard desktop)

## 🎨 Key Features to Explore

### 1. Theme Switching
- Click the theme toggle in the header
- Theme preference is saved automatically
- All components adapt to the theme

### 2. IBM Gradients
- Metric cards use IBM gradient backgrounds
- Hover effects on cards
- Smooth animations

### 3. Navigation
- Click any sidebar item to navigate
- Breadcrumbs on detail pages
- Active state indicators

### 4. Review Details
- Click on any review to see details
- Expandable findings with severity
- Code snippets and suggestions

### 5. Settings
- Configure user preferences
- Toggle notifications
- Set up integrations

## 🔌 Backend Connection

The frontend expects the backend API at:
```
http://localhost:8000/api/v1
```

### Start the Backend
```bash
cd ../backend
python -m uvicorn main:app --reload
```

### API Endpoints Used
- `GET /api/v1/reviews` - List reviews
- `GET /api/v1/reviews/:id` - Review details
- `GET /api/v1/repositories` - List repositories
- `GET /health` - Health check

## 🎨 IBM Carbon Components

All UI components are from IBM Carbon Design System:
- **No custom UI components**
- **Only Carbon icons**
- **Carbon design tokens for styling**
- **Carbon grid system for layout**

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- --port 3001
```

### Dependencies Issues
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## 📚 Next Steps

1. **Explore the Dashboard** - See all metrics and analytics
2. **Check Review Details** - Click on any review
3. **Toggle Theme** - Try light and dark modes
4. **Adjust Settings** - Configure your preferences
5. **Test Responsive** - Resize browser window

## 🎓 Learn More

- [IBM Carbon Design System](https://carbondesignsystem.com/)
- [Carbon React Components](https://react.carbondesignsystem.com/)
- [Project README](./README.md)
- [Project Summary](./PROJECT_SUMMARY.md)

## 💡 Tips

- **Use keyboard navigation** - Tab through interactive elements
- **Check browser console** - See API calls and responses
- **Inspect with DevTools** - View Carbon component structure
- **Test accessibility** - Use screen reader or keyboard only

---

**Ready to code? Start the dev server and explore!** 🚀