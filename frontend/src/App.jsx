import { lazy, Suspense } from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';

import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LoadingState from './components/LoadingState';

import LandingPage from './pages/LandingPage';

import './App.css';

// Load heavier analysis pages only when they are actually visited.
const PrivacyAnalyzer = lazy(() => import('./pages/PrivacyAnalyzer'));
const FactChecker = lazy(() => import('./pages/FactChecker'));
const WebsiteScanner = lazy(() => import('./pages/WebsiteScanner'));

function RouteLoading() {
  return (
    <div className="route-loading">
      <LoadingState message="Loading NeuroShield..." />
    </div>
  );
}

function App() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <div className="bg-gradient-radial" aria-hidden="true" />
      <div className="grid-overlay" aria-hidden="true" />

      <Navbar />

      <main className="page">
        <AnimatePresence mode="wait">
          <Suspense fallback={<RouteLoading />}>
            <Routes location={location} key={location.pathname}>
              <Route path="/" element={<LandingPage />} />
              <Route path="/privacy" element={<PrivacyAnalyzer />} />
              <Route path="/factcheck" element={<FactChecker />} />
              <Route path="/scanner" element={<WebsiteScanner />} />
            </Routes>
          </Suspense>
        </AnimatePresence>
      </main>

      <Footer />

      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-light)',
            borderRadius: 'var(--radius-md)',
            backdropFilter: 'blur(16px)',
            boxShadow: 'var(--shadow-lg)',
          },
        }}
      />
    </div>
  );
}

export default App;