import { motion } from 'framer-motion';
import './ProgressBar.css';

const ProgressBar = ({ label, score = 0, icon }) => {
  const normalizedScore = Math.max(0, Math.min(100, Number(score) || 0));

  const getScoreColor = (value) => {
    if (value >= 75) return 'var(--color-safe)';
    if (value >= 50) return 'var(--color-caution)';
    if (value >= 25) return 'var(--color-suspicious)';
    return 'var(--color-dangerous)';
  };

  const color = getScoreColor(normalizedScore);

  return (
    <div className="progress-container">
      <div className="progress-header">
        <span className="progress-label">
          {icon && <span className="progress-icon">{icon}</span>}
          <span>{label}</span>
        </span>

        <span
          className="progress-score"
          style={{ color }}
        >
          {normalizedScore.toFixed(0)}/100
        </span>
      </div>

      <div
        className="progress-track"
        role="progressbar"
        aria-label={label}
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow={normalizedScore}
      >
        <motion.div
          className="progress-fill"
          initial={{ width: 0 }}
          animate={{ width: `${normalizedScore}%` }}
          transition={{
            duration: 0.9,
            ease: 'easeOut',
            delay: 0.15,
          }}
          style={{
            background: color,
            boxShadow: `0 0 12px ${color}`,
          }}
        />
      </div>
    </div>
  );
};

export default ProgressBar;