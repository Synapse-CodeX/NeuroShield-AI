import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import {
  Search,
  Link as LinkIcon,
  Calendar,
  AlertTriangle,
  Lock,
  FileText,
  Star,
  Lightbulb,
  ShieldCheck,
  ShieldAlert,
  Activity,
  ChevronDown,
  ChevronUp,
  Globe,
} from 'lucide-react';
import { scanWebsite, chatScanner } from '../services/api';

import LoadingState from '../components/LoadingState';
import VerdictBadge from '../components/VerdictBadge';
import ProgressBar from '../components/ProgressBar';
import ChatPanel from '../components/ChatPanel';
import './WebsiteScanner.css';

const SCORE_LABELS = {
  url_structure: {
    icon: LinkIcon,
    label: 'URL Structure',
    description: 'Checks URL patterns associated with suspicious or deceptive sites.',
  },
  domain_age: {
    icon: Calendar,
    label: 'Domain Age',
    description: 'Evaluates available domain-age signals.',
  },
  scam_reports: {
    icon: AlertTriangle,
    label: 'Scam Reports',
    description: 'Assesses available scam and abuse indicators.',
  },
  ssl_certificate: {
    icon: Lock,
    label: 'SSL Certificate',
    description: 'Checks HTTPS and TLS certificate validity.',
  },
  content_quality: {
    icon: FileText,
    label: 'Content Quality',
    description: 'Evaluates the quality and legitimacy of website content.',
  },
  reputation: {
    icon: Star,
    label: 'Reputation',
    description: 'Assesses broader reputation signals for the website.',
  },
};

const ANALYSIS_CATEGORIES = [
  {
    key: 'url_analysis',
    title: 'URL Analysis',
    icon: LinkIcon,
    color: 'purple',
  },
  {
    key: 'domain_age_analysis',
    title: 'Domain Information',
    icon: Calendar,
    color: 'blue',
  },
  {
    key: 'ssl_analysis',
    title: 'SSL / TLS',
    icon: Lock,
    color: 'green',
  },
  {
    key: 'scam_report_analysis',
    title: 'Scam Reports',
    icon: AlertTriangle,
    color: 'red',
  },
  {
    key: 'content_analysis',
    title: 'Content Quality',
    icon: FileText,
    color: 'yellow',
  },
  {
    key: 'reputation_analysis',
    title: 'Reputation',
    icon: Star,
    color: 'purple',
  },
];

const WebsiteScanner = () => {
  const [url, setUrl] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  const [expandedAnalysis, setExpandedAnalysis] = useState(null);

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
    setExpandedAnalysis(null);

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
      const data = await chatScanner(
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
    setUrl('');
    setResult(null);
    setExpandedAnalysis(null);
  };

  const getVerdictClass = (verdict) => {
    const normalized = String(verdict || '')
      .toLowerCase()
      .replace(/\s+/g, '-');

    if (normalized.includes('safe')) return 'safe';
    if (normalized.includes('caution')) return 'caution';
    if (normalized.includes('suspicious')) return 'suspicious';
    if (normalized.includes('dangerous')) return 'dangerous';

    return 'caution';
  };

  const parseSummary = (summary) => {
    if (!summary) {
      return 'Website scan complete.';
    }

    if (typeof summary === 'object') {
      return (
        summary.summary ||
        summary.description ||
        summary.reason ||
        'Website scan complete.'
      );
    }

    if (typeof summary !== 'string') {
      return 'Website scan complete.';
    }

    try {
      const parsed = JSON.parse(summary);

      return (
        parsed.summary ||
        parsed.description ||
        parsed.reason ||
        summary
      );
    } catch {
      return summary;
    }
  };

  const getAnalysisItems = (data) => {
    if (!data || typeof data !== 'object') {
      return [];
    }

    const preferredKeys = [
      'flags',
      'red_flags',
      'warnings',
      'details',
      'signals',
      'findings',
      'observations',
    ];

    const items = [];

    preferredKeys.forEach((key) => {
      const value = data[key];

      if (Array.isArray(value)) {
        value.forEach((item) => {
          if (item !== null && item !== undefined) {
            items.push(String(item));
          }
        });
      } else if (
        typeof value === 'string' &&
        value.trim()
      ) {
        items.push(value.trim());
      }
    });

    return [...new Set(items)];
  };

  const getAnalysisText = (data) => {
    if (!data || typeof data !== 'object') {
      return '';
    }

    const candidates = [
      data.summary,
      data.reason,
      data.description,
      data.assessment,
      data.verdict_reason,
      data.message,
    ];

    return (
      candidates.find(
        (value) =>
          typeof value === 'string' &&
          value.trim(),
      ) || ''
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="scanner-page container section"
    >
      <div className="page-header">
        <h1>
          <Search className="inline-icon" />
          Website Safety Scanner
        </h1>

        <p>
          Detect phishing, scam, and deceptive website signals
          before you click or share sensitive information.
        </p>
      </div>

      {/* =====================================================
          INPUT
      ====================================================== */}

      {!result && !isScanning && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="input-section glass-card"
        >
          <div className="url-input-wrapper">
            <Search className="input-icon" />

            <input
              type="text"
              value={url}
              onChange={(event) =>
                setUrl(event.target.value)
              }
              placeholder="Enter website URL (e.g., example.com)"
              className="input-field url-input"
              onKeyDown={(event) =>
                event.key === 'Enter' && handleScan()
              }
            />

            <button
              onClick={handleScan}
              className="btn btn-primary scan-btn"
              disabled={!url.trim()}
            >
              Scan Site
            </button>
          </div>
        </motion.div>
      )}

      {isScanning && (
        <LoadingState
          message="Analyzing website structure and reputation..."
        />
      )}

      {/* =====================================================
          RESULTS
      ====================================================== */}

      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="scanner-results"
        >
          <div className="results-main">
            {/* =================================================
                VERDICT
            ================================================== */}

            <div
              className={`verdict-banner glass-card ${getVerdictClass(
                result.verdict,
              )}`}
            >
              <div className="verdict-score-display">
                <span className="huge-score">
                  {Number(
                    result.overall_score || 0,
                  ).toFixed(0)}
                </span>

                <span className="max-score">
                  /100
                </span>
              </div>

              <div className="verdict-status">
                <div className="verdict-heading">
                  <Globe size={18} />
                  <span className="scanned-url">
                    {url}
                  </span>
                </div>

                <VerdictBadge
                  verdict={result.verdict}
                />

                <p className="verdict-summary">
                  {parseSummary(result.summary)}
                </p>
              </div>
            </div>

            {/* =================================================
                SCORE BREAKDOWN
            ================================================== */}

            <div className="glass-card scores-panel">
              <div className="panel-heading">
                <div>
                  <span className="section-eyebrow">
                    Risk Engine
                  </span>

                  <h3>
                    <Activity size={19} />
                    Safety Signal Breakdown
                  </h3>
                </div>

                <span className="panel-caption">
                  Six independent signals
                </span>
              </div>

              <div className="scores-grid">
                {Object.entries(
                  SCORE_LABELS,
                ).map(([key, config]) => {
                  const Icon = config.icon;
                  const score =
                    result.scores?.[key] ?? 0;

                  return (
                    <div
                      key={key}
                      className="score-item"
                    >
                      <ProgressBar
                        label={config.label}
                        score={score}
                        icon={
                          <Icon
                            size={15}
                            strokeWidth={2}
                          />
                        }
                      />

                      <p className="score-description">
                        {config.description}
                      </p>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* =================================================
                SIGNAL ANALYSIS
            ================================================== */}

            <div className="glass-card findings-panel">
              <div className="panel-heading">
                <div>
                  <span className="section-eyebrow">
                    Observable Signals
                  </span>

                  <h3>
                    <ShieldAlert size={19} />
                    Security Assessment
                  </h3>
                </div>

                <span className="panel-caption">
                  Inspect each signal
                </span>
              </div>

              <div className="analysis-list">
                {ANALYSIS_CATEGORIES.map(
                  (category, index) => {
                    const data =
                      result[category.key];

                    if (!data) {
                      return null;
                    }

                    const Icon = category.icon;
                    const items =
                      getAnalysisItems(data);
                    const text =
                      getAnalysisText(data);

                    const isExpanded =
                      expandedAnalysis ===
                      category.key;

                    const hasContent =
                      items.length > 0 ||
                      Boolean(text);

                    return (
                      <div
                        key={category.key}
                        className={`analysis-card analysis-${category.color}`}
                      >
                        <button
                          type="button"
                          className="analysis-header"
                          onClick={() =>
                            setExpandedAnalysis(
                              isExpanded
                                ? null
                                : category.key,
                            )
                          }
                          aria-expanded={isExpanded}
                        >
                          <span className="analysis-icon">
                            <Icon size={17} />
                          </span>

                          <span className="analysis-title-wrap">
                            <strong>
                              {category.title}
                            </strong>

                            <span>
                              {hasContent
                                ? `${items.length || 1} signal${
                                    (items.length ||
                                      1) === 1
                                      ? ''
                                      : 's'
                                  } available`
                                : 'No detailed signals returned'}
                            </span>
                          </span>

                          <span className="analysis-toggle">
                            {isExpanded ? (
                              <ChevronUp size={18} />
                            ) : (
                              <ChevronDown size={18} />
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
                            className="analysis-details"
                          >
                            {text && (
                              <div className="analysis-summary">
                                <span className="analysis-detail-label">
                                  Assessment
                                </span>

                                <p>{text}</p>
                              </div>
                            )}

                            {items.length > 0 && (
                              <div className="signal-list">
                                <span className="analysis-detail-label">
                                  Detected signals
                                </span>

                                <ul>
                                  {items.map(
                                    (item, itemIndex) => (
                                      <li
                                        key={`${item}-${itemIndex}`}
                                      >
                                        <span className="signal-marker">
                                          {category.color ===
                                          'green'
                                            ? '✓'
                                            : '•'}
                                        </span>

                                        <span>
                                          {item}
                                        </span>
                                      </li>
                                    ),
                                  )}
                                </ul>
                              </div>
                            )}

                            {!hasContent && (
                              <div className="no-analysis-data">
                                <ShieldCheck size={17} />

                                <span>
                                  No additional details were
                                  returned for this signal.
                                </span>
                              </div>
                            )}
                          </motion.div>
                        )}
                      </div>
                    );
                  },
                )}
              </div>
            </div>

            {/* =================================================
                RECOMMENDATIONS
            ================================================== */}

            {result.recommendations?.length > 0 && (
              <div className="glass-card recommendations-panel">
                <div className="recommendations-heading">
                  <div>
                    <span className="section-eyebrow">
                      User Protection
                    </span>

                    <h3>
                      <Lightbulb
                        size={19}
                        className="text-yellow"
                      />
                      Recommended Actions
                    </h3>
                  </div>

                  <span>
                    {result.recommendations.length}{' '}
                    actions
                  </span>
                </div>

                <div className="recs-list">
                  {result.recommendations.map(
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
          </div>

          {/* =====================================================
              SIDEBAR
          ====================================================== */}

          <div className="results-sidebar">
            <ChatPanel
              onSendMessage={handleChat}
              isTyping={isTyping}
            />

            <div className="action-row scanner-action">
              <button
                onClick={reset}
                className="btn btn-secondary w-full"
              >
                Scan Another URL
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

export default WebsiteScanner;