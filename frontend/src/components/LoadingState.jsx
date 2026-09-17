import { motion } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import './LoadingState.css';

const LoadingState = ({ message = "Analyzing..." }) => {
  return (
    <div className="loading-state">
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
        className="loading-icon-wrapper"
      >
        <Loader2 className="loading-icon" size={48} />
      </motion.div>
      <h3 className="loading-message gradient-text">{message}</h3>
      <div className="loading-dots">
        <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0 }}>.</motion.span>
        <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.3 }}>.</motion.span>
        <motion.span animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: 1.5, delay: 0.6 }}>.</motion.span>
      </div>
    </div>
  );
};

export default LoadingState;
