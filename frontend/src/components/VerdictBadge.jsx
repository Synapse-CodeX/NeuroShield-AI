import {
  CheckCircle2,
  AlertTriangle,
  XCircle,
  HelpCircle,
  ShieldCheck,
} from 'lucide-react';

const VerdictBadge = ({ verdict }) => {
  const normalized = String(verdict || 'Unknown')
    .trim()
    .toUpperCase();

  const getVerdictConfig = (value) => {
    switch (value) {
      case 'SAFE':
      case 'TRUE':
        return {
          className: 'pill-success',
          icon: CheckCircle2,
        };

      case 'CAUTION':
      case 'PARTIALLY TRUE':
      case 'MODERATE RISK':
        return {
          className: 'pill-warning',
          icon: AlertTriangle,
        };

      case 'SUSPICIOUS':
      case 'HIGH RISK':
        return {
          className: 'pill-accent',
          icon: AlertTriangle,
        };

      case 'DANGEROUS':
      case 'FALSE':
      case 'CRITICAL RISK':
        return {
          className: 'pill-danger',
          icon: XCircle,
        };

      case 'UNVERIFIABLE':
      case 'UNKNOWN':
        return {
          className: 'pill',
          icon: HelpCircle,
        };

      default:
        return {
          className: 'pill',
          icon: ShieldCheck,
        };
    }
  };

  const { className, icon: Icon } = getVerdictConfig(normalized);

  return (
    <span
      className={`pill ${className}`}
      title={`Verdict: ${verdict || 'Unknown'}`}
    >
      <Icon size={14} strokeWidth={2.5} />
      <span>{verdict || 'Unknown'}</span>
    </span>
  );
};

export default VerdictBadge;