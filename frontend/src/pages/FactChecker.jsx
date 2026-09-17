import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { CheckSquare, ChevronDown, ChevronUp, ExternalLink, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { checkFacts } from '../services/api';

import LoadingState from '../components/LoadingState';
import VerdictBadge from '../components/VerdictBadge';
import './FactChecker.css';

const FactChecker = () => {
  const [text, setText] = useState('');
  const [isChecking, setIsChecking] = useState(false);
  const [result, setResult] = useState(null);
  const [expandedClaim, setExpandedClaim] = useState(null);
  const [showFullReport, setShowFullReport] = useState(false);

  const handleCheck = async () => {
    if (!text.trim()) {
      toast.error('Please enter text to fact-check.');
      return;
    }

    setIsChecking(true);
    setResult(null);

    try {
      const data = await checkFacts(text);
      setResult(data);
      toast.success('Fact check complete!');
    } catch (error) {
      toast.error('Fact check failed. ' + error.message);
    } finally {
      setIsChecking(false);
    }
  };

  const reset = () => {
    setText('');
    setResult(null);
    setExpandedClaim(null);
    setShowFullReport(false);
  };

  const getVerdictCounts = () => {
    if (!result || !result.verifications) return {};
    const counts = { True: 0, False: 0, 'Partially True': 0, Unverifiable: 0 };
    Object.values(result.verifications).forEach(v => {
      if (counts[v.verdict] !== undefined) counts[v.verdict]++;
    });
    return counts;
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="factcheck-page container section"
    >
      <div className="page-header">
        <h1><CheckSquare className="inline-icon" /> AI Fact Checker</h1>
        <p>Verify claims using our advanced RAG pipeline that cross-references trusted sources across the web.</p>
      </div>

      {!result && !isChecking && (
        <motion.div initial={{ y: 20 }} animate={{ y: 0 }} className="input-section glass-card">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste text containing claims you want to verify (e.g., news article, social media post)..."
            className="textarea-field"
          />
          <div className="input-actions">
            <span className="char-count">{text.length} characters</span>
            <button onClick={handleCheck} className="btn btn-primary" disabled={!text.trim()}>
              Verify Facts
            </button>
          </div>
        </motion.div>
      )}

      {isChecking && (
        <LoadingState message="Extracting claims and searching the web..." />
      )}

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="results-container">
          
          {/* Summary Bar */}
          <div className="summary-bar glass-card">
            <div className="summary-stat">
              <span className="stat-value">{result.claims?.length || 0}</span>
              <span className="stat-label">Claims Found</span>
            </div>
            <div className="verdict-counts">
              {Object.entries(getVerdictCounts()).map(([verdict, count]) => (
                <div key={verdict} className="count-pill">
                  <VerdictBadge verdict={verdict} />
                  <span className="count-number">{count}</span>
                </div>
              ))}
            </div>
            <button onClick={reset} className="btn btn-ghost">Check Another</button>
          </div>

          <div className="claims-list">
            <h3>Analyzed Claims</h3>
            {result.claims?.length === 0 ? (
              <div className="glass-card empty-state">
                <AlertCircle size={48} className="empty-icon" />
                <p>No verifiable claims found in the text.</p>
              </div>
            ) : (
              result.claims?.map(claim => {
                const verification = result.verifications?.[claim.id];
                const evidence = result.evidence?.[claim.id] || [];
                const isExpanded = expandedClaim === claim.id;

                if (!verification) return null;

                return (
                  <div key={claim.id} className="claim-card glass-card">
                    <div 
                      className="claim-header" 
                      onClick={() => setExpandedClaim(isExpanded ? null : claim.id)}
                    >
                      <div className="claim-main">
                        <div className="claim-meta">
                          <span className="pill">{claim.type}</span>
                          <VerdictBadge verdict={verification.verdict} />
                          <span className="confidence-pill" title={`Confidence: ${(verification.confidence * 100).toFixed(0)}%`}>
                            {Math.round(verification.confidence * 100)}% Confidence
                          </span>
                        </div>
                        <h4 className="claim-text">"{claim.claim}"</h4>
                      </div>
                      <button className="expand-btn">
                        {isExpanded ? <ChevronUp /> : <ChevronDown />}
                      </button>
                    </div>

                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div 
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="claim-details"
                        >
                          <div className="reasoning-box">
                            <strong>Reasoning:</strong> {verification.reason}
                          </div>

                          {evidence.length > 0 && (
                            <div className="evidence-section">
                              <strong>Sources Considered:</strong>
                              <div className="sources-grid">
                                {evidence.map((source, idx) => (
                                  <a 
                                    key={idx} 
                                    href={source.url} 
                                    target="_blank" 
                                    rel="noopener noreferrer"
                                    className="source-card"
                                  >
                                    <div className="source-title">
                                      {source.title} <ExternalLink size={12} />
                                    </div>
                                    <div className="source-url">{new URL(source.url).hostname}</div>
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {verification.uncertainty_reason && (
                            <div className="uncertainty-box">
                              <AlertCircle size={16} />
                              <span>{verification.uncertainty_reason}</span>
                            </div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })
            )}
          </div>

          {/* Full Report Toggle */}
          <div className="report-section glass-card">
            <div 
              className="report-header" 
              onClick={() => setShowFullReport(!showFullReport)}
            >
              <h3>Full Narrative Report</h3>
              <button className="btn btn-ghost">
                {showFullReport ? 'Hide' : 'Show'} Report
              </button>
            </div>
            
            <AnimatePresence>
              {showFullReport && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="full-report-content"
                >
                  <div className="markdown-content">
                    <ReactMarkdown>{result.final_report}</ReactMarkdown>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

        </motion.div>
      )}
    </motion.div>
  );
};

export default FactChecker;
