import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  CheckSquare,
  ExternalLink,
  FileSearch,
  Lock,
  Search,
  Shield,
  Sparkles,
} from 'lucide-react';

import heroImage from '../assets/hero.png';
import FeatureCard from '../components/FeatureCard';
import './LandingPage.css';

const intelligenceModules = [
  {
    icon: Shield,
    title: 'Privacy Intelligence',
    description:
      'Turn long privacy policies into clear findings, risk signals, evidence, and actionable recommendations.',
    linkTo: '/privacy',
    delay: 0.1,
  },
  {
    icon: CheckSquare,
    title: 'Fact Intelligence',
    description:
      'Break claims into atomic statements and verify them against retrieved web evidence and source credibility.',
    linkTo: '/factcheck',
    delay: 0.2,
  },
  {
    icon: Search,
    title: 'Site Intelligence',
    description:
      'Inspect URLs, SSL, domain signals, content quality, reputation, and scam indicators before you trust a site.',
    linkTo: '/scanner',
    delay: 0.3,
  },
];

const workflow = [
  {
    number: '01',
    icon: FileSearch,
    title: 'Detect',
    description:
      'Identify risks, claims, suspicious signals, and relevant patterns.',
  },
  {
    number: '02',
    icon: Search,
    title: 'Verify',
    description:
      'Retrieve supporting evidence and cross-check the available signals.',
  },
  {
    number: '03',
    icon: Sparkles,
    title: 'Explain',
    description:
      'Turn technical analysis into clear, understandable findings.',
  },
  {
    number: '04',
    icon: ArrowRight,
    title: 'Recommend',
    description:
      'Surface practical next steps based on the analysis.',
  },
];

const LandingPage = () => {
  return (
    <div className="landing-page">
      {/* =========================================================
          HERO
          ========================================================= */}
      <section className="hero-section">
        <div className="hero-background-orb hero-background-orb-one" />
        <div className="hero-background-orb hero-background-orb-two" />

        <div className="container hero-container">
          <motion.div
            initial={{ opacity: 0, y: 28 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="hero-content"
          >
            <div className="hero-badge">
              <Lock size={15} />
              <span>AI-POWERED WEB TRUST LAYER</span>
            </div>

            <h1 className="hero-title">
              Navigate the web
              <br />
              with <span className="gradient-text">confidence.</span>
            </h1>

            <p className="hero-subtitle">
              NeuroShield detects risks, verifies information, explains the
              evidence, and recommends safer actions across websites, privacy
              policies, and online claims.
            </p>

            <div className="hero-cta">
              <Link to="/scanner" className="btn btn-primary btn-lg">
                Scan a Website
                <ArrowRight size={18} />
              </Link>

              <Link to="/factcheck" className="btn btn-secondary btn-lg">
                Verify a Claim
              </Link>
            </div>

            <div className="hero-trust-row">
              <div className="hero-trust-item">
                <span className="hero-trust-dot" />
                <span>Evidence-first analysis</span>
              </div>

              <div className="hero-trust-divider" />

              <div className="hero-trust-item">
                <span className="hero-trust-dot" />
                <span>Explainable findings</span>
              </div>

              <div className="hero-trust-divider" />

              <div className="hero-trust-item">
                <span className="hero-trust-dot" />
                <span>Actionable recommendations</span>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.92, x: 20 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.15 }}
            className="hero-visual"
          >
            <div className="hero-glow-orb" />

            <div className="hero-image-frame">
              <div className="hero-image-shine" />

              <img
                src={heroImage}
                alt="NeuroShield security intelligence interface"
                className="hero-image"
              />

              <div className="hero-floating-card hero-floating-card-top">
                <div className="floating-card-icon">
                  <Shield size={16} />
                </div>
                <div>
                  <span>Security signals</span>
                  <strong>Analyzed</strong>
                </div>
              </div>

              <div className="hero-floating-card hero-floating-card-bottom">
                <div className="floating-card-status">
                  <span />
                  Evidence grounded
                </div>
                <ExternalLink size={14} />
              </div>
            </div>
          </motion.div>
        </div>

        <motion.div
          className="hero-scroll-hint"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1, duration: 0.5 }}
        >
          <span>Explore intelligence</span>
          <div className="hero-scroll-line" />
        </motion.div>
      </section>

      {/* =========================================================
          POSITIONING
          ========================================================= */}
      <section className="positioning-section">
        <div className="container">
          <motion.div
            className="positioning-card"
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: '-80px' }}
            transition={{ duration: 0.6 }}
          >
            <div className="positioning-label">
              <span className="positioning-label-line" />
              <span>THE NEUROSHIELD APPROACH</span>
            </div>

            <h2>
              Don't just get an AI answer.
              <br />
              <span className="gradient-text">Understand why.</span>
            </h2>

            <p>
              Every analysis is designed around observable signals, retrieved
              evidence, structured findings, and clear explanations—so users
              can inspect the reasoning behind a result.
            </p>
          </motion.div>
        </div>
      </section>

      {/* =========================================================
          CORE INTELLIGENCE
          ========================================================= */}
      <section className="section features-section">
        <div className="container">
          <motion.div
            className="section-header landing-section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="section-kicker">
              <Sparkles size={14} />
              THREE INTELLIGENCE LAYERS
            </div>

            <h2>Your web trust toolkit.</h2>

            <p>
              Three specialized analysis systems designed around different
              types of online risk and uncertainty.
            </p>
          </motion.div>

          <div className="features-grid">
            {intelligenceModules.map((module) => (
              <FeatureCard
                key={module.title}
                icon={module.icon}
                title={module.title}
                description={module.description}
                linkTo={module.linkTo}
                delay={module.delay}
              />
            ))}
          </div>
        </div>
      </section>

      {/* =========================================================
          WORKFLOW
          ========================================================= */}
      <section className="section workflow-section">
        <div className="container">
          <motion.div
            className="section-header landing-section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <div className="section-kicker">
              <Search size={14} />
              EVIDENCE-FIRST WORKFLOW
            </div>

            <h2>From signal to decision context.</h2>

            <p>
              NeuroShield transforms raw online information into a structured
              analysis that users can actually understand.
            </p>
          </motion.div>

          <div className="workflow-container">
            <div className="workflow-line" />

            {workflow.map((step, index) => {
              const Icon = step.icon;

              return (
                <motion.div
                  key={step.number}
                  className="workflow-step"
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: '-60px' }}
                  transition={{
                    duration: 0.5,
                    delay: index * 0.1,
                  }}
                >
                  <div className="workflow-number">{step.number}</div>

                  <div className="workflow-icon">
                    <Icon size={20} />
                  </div>

                  <h3>{step.title}</h3>

                  <p>{step.description}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* =========================================================
          FINAL CTA
          ========================================================= */}
      <section className="section final-cta-section">
        <div className="container">
          <motion.div
            className="final-cta-card"
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <div className="final-cta-glow" />

            <div className="final-cta-content">
              <div className="section-kicker">
                <Shield size={14} />
                NEUROSHIELD
              </div>

              <h2>
                Before you trust it,
                <br />
                <span className="gradient-text">check it.</span>
              </h2>

              <p>
                Analyze a website, verify a claim, or understand what a privacy
                policy is really asking for.
              </p>

              <div className="final-cta-actions">
                <Link to="/scanner" className="btn btn-primary btn-lg">
                  Start an Analysis
                  <ArrowRight size={18} />
                </Link>

                <Link to="/privacy" className="btn btn-secondary btn-lg">
                  Analyze a Privacy Policy
                </Link>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;