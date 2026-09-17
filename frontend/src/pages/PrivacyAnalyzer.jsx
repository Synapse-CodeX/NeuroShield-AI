import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { Shield, AlertTriangle, Info, ShieldCheck } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { analyzePrivacy, chatPrivacy } from '../services/api';

import ScoreGauge from '../components/ScoreGauge';
import LoadingState from '../components/LoadingState';
import ChatPanel from '../components/ChatPanel';
import './PrivacyAnalyzer.css';

const PrivacyAnalyzer = () => {
  const [text, setText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [isTyping, setIsTyping] = useState(false);

  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast.error('Please enter a privacy policy to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setResult(null);

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
      const data = await chatPrivacy(question, result.session_id);
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
  };

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="privacy-page container section"
    >
      <div className="page-header">
        <h1><Shield className="inline-icon" /> Privacy Policy Analyzer</h1>
        <p>Paste any privacy policy text below to instantly extract key data, assess risks, and generate a simple summary.</p>
      </div>

      {!result && !isAnalyzing && (
        <motion.div initial={{ y: 20 }} animate={{ y: 0 }} className="input-section glass-card">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste privacy policy text here..."
            className="textarea-field"
          />
          <div className="input-actions">
            <span className="char-count">{text.length} characters</span>
            <button onClick={handleAnalyze} className="btn btn-primary" disabled={!text.trim()}>
              Analyze Policy
            </button>
          </div>
        </motion.div>
      )}

      {isAnalyzing && (
        <LoadingState message="Analyzing Privacy Policy..." />
      )}

      {result && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="results-grid">
          
          {/* Main Content Area */}
          <div className="results-main">
            {/* Score & Summary Banner */}
            <div className="glass-card summary-banner">
              <div className="score-section">
                <ScoreGauge score={result.score} size={140} />
                <div className="risk-level">
                  <span className="risk-label">Risk Level</span>
                  <h3 className={`risk-value ${result.risk_level?.toLowerCase()}`}>
                    {result.risk_level}
                  </h3>
                </div>
              </div>
              <div className="summary-section">
                <h3><Info size={20}/> Simple Summary</h3>
                <div className="markdown-content">
                  <ReactMarkdown>{result.summary}</ReactMarkdown>
                </div>
              </div>
            </div>

            {/* Risks Panel */}
            {result.risks && result.risks.length > 0 ? (
              <div className="glass-card risks-panel">
                <h3 className="panel-title danger">
                  <AlertTriangle size={20} /> Detected Risks
                </h3>
                <ul className="risk-list">
                  {result.risks.map((risk, idx) => (
                    <li key={idx}>⚠️ {risk}</li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="glass-card risks-panel safe">
                <h3 className="panel-title success">
                  <ShieldCheck size={20} /> No Major Risks Detected
                </h3>
              </div>
            )}

            {/* Structured Data */}
            <div className="glass-card data-panel">
              <h3 className="panel-title">Extracted Details</h3>
              <div className="data-grid">
                {Object.entries(result.structured_data || {}).map(([key, value]) => {
                  if (!value || (Array.isArray(value) && value.length === 0)) return null;
                  
                  const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                  
                  return (
                    <div key={key} className="data-group">
                      <h4>{formattedKey}</h4>
                      {Array.isArray(value) ? (
                        <div className="pill-container">
                          {value.map((item, i) => (
                            <span key={i} className="pill pill-accent">{item}</span>
                          ))}
                        </div>
                      ) : (
                        <p>{value}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="action-row">
              <button onClick={reset} className="btn btn-secondary">Analyze Another Policy</button>
            </div>
          </div>

          {/* Chat Sidebar */}
          <div className="results-sidebar">
            <ChatPanel onSendMessage={handleChat} isTyping={isTyping} />
          </div>

        </motion.div>
      )}
    </motion.div>
  );
};

export default PrivacyAnalyzer;
