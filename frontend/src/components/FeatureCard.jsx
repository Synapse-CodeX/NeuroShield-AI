import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import './FeatureCard.css';

const FeatureCard = ({ icon: Icon, title, description, linkTo, delay = 0 }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5, delay }}
      className="feature-card glass-card"
    >
      <div className="feature-icon-wrapper">
        <Icon size={28} className="feature-icon" />
      </div>
      <h3 className="feature-title">{title}</h3>
      <p className="feature-description">{description}</p>
      {linkTo && (
        <Link to={linkTo} className="feature-link">
          Try it out <span className="arrow">→</span>
        </Link>
      )}
    </motion.div>
  );
};

export default FeatureCard;
