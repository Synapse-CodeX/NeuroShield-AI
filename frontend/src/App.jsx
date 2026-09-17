import { Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';

import Navbar from './components/Navbar';
import Footer from './components/Footer';

import LandingPage from './pages/LandingPage';
import PrivacyAnalyzer from './pages/PrivacyAnalyzer';
import FactChecker from './pages/FactChecker';
import WebsiteScanner from './pages/WebsiteScanner';

function App() {
  const location = useLocation();

  return (
    <div className="app-shell">
      <div className="bg-gradient-radial" aria-hidden="true" />
      <div className="grid-overlay" aria-hidden="true" />

      <Navbar />

      <main className="page">
        <AnimatePresence mode="wait">
          <Routes location={location} key={location.pathname}>
            <Route path="/" element={<LandingPage />} />
            <Route path="/privacy" element={<PrivacyAnalyzer />} />
            <Route path="/factcheck" element={<FactChecker />} />
            <Route path="/scanner" element={<WebsiteScanner />} />
          </Routes>
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