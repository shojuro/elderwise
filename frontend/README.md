# ElderWise Frontend

A comprehensive, elderly-friendly React TypeScript frontend for the ElderWise AI companion system.

## 🌟 Features

### Core Features
- **AI Chat Interface**: Real-time conversations with ElderWise AI companion
- **Voice Support**: Speech recognition and synthesis for hands-free interaction
- **Memory Lane**: Browse and search through conversation history
- **Health Tracking**: Monitor health metrics and medication reminders
- **Emergency Features**: Quick access to emergency contacts and services
- **Settings**: Customizable preferences including text size and contrast

### Accessibility Features
- **WCAG 2.1 AA Compliant**: Meets accessibility standards for elderly users
- **Large Touch Targets**: Minimum 48px touch targets for easy interaction
- **High Contrast Mode**: Enhanced visibility option
- **Text Size Control**: Adjustable text sizes (small, medium, large, extra-large)
- **Voice Control**: Voice commands for navigation
- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: Comprehensive ARIA labels and live regions
- **Reduced Motion**: Respects user preferences for reduced animations

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/elderwise.git
cd elderwise/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment variables:
```bash
cp .env.example .env
```

4. Configure your .env file:
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=ElderWise
VITE_APP_VERSION=1.0.0
VITE_VOICE_ENABLED=true
VITE_OFFLINE_ENABLED=true
VITE_DEBUG_MODE=true
```

### Development

Run the development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

### Building for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Run Accessibility Tests
```bash
npm run test:a11y
```

### Run Tests with Coverage
```bash
npm run test:coverage
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── common/       # Common components (Button, Card, etc.)
│   │   ├── chat/         # Chat-specific components
│   │   └── family/       # Family dashboard components
│   ├── screens/          # Page-level components
│   │   ├── auth/         # Authentication screens
│   │   └── main/         # Main app screens
│   ├── services/         # API and external services
│   ├── store/            # Zustand state management
│   ├── hooks/            # Custom React hooks
│   ├── utils/            # Utility functions
│   ├── types/            # TypeScript type definitions
│   └── __tests__/        # Test files
├── public/               # Static assets
└── dist/                 # Production build output
```

## 🎨 Design System

### Colors
- **Lavender**: Primary brand color for calm and trust
- **Sage**: Success and positive states
- **Coral**: Alerts and emergency actions
- **Cream**: Soft backgrounds for reduced eye strain

### Typography
- **Font**: Atkinson Hyperlegible for maximum readability
- **Base Size**: 20px (larger than typical for elderly users)
- **Scale**: 1.25 ratio for clear hierarchy

### Components
All components are designed with elderly users in mind:
- Large, clear buttons with distinct states
- High contrast text and backgrounds
- Clear visual feedback for all interactions
- Simplified navigation patterns

## 🔧 Configuration

### Text Size
Users can adjust text size in Settings:
- Small (16px base)
- Medium (18px base)
- Large (20px base) - Default
- Extra Large (24px base)

### Theme Options
- Standard theme (default)
- High contrast mode
- Reduced motion (respects system preference)

## 🚀 Deployment

### Docker
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
```

### Environment Variables
Configure these for production:
- `VITE_API_URL`: Backend API URL
- `VITE_VOICE_ENABLED`: Enable/disable voice features
- `VITE_OFFLINE_ENABLED`: Enable/disable offline mode

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards
- Follow TypeScript best practices
- Maintain accessibility standards
- Write tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and feature requests, please use the GitHub issues tracker.

For questions about ElderWise, contact support@elderwise.ai