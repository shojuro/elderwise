import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AnimatePresence } from 'framer-motion';

// Screens
import { WelcomeScreen } from './screens/auth/WelcomeScreen';
import { SetupScreen } from './screens/auth/SetupScreen';
import { LoginScreen } from './screens/auth/LoginScreen';
import { HomeScreen } from './screens/main/HomeScreen';
import { ChatScreen } from './screens/main/ChatScreen';
import { MemoryScreen } from './screens/main/MemoryScreen';
import { EmergencyScreen } from './screens/main/EmergencyScreen';
import { SettingsScreen } from './screens/main/SettingsScreen';
import { HealthScreen } from './screens/main/HealthScreen';

// Store
import { useAppStore } from './store';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAppStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/welcome" replace />;
  }
  
  return <>{children}</>;
};

// Public Route Component (redirect if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAppStore();
  
  if (isAuthenticated && user) {
    // Redirect based on user role
    if (user.role === 'family') {
      return <Navigate to="/family" replace />;
    }
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="App">
          <AnimatePresence mode="wait">
            <Routes>
              {/* Public routes */}
              <Route path="/welcome" element={
                <PublicRoute>
                  <WelcomeScreen />
                </PublicRoute>
              } />
              
              <Route path="/setup" element={
                <PublicRoute>
                  <SetupScreen />
                </PublicRoute>
              } />
              
              <Route path="/login" element={
                <PublicRoute>
                  <LoginScreen />
                </PublicRoute>
              } />

              {/* Protected routes for elderly users */}
              <Route path="/" element={
                <ProtectedRoute>
                  <HomeScreen />
                </ProtectedRoute>
              } />

              <Route path="/chat" element={
                <ProtectedRoute>
                  <ChatScreen />
                </ProtectedRoute>
              } />

              <Route path="/memories" element={
                <ProtectedRoute>
                  <MemoryScreen />
                </ProtectedRoute>
              } />

              <Route path="/health" element={
                <ProtectedRoute>
                  <HealthScreen />
                </ProtectedRoute>
              } />

              <Route path="/emergency" element={
                <ProtectedRoute>
                  <EmergencyScreen />
                </ProtectedRoute>
              } />

              <Route path="/settings" element={
                <ProtectedRoute>
                  <SettingsScreen />
                </ProtectedRoute>
              } />

              {/* Family routes - placeholder */}
              <Route path="/family/*" element={
                <ProtectedRoute>
                  <div className="p-8 text-center">
                    <h1 className="text-2xl font-bold mb-4">Family Dashboard</h1>
                    <p>Coming soon...</p>
                  </div>
                </ProtectedRoute>
              } />

              {/* Default redirect */}
              <Route path="*" element={<Navigate to="/welcome" replace />} />
            </Routes>
          </AnimatePresence>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App;