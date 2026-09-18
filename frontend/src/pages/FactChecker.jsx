import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import {
  CheckSquare,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  ShieldCheck,
  XCircle,
  Search,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { checkFacts } from '../services/api';

import LoadingState from '../components/LoadingState';
import VerdictBadge from '../components/VerdictBadge';
import EvidenceCard from '../components/EvidenceCard';
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
    setExpandedClaim(null);
    setShowFullReport(false);

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

    const counts = {
      True: 0,
      False: 0,
      'Partially True': 0,
      Unverifiable: 0,
    };

    Object.values(result.verifications).forEach((verification) => {
      if (counts[verification.verdict] !== undefined) {
        counts[verification.verdict]++;
      }
    });

    return counts;
  };

  const getEvidenceRole = (source, verification) => {
    const url = source?.url;

    if (!url || !verification) {
      return 'Retrieved';
    }

    if (verification.supporting_sources?.includes(url)) {
      return 'Supporting';
    }

    if (verification.conflicting_sources?.includes(url)) {
      return 'Conflicting';
    }

    return 'Retrieved';
  };

  const getEvidenceGroups = (evidence, verification) => {
    const supporting = [];
    const conflicting = [];
    const retrieved = [];

    evidence.forEach((source) => {
      const role = getEvidenceRole(source, verification);

      if (role === 'Supporting') {
        supporting.push(source);
      } else if (role === 'Conflicting') {
        conflicting.push(source);
      } else {
        retrieved.push(source);
      }
    });

    return {
      supporting,
      conflicting,
      retrieved,
    };
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="factcheck-page container section"
    >
      <div className="page-header">
        <h1>
          <CheckSquare className="inline-icon" />
          AI Fact Checker
        </h1>

        <p>
          Verify claims using our evidence-first RAG pipeline that
          cross-references retrieved sources across the web.
        </p>
      </div>

      {!result && !isChecking && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="input-section glass-card"
        >
          <textarea
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="Paste text containing claims you want to verify (e.g., news article, social media post)..."
            className="textarea-field"
          />

          <div className="input-actions">
            <span className="char-count">
              {text.length} characters
            </span>

            <button
              onClick={handleCheck}
              className="btn btn-primary"
              disabled={!text.trim()}
            >
              Verify Facts
            </button>
          </div>
        </motion.div>
      )}

      {isChecking && (
        <LoadingState message="Extracting claims and searching the web..." />
      )}

      {result && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="results-container"
        >
          {/* =====================================================
              SUMMARY
          ====================================================== */}

          <div className="summary-bar glass-card">
            <div className="summary-stat">
              <span className="stat-value">
                {result.claims?.length || 0}
              </span>

              <span className="stat-label">
                Claims Found
              </span>
            </div>

            <div className="verdict-counts">
              {Object.entries(getVerdictCounts()).map(
                ([verdict, count]) => (
                  <div
                    key={verdict}
                    className="count-pill"
                  >
                    <VerdictBadge verdict={verdict} />
                    <span className="count-number">
                      {count}
                    </span>
                  </div>
                ),
              )}
            </div>

            <button
              onClick={reset}
              className="btn btn-ghost"
            >
              Check Another
            </button>
          </div>

          {/* =====================================================
              CLAIMS
          ====================================================== */}

          <div className="claims-list">
            <div className="claims-list-header">
              <div>
                <span className="section-eyebrow">
                  Evidence Analysis
                </span>

                <h3>Analyzed Claims</h3>
              </div>

              <span className="claims-list-hint">
                Expand a claim to inspect its evidence
              </span>
            </div>

            {result.claims?.length === 0 ? (
              <div className="glass-card empty-state">
                <AlertCircle
                  size={48}
                  className="empty-icon"
                />

                <h3>No verifiable claims found</h3>

                <p>
                  The submitted text did not contain claims that
                  could be extracted for verification.
                </p>
              </div>
            ) : (
              result.claims?.map((claim) => {
                const verification =
                  result.verifications?.[claim.id];

                const evidence =
                  result.evidence?.[claim.id] || [];

                const isExpanded =
                  expandedClaim === claim.id;

                if (!verification) {
                  return null;
                }

                const {
                  supporting,
                  conflicting,
                  retrieved,
                } = getEvidenceGroups(
                  evidence,
                  verification,
                );

                const totalEvidence =
                  evidence.length;

                return (
                  <motion.div
                    key={claim.id}
                    layout
                    className="claim-card glass-card"
                  >
                    <button
                      type="button"
                      className="claim-header"
                      onClick={() =>
                        setExpandedClaim(
                          isExpanded
                            ? null
                            : claim.id,
                        )
                      }
                      aria-expanded={isExpanded}
                    >
                      <div className="claim-main">
                        <div className="claim-meta">
                          <span className="pill">
                            {claim.type}
                          </span>

                          <VerdictBadge
                            verdict={
                              verification.verdict
                            }
                          />

                          <span
                            className="confidence-pill"
                            title={`Confidence: ${(
                              verification.confidence *
                              100
                            ).toFixed(0)}%`}
                          >
                            {Math.round(
                              verification.confidence *
                                100,
                            )}
                            % Confidence
                          </span>

                          <span className="evidence-count-pill">
                            <Search size={12} />
                            {totalEvidence}{' '}
                            {totalEvidence === 1
                              ? 'source'
                              : 'sources'}
                          </span>
                        </div>

                        <h4 className="claim-text">
                          "{claim.claim}"
                        </h4>
                      </div>

                      <span className="expand-btn">
                        {isExpanded ? (
                          <ChevronUp size={20} />
                        ) : (
                          <ChevronDown size={20} />
                        )}
                      </span>
                    </button>

                    <AnimatePresence>
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
                          exit={{
                            height: 0,
                            opacity: 0,
                          }}
                          className="claim-details"
                        >
                          {/* =================================================
                              VERIFICATION REASONING
                          ================================================== */}

                          <div className="reasoning-box">
                            <div className="detail-heading">
                              <span className="detail-heading-icon">
                                <ShieldCheck size={15} />
                              </span>

                              <span>
                                Verification reasoning
                              </span>
                            </div>

                            <p>
                              {verification.reason ||
                                'No reasoning was provided.'}
                            </p>
                          </div>

                          {/* =================================================
                              EVIDENCE
                          ================================================== */}

                          {evidence.length > 0 ? (
                            <div className="evidence-section">
                              <div className="evidence-section-header">
                                <div>
                                  <span className="section-eyebrow">
                                    Evidence Layer
                                  </span>

                                  <h4>
                                    Sources considered
                                  </h4>
                                </div>

                                <span className="evidence-total">
                                  {totalEvidence}{' '}
                                  {totalEvidence === 1
                                    ? 'source'
                                    : 'sources'}{' '}
                                  retrieved
                                </span>
                              </div>

                              {/* Supporting */}
                              {supporting.length > 0 && (
                                <div className="evidence-group">
                                  <div className="evidence-group-header supporting-header">
                                    <ShieldCheck size={16} />

                                    <div>
                                      <strong>
                                        Supporting Evidence
                                      </strong>

                                      <span>
                                        Sources that support
                                        the verification result
                                      </span>
                                    </div>

                                    <span className="evidence-group-count">
                                      {supporting.length}
                                    </span>
                                  </div>

                                  <div className="sources-grid">
                                    {supporting.map(
                                      (source, index) => (
                                        <EvidenceCard
                                          key={`supporting-${source.url}-${index}`}
                                          evidence={source}
                                          role="Supporting"
                                        />
                                      ),
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* Conflicting */}
                              {conflicting.length > 0 && (
                                <div className="evidence-group">
                                  <div className="evidence-group-header conflicting-header">
                                    <XCircle size={16} />

                                    <div>
                                      <strong>
                                        Conflicting Evidence
                                      </strong>

                                      <span>
                                        Sources that contradict
                                        or qualify the claim
                                      </span>
                                    </div>

                                    <span className="evidence-group-count">
                                      {conflicting.length}
                                    </span>
                                  </div>

                                  <div className="sources-grid">
                                    {conflicting.map(
                                      (source, index) => (
                                        <EvidenceCard
                                          key={`conflicting-${source.url}-${index}`}
                                          evidence={source}
                                          role="Conflicting"
                                        />
                                      ),
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* Retrieved but not explicitly classified */}
                              {retrieved.length > 0 && (
                                <div className="evidence-group">
                                  <div className="evidence-group-header retrieved-header">
                                    <Search size={16} />

                                    <div>
                                      <strong>
                                        Additional Retrieved Evidence
                                      </strong>

                                      <span>
                                        Sources retrieved for
                                        context but not explicitly
                                        classified by the verifier
                                      </span>
                                    </div>

                                    <span className="evidence-group-count">
                                      {retrieved.length}
                                    </span>
                                  </div>

                                  <div className="sources-grid">
                                    {retrieved.map(
                                      (source, index) => (
                                        <EvidenceCard
                                          key={`retrieved-${source.url}-${index}`}
                                          evidence={source}
                                          role="Retrieved"
                                        />
                                      ),
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          ) : (
                            <div className="no-evidence-box">
                              <Search size={18} />

                              <div>
                                <strong>
                                  No web evidence retrieved
                                </strong>

                                <span>
                                  The claim could not be verified
                                  because no usable source evidence
                                  was returned.
                                </span>
                              </div>
                            </div>
                          )}

                          {/* =================================================
                              UNCERTAINTY
                          ================================================== */}

                          {verification.uncertainty_reason && (
                            <div className="uncertainty-box">
                              <AlertCircle size={17} />

                              <div>
                                <strong>
                                  Verification uncertainty
                                </strong>

                                <span>
                                  {
                                    verification.uncertainty_reason
                                  }
                                </span>
                              </div>
                            </div>
                          )}
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                );
              })
            )}
          </div>

          {/* =====================================================
              FULL REPORT
          ====================================================== */}

          {result.final_report && (
            <div className="report-section glass-card">
              <button
                type="button"
                className="report-header"
                onClick={() =>
                  setShowFullReport(!showFullReport)
                }
                aria-expanded={showFullReport}
              >
                <div>
                  <span className="section-eyebrow">
                    Generated Analysis
                  </span>

                  <h3>Full Narrative Report</h3>
                </div>

                <span className="btn btn-ghost">
                  {showFullReport
                    ? 'Hide Report'
                    : 'Show Report'}
                </span>
              </button>

              <AnimatePresence>
                {showFullReport && (
                  <motion.div
                    initial={{
                      height: 0,
                      opacity: 0,
                    }}
                    animate={{
                      height: 'auto',
                      opacity: 1,
                    }}
                    exit={{
                      height: 0,
                      opacity: 0,
                    }}
                    className="full-report-content"
                  >
                    <div className="markdown-content">
                      <ReactMarkdown>
                        {result.final_report}
                      </ReactMarkdown>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
};

export default FactChecker;