import { Mail, Globe } from 'lucide-react';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container footer-container">
        <div className="footer-brand">
          <span className="logo-text gradient-text">NeuroShield</span>
          <p className="footer-tagline">AI-Powered Digital Safety</p>
        </div>
        <div className="footer-links">
          <a href="#" className="footer-link"><Mail size={20} /></a>
          <a href="#" className="footer-link"><Globe size={20} /></a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
