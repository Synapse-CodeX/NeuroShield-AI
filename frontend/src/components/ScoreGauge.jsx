import { motion } from 'framer-motion';

const ScoreGauge = ({ score = 0, size = 160 }) => {
  const normalizedScore = Math.max(0, Math.min(100, Number(score) || 0));

  const getScoreColor = (value) => {
    if (value >= 75) return 'var(--color-safe)';
    if (value >= 50) return 'var(--color-caution)';
    if (value >= 25) return 'var(--color-suspicious)';
    return 'var(--color-dangerous)';
  };

  const color = getScoreColor(normalizedScore);

  const strokeWidth = Math.max(8, size * 0.075);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset =
    circumference - (normalizedScore / 100) * circumference;

  return (
    <div
      role="img"
      aria-label={`Safety score ${normalizedScore.toFixed(0)} out of 100`}
      style={{
        position: 'relative',
        width: size,
        height: size,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{
          transform: 'rotate(-90deg)',
          overflow: 'visible',
        }}
        aria-hidden="true"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--bg-tertiary)"
          strokeWidth={strokeWidth}
        />

        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{
            strokeDashoffset: circumference,
          }}
          animate={{
            strokeDashoffset,
          }}
          transition={{
            duration: 1.35,
            ease: 'easeOut',
          }}
          style={{
            filter: `drop-shadow(0 0 7px ${color})`,
          }}
        />
      </svg>

      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <motion.span
          initial={{ opacity: 0, scale: 0.65 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{
            duration: 0.45,
            delay: 0.35,
          }}
          style={{
            fontSize: size * 0.25,
            fontWeight: 850,
            color: 'var(--text-primary)',
            lineHeight: 1,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {normalizedScore.toFixed(0)}
        </motion.span>

        <span
          style={{
            marginTop: 6,
            fontSize: Math.max(10, size * 0.075),
            color: 'var(--text-tertiary)',
            fontWeight: 650,
            letterSpacing: '0.04em',
          }}
        >
          / 100
        </span>
      </div>
    </div>
  );
};

export default ScoreGauge;