import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Search, Link as LinkIcon, Calendar, AlertTriangle, Lock, FileText, Star, Lightbulb } from 'lucide-react';
import { scanWebsite, chatScanner } from '../services/api';

import LoadingState from '../components/LoadingState';
import VerdictBadge from '../components/VerdictBadge';
import ProgressBar from '../components/ProgressBar';
import ChatPanel from '../components/ChatPanel';
import './WebsiteScanner.css';

const SCORE_LABELS = {
  url_structure: { icon: LinkIcon, label: "URL Structure" },
  domain_age: { icon: Calendar, label: "Domain Age" },
  scam_reports: { icon: AlertTriangle, label: "Scam Reports" },
  ssl_certificate: { icon: Lock, label: "SSL Certificate" },
  content_quality: { icon: FileText, label: "Content Quality" },
  reputation: { icon: Star, label: "Reputation" },
};

const WebsiteScanner = () => {
  const [url, setUrl] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  const handleScan = async () => {
    let targetUrl = url.trim();
    if (!targetUrl) {
      toast.error('Please enter a URL to scan.');
      return;
    }
    
    if (!/^https?:\/\//i.test(targetUrl)) {
      targetUrl = 'https://' + targetUrl;
    }

    setIsScanning(true);
    setResult(null);

    try {
      const data = await scanWebsite(targetUrl);
      setResult(data);
      toast.success('Scan complete!');
    } catch (error) {
      toast.error('Scan failed. ' + error.message);
    } finally {
      setIsScanning(false);
    }
  };

  const handleChat = async (question) => {
    setIsTyping(true);
    try {
      const data = await chatScanner(question, result.session_id);
      return data.answer;
    } catch (error) {
      toast.error('Chat error: ' + error.message);
      throw error;
    } finally {
      setIsTyping(false);
    }
  };

  const reset = () => {
    setUrl('');
    setResult(null);
  };

  const renderDetailsList = (items, prefix = "⚠️") => {
    if (!items || items.length === 0) return null;
    return (
      <ul className="details-list">
        {items.map((item, idx) => (
          <li key={idx}><span>{prefix}</span> {item}</li>
        ))}
      </ul>
    );
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="scanner-page container section"
    >
      <div className="page-header">
        <h1><Search className="inline-icon" /> Website Safety Scanner</h1>
        <p>Detect phishing, scam, and fake websites instantly before you click or share data.</p>
      </div>

      {!result && !isScanning && (
        <motion.div initial={{ y: 20 }} animate={{ y: 0 }} className="input-section glass-card">
          <div className="url-input-wrapper">
            <Search className="input-icon" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter website URL (e.g., example.com)"
              className="input-field url-input"
              onKeyDown={(e) => e.key === 'Enter' && handleScan()}
            />
            <button onClick={handleScan} className="btn btn-primary scan-btn" disabled={!url.trim()}>
              Scan Site
            </button>
          </div>
        </motion.div>
      )}

      {isScanning && (
        <LoadingState message="Analyzing website structure and reputation..." />
      )}

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="results-grid">
          
          <div className="results-main">
            {/* Verdict Banner */}
            <div className={`verdict-banner glass-card ${result.verdict?.toLowerCase()}`}>
              <div className="verdict-score-display">
                <span className="huge-score">{result.overall_score}</span>
                <span className="max-score">/100</span>
              </div>
              <div className="verdict-status">
                <VerdictBadge verdict={result.verdict} />
                <p className="verdict-summary">
                  {JSON.parse(result.summary || '{}').summary || "Website scan complete."}
                </p>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="glass-card scores-panel">
              <h3>Score Breakdown</h3>
              <div className="scores-grid">
                {Object.entries(result.scores || {}).map(([key, score]) => {
                  const labelData = SCORE_LABELS[key] || { icon: AlertTriangle, label: key };
                  const Icon = labelData.icon;
                  return (
                    <ProgressBar 
                      key={key} 
                      label={labelData.label} 
                      score={score} 
                      icon={<Icon size={16} />} 
                    />
                  );
                })}
              </div>
            </div>

            {/* Findings */}
            <div className="glass-card findings-panel">
              <h3>Key Findings</h3>
              <div className="findings-accordion">
                {/* Check each category for flags/details */}
                {(() => {
                  const categories = [
                    { key: 'url_analysis', title: 'URL Analysis', data: result.url_analysis },
                    { key: 'domain_age_analysis', title: 'Domain Info', data: result.domain_age_analysis },
                    { key: 'ssl_analysis', title: 'SSL Certificate', data: result.ssl_analysis },
                    { key: 'scam_report_analysis', title: 'Scam Reports', data: result.scam_report_analysis },
                  ];

                  return categories.map(({ key, title, data }) => {
                    if (!data) return null;
                    const items = [
                      ...(data.flags || []),
                      ...(data.red_flags || []),
                      ...(data.details || [])
                    ].filter(Boolean);

                    if (items.length === 0) return null;

                    return (
                      <div key={key} className="finding-group">
                        <h4>{title}</h4>
                        {renderDetailsList(items)}
                      </div>
                    );
                  });
                })()}
              </div>
            </div>

          </div>

          <div className="results-sidebar">
            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <div className="glass-card recommendations-panel">
                <h3><Lightbulb size={20} className="text-yellow" /> Actionable Advice</h3>
                <ul className="recs-list">
                  {result.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}

            <ChatPanel onSendMessage={handleChat} isTyping={isTyping} />
            
            <div className="action-row mt-4">
              <button onClick={reset} className="btn btn-secondary w-full">Scan Another URL</button>
            </div>
          </div>

        </motion.div>
      )}
    </motion.div>
  );
};

export default WebsiteScanner;
