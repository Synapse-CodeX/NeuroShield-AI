import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import {
  Shield,
  AlertTriangle,
  Info,
  ShieldCheck,
  ChevronDown,
  ChevronUp,
  Lightbulb,
  FileText,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { analyzePrivacy, chatPrivacy } from '../services/api';

import ScoreGauge from '../components/ScoreGauge';
import LoadingState from '../components/LoadingState';
import ChatPanel from '../components/ChatPanel';
import EvidenceCard from '../components/EvidenceCard';
import './PrivacyAnalyzer.css';

const SEVERITY_CONFIG = {
  critical: {
    label: 'Critical',
    className: 'severity-critical',
  },
  high: {
    label: 'High',
    className: 'severity-high',
  },
  medium: {
    label: 'Medium',
    className: 'severity-medium',
  },
  low: {
    label: 'Low',
    className: 'severity-low',
  },
  info: {
    label: 'Info',
    className: 'severity-info',
  },
};

const formatKey = (key) =>
  key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const PrivacyAnalyzer = () => {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [expandedFinding, setExpandedFinding] = useState(null);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error('Please enter a privacy policy to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setResult(null);
    setExpandedFinding(null);

    try {
      const data = await analyzePrivacy(text);
      setResult(data);
      toast.success('Analysis complete!');
    } catch (error) {
      toast.error('Analysis failed. ' + error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleChat = async (question) => {
    setIsTyping(true);

    try {
      const data = await chatPrivacy(
        question,
        result.session_id,
      );

      return data.answer;
    } catch (error) {
      toast.error('Chat error: ' + error.message);
      throw error;
    } finally {
      setIsTyping(false);
    }
  };

  const reset = () => {
    setText('');
    setResult(null);
    setExpandedFinding(null);
  };

  const findings = Array.isArray(result?.findings)
    ? result.findings
    : [];

  const recommendations = Array.isArray(
    result?.recommendations,
  )
    ? result.recommendations
    : [];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="privacy-page container section"
    >
      <div className="page-header">
        <h1>
          <Shield className="inline-icon" />
          Privacy Policy Analyzer
        </h1>

        <p>
          Paste any privacy policy to extract what data is
          collected, identify privacy risks, inspect the evidence,
          and understand what to do next.
        </p>
      </div>

      {!result && !isAnalyzing && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="input-section glass-card"
        >
          <textarea
            value={text}
            onChange={(event) =>
              setText(event.target.value)
            }
            placeholder="Paste privacy policy text here..."
            className="textarea-field"
          />

          <div className="input-actions">
            <span className="char-count">
              {text.length} characters
            </span>

            <button
              onClick={handleAnalyze}
              className="btn btn-primary"
              disabled={!text.trim()}
            >
              Analyze Policy
            </button>
          </div>
        </motion.div>
      )}

      {isAnalyzing && (
        <LoadingState
          message="Analyzing Privacy Policy..."
        />
      )}

      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="results-grid"
        >
          {/* =====================================================
              MAIN CONTENT
          ====================================================== */}

          <div className="results-main">
            {/* =================================================
                SCORE + SUMMARY
            ================================================== */}

            <div className="glass-card summary-banner">
              <div className="score-section">
                <ScoreGauge
                  score={result.score}
                  size={140}
                />

                <div className="risk-level">
                  <span className="risk-label">
                    Privacy Risk
                  </span>

                  <h3 className="risk-value">
                    {result.verdict || 'Unknown'}
                  </h3>

                  {result.confidence !== undefined && (
                    <span className="analysis-confidence">
                      {Math.round(
                        Number(result.confidence) * 100,
                      )}
                      % analysis confidence
                    </span>
                  )}
                </div>
              </div>

              <div className="summary-section">
                <h3>
                  <Info size={20} />
                  Plain-English Summary
                </h3>

                <div className="markdown-content">
                  <ReactMarkdown>
                    {result.summary ||
                      'No summary was generated.'}
                  </ReactMarkdown>
                </div>
              </div>
            </div>

            {/* =================================================
                FINDINGS
            ================================================== */}

            <div className="glass-card findings-panel">
              <div className="panel-heading-row">
                <div>
                  <span className="section-eyebrow">
                    Evidence Analysis
                  </span>

                  <h3 className="panel-title">
                    <AlertTriangle size={20} />
                    Privacy Findings
                  </h3>
                </div>

                <span className="finding-count">
                  {findings.length}{' '}
                  {findings.length === 1
                    ? 'finding'
                    : 'findings'}
                </span>
              </div>

              {findings.length > 0 ? (
                <div className="findings-list">
                  {findings.map((finding, index) => {
                    const severity =
                      SEVERITY_CONFIG[
                        String(
                          finding.severity || 'info',
                        ).toLowerCase()
                      ] || SEVERITY_CONFIG.info;

                    const evidence =
                      Array.isArray(finding.evidence)
                        ? finding.evidence
                        : [];

                    const isExpanded =
                      expandedFinding === index;

                    return (
                      <motion.div
                        layout
                        key={`${finding.title}-${index}`}
                        className={`privacy-finding ${severity.className}`}
                      >
                        <button
                          type="button"
                          className="finding-header"
                          onClick={() =>
                            setExpandedFinding(
                              isExpanded
                                ? null
                                : index,
                            )
                          }
                          aria-expanded={isExpanded}
                        >
                          <div className="finding-header-main">
                            <div className="finding-meta">
                              <span
                                className={`severity-badge ${severity.className}`}
                              >
                                {severity.label}
                              </span>

                              {finding.category && (
                                <span className="finding-category">
                                  {finding.category}
                                </span>
                              )}

                              {finding.confidence !==
                                undefined && (
                                <span className="finding-confidence">
                                  {Math.round(
                                    Number(
                                      finding.confidence,
                                    ) * 100,
                                  )}
                                  % confidence
                                </span>
                              )}
                            </div>

                            <h4>{finding.title}</h4>

                            <p>
                              {finding.description}
                            </p>
                          </div>

                          <span className="finding-expand">
                            {isExpanded ? (
                              <ChevronUp size={19} />
                            ) : (
                              <ChevronDown size={19} />
                            )}
                          </span>
                        </button>

                        {isExpanded && (
                          <motion.div
                            initial={{
                              height: 0,
                              opacity: 0,
                            }}
                            animate={{
                              height: 'auto',
                              opacity: 1,
                            }}
                            className="finding-details"
                          >
                            {finding.recommendation && (
                              <div className="finding-recommendation">
                                <Lightbulb size={16} />

                                <div>
                                  <strong>
                                    Recommended action
                                  </strong>

                                  <span>
                                    {
                                      finding.recommendation
                                    }
                                  </span>
                                </div>
                              </div>
                            )}

                            <div className="finding-evidence">
                              <div className="finding-evidence-heading">
                                <div>
                                  <span className="section-eyebrow">
                                    Source Evidence
                                  </span>

                                  <h5>
                                    Why this finding was
                                    detected
                                  </h5>
                                </div>

                                <span>
                                  {evidence.length}{' '}
                                  {evidence.length === 1
                                    ? 'excerpt'
                                    : 'excerpts'}
                                </span>
                              </div>

                              {evidence.length > 0 ? (
                                <div className="privacy-evidence-grid">
                                  {evidence.map(
                                    (
                                      evidenceItem,
                                      evidenceIndex,
                                    ) => (
                                      <EvidenceCard
                                        key={`${evidenceItem.title}-${evidenceIndex}`}
                                        evidence={
                                          evidenceItem
                                        }
                                        role="Policy Evidence"
                                      />
                                    ),
                                  )}
                                </div>
                              ) : (
                                <div className="no-policy-evidence">
                                  <Info size={17} />

                                  <span>
                                    No specific policy
                                    excerpt was attached to
                                    this finding.
                                  </span>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </motion.div>
                    );
                  })}
                </div>
              ) : (
                <div className="safe-state">
                  <ShieldCheck size={28} />

                  <div>
                    <strong>
                      No significant privacy findings
                    </strong>

                    <span>
                      No rule-based privacy risks were
                      identified in the analyzed policy.
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* =================================================
                RECOMMENDATIONS
            ================================================== */}

            {recommendations.length > 0 && (
              <div className="glass-card recommendations-panel">
                <div className="recommendations-heading">
                  <div>
                    <span className="section-eyebrow">
                      User Protection
                    </span>

                    <h3>
                      <Lightbulb size={20} />
                      Recommended Actions
                    </h3>
                  </div>

                  <span>
                    {recommendations.length}{' '}
                    actions
                  </span>
                </div>

                <div className="recommendations-list">
                  {recommendations.map(
                    (recommendation, index) => (
                      <div
                        key={`${recommendation}-${index}`}
                        className="recommendation-item"
                      >
                        <span className="recommendation-number">
                          {index + 1}
                        </span>

                        <p>{recommendation}</p>
                      </div>
                    ),
                  )}
                </div>
              </div>
            )}

            {/* =================================================
                STRUCTURED DATA
            ================================================== */}

            <div className="glass-card data-panel">
              <div className="panel-heading-row">
                <div>
                  <span className="section-eyebrow">
                    Policy Extraction
                  </span>

                  <h3 className="panel-title">
                    <FileText size={19} />
                    Extracted Details
                  </h3>
                </div>
              </div>

              <div className="data-grid">
                {Object.entries(
                  result.structured_data || {},
                ).map(([key, value]) => {
                  if (
                    !value ||
                    (Array.isArray(value) &&
                      value.length === 0)
                  ) {
                    return null;
                  }

                  return (
                    <div
                      key={key}
                      className="data-group"
                    >
                      <h4>{formatKey(key)}</h4>

                      {Array.isArray(value) ? (
                        <div className="pill-container">
                          {value.map((item, index) => (
                            <span
                              key={`${item}-${index}`}
                              className="pill pill-accent"
                            >
                              {item}
                            </span>
                          ))}
                        </div>
                      ) : (
                        <p>{String(value)}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="action-row">
              <button
                onClick={reset}
                className="btn btn-secondary"
              >
                Analyze Another Policy
              </button>
            </div>
          </div>

          {/* =====================================================
              CHAT SIDEBAR
          ====================================================== */}

          <div className="results-sidebar">
            <ChatPanel
              onSendMessage={handleChat}
              isTyping={isTyping}
            />
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default PrivacyAnalyzer;