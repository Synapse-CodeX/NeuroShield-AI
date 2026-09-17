import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Shield, CheckSquare, Search, Lock } from 'lucide-react';
import FeatureCard from '../components/FeatureCard';
import './LandingPage.css';

const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="container hero-container">
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="hero-content"
          >
            <div className="hero-badge">
              <Lock size={16} />
              <span>Next-Gen Digital Protection</span>
            </div>
            <h1 className="hero-title">
              AI-Powered <br/>
              <span className="gradient-text animate-pulse-glow">Digital Safety</span>
            </h1>
            <p className="hero-subtitle">
              Protect yourself online with our advanced AI analysis tools. We scan privacy policies, fact-check claims, and analyze websites for threats in seconds.
            </p>
            <div className="hero-cta">
              <Link to="/scanner" className="btn btn-primary btn-lg">Scan a Website</Link>
              <Link to="/factcheck" className="btn btn-secondary btn-lg">Verify Facts</Link>
            </div>
          </motion.div>
          
          <motion.div 
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="hero-visual animate-float"
          >
            <div className="hero-glow-orb"></div>
            <div className="glass-card hero-mockup">
              <div className="mockup-header">
                <span className="dot red"></span>
                <span className="dot yellow"></span>
                <span className="dot green"></span>
              </div>
              <div className="mockup-body">
                <Shield size={48} className="mockup-icon" />
                <div className="mockup-line w-3/4"></div>
                <div className="mockup-line w-1/2"></div>
                <div className="mockup-line w-5/6"></div>
                <div className="mockup-verdict safe">VERIFIED SAFE</div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section features-section">
        <div className="container">
          <div className="section-header">
            <h2>Our Core Tools</h2>
            <p>Comprehensive protection across all your digital touchpoints.</p>
          </div>
          
          <div className="features-grid">
            <FeatureCard 
              icon={Shield}
              title="Privacy Policy Analyzer"
              description="Instantly understand what data companies collect and how they use it. We highlight the risks so you don't have to read 50 pages of legalese."
              linkTo="/privacy"
              delay={0.1}
            />
            <FeatureCard 
              icon={CheckSquare}
              title="AI Fact Checker"
              description="Verify claims using our advanced RAG pipeline that cross-references trusted sources across the web to bring you the truth."
              linkTo="/factcheck"
              delay={0.2}
            />
            <FeatureCard 
              icon={Search}
              title="Website Safety Scanner"
              description="Detect phishing, scams, and dangerous domains before you click. We analyze URLs, SSL certs, and domain age in real-time."
              linkTo="/scanner"
              delay={0.3}
            />
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="section how-it-works-section">
        <div className="container">
          <div className="section-header text-center">
            <h2>How NeuroShield Works</h2>
          </div>
          <div className="steps-container">
            {[
              { num: '01', title: 'Provide Input', desc: 'Paste text, a URL, or a policy.' },
              { num: '02', title: 'AI Analysis', desc: 'Our LangGraph agents process the data.' },
              { num: '03', title: 'Get Results', desc: 'Clear, actionable insights & scores.' },
            ].map((step, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.2 }}
                className="step-card"
              >
                <div className="step-number gradient-text">{step.num}</div>
                <h3>{step.title}</h3>
                <p>{step.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
