import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';

import { ThemeProvider } from '@/components/layout/theme-provider';
import { AppLayout } from '@/components/layout/app-layout';
import { useAuthStore } from '@/store/auth-store';

// Pages
import { Login } from '@/pages/auth/login';
import { Register } from '@/pages/auth/register';

// Placeholder/Stub components for routing
const Dashboard = React.lazy(() => import('@/pages/dashboard'));
const Documents = React.lazy(() => import('@/pages/documents'));
const Chat = React.lazy(() => import('@/pages/chat'));
const Settings = React.lazy(() => import('@/pages/settings'));

// Stubs for future features (Phase 4-7) to make sidebar links work
const CompareStubs = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <h2 className="text-2xl font-bold font-sans text-indigo-400 mb-2">Paper Comparison Matrix</h2>
    <p className="text-muted-foreground max-w-md">Compare methods, datasets, models, results, strengths, and weaknesses of multiple research papers side-by-side. (Phase 5 Feature)</p>
  </div>
);

const CitationsStubs = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <h2 className="text-2xl font-bold font-sans text-indigo-400 mb-2">Citation Generator</h2>
    <p className="text-muted-foreground max-w-md">Automatically generate bibliography and citations in APA, MLA, IEEE, Chicago, and BibTeX formats. (Phase 5 Feature)</p>
  </div>
);

const GraphStubs = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <h2 className="text-2xl font-bold font-sans text-indigo-400 mb-2">Interactive Knowledge Graph</h2>
    <p className="text-muted-foreground max-w-md">Visualize connections between authors, topics, keywords, citations, and paper relationships. (Phase 6 Feature)</p>
  </div>
);

const NotebookStubs = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <h2 className="text-2xl font-bold font-sans text-indigo-400 mb-2">Research Notebook</h2>
    <p className="text-muted-foreground max-w-md">Store paper highlights, customized tags, and annotated research notes. (Phase 6 Feature)</p>
  </div>
);

const AnalyticsStubs = () => (
  <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
    <h2 className="text-2xl font-bold font-sans text-indigo-400 mb-2">Research Analytics</h2>
    <p className="text-muted-foreground max-w-md">Analyze reading progress, top-studied topics, frequently used terms, and upload statistics. (Phase 7 Feature)</p>
  </div>
);

// Protected Route Guard
const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, loadUser } = useAuthStore();

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const token = localStorage.getItem('auth-token');
  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

const LazyLoadWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <React.Suspense
      fallback={
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent"></div>
        </div>
      }
    >
      {children}
    </React.Suspense>
  );
};

const App: React.FC = () => {
  const loadUser = useAuthStore((state) => state.loadUser);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Main Workspace Routes */}
          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route
                path="/dashboard"
                element={
                  <LazyLoadWrapper>
                    <Dashboard />
                  </LazyLoadWrapper>
                }
              />
              <Route
                path="/documents"
                element={
                  <LazyLoadWrapper>
                    <Documents />
                  </LazyLoadWrapper>
                }
              />
              <Route
                path="/chat"
                element={
                  <LazyLoadWrapper>
                    <Chat />
                  </LazyLoadWrapper>
                }
              />
              <Route path="/compare" element={<CompareStubs />} />
              <Route path="/citations" element={<CitationsStubs />} />
              <Route path="/knowledge-graph" element={<GraphStubs />} />
              <Route path="/notebook" element={<NotebookStubs />} />
              <Route path="/analytics" element={<AnalyticsStubs />} />
              <Route
                path="/settings"
                element={
                  <LazyLoadWrapper>
                    <Settings />
                  </LazyLoadWrapper>
                }
              />
            </Route>
          </Route>

          {/* Wildcard Fallback */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" toastOptions={{ duration: 4000 }} />
    </ThemeProvider>
  );
};

export default App;
