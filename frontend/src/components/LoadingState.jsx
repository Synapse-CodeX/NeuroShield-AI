import { useEffect, useState } from 'react';
import './LoadingState.css';

const DEFAULT_STEPS = [
  'Initializing analysis',
  'Inspecting input',
  'Analyzing signals',
  'Correlating evidence',
  'Generating assessment',
];

function LoadingState({ message = 'Analyzing...', steps = DEFAULT_STEPS }) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    if (steps.length <= 1) return undefined;

    const interval = window.setInterval(() => {
      setActiveStep((current) => {
        if (current >= steps.length - 1) {
          return current;
        }

        return current + 1;
      });
    }, 1800);

    return () => window.clearInterval(interval);
  }, [steps]);

  return (
    <div className="loading-state" role="status" aria-live="polite">
      <div className="loading-orb">
        <div className="loading-orb-ring" />
        <div className="loading-orb-core" />
      </div>

      <div className="loading-copy">
        <p className="loading-eyebrow">NEUROSHIELD INTELLIGENCE</p>
        <h3>{message}</h3>
        <p className="loading-subtitle">
          Building an evidence-grounded assessment...
        </p>
      </div>

      <div className="loading-pipeline">
        {steps.map((step, index) => {
          const isComplete = index < activeStep;
          const isActive = index === activeStep;

          return (
            <div
              className={`loading-step ${
                isComplete ? 'complete' : ''
              } ${isActive ? 'active' : ''}`}
              key={step}
            >
              <div className="loading-step-indicator">
                {isComplete ? '✓' : index + 1}
              </div>

              <span>{step}</span>
            </div>
          );
        })}
      </div>

      <div className="loading-progress">
        <div
          className="loading-progress-fill"
          style={{
            width: `${((activeStep + 1) / steps.length) * 100}%`,
          }}
        />
      </div>
    </div>
  );
}

export default LoadingState;