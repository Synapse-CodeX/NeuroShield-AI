import {
  ExternalLink,
  Globe,
  ShieldCheck,
  Search,
} from "lucide-react";
import "./EvidenceCard.css";

function percentage(value) {
  if (value === null || value === undefined) {
    return null;
  }

  return `${Math.round(
    Math.max(0, Math.min(1, Number(value))) * 100,
  )}%`;
}

function EvidenceCard({
  evidence,
  role = "Retrieved",
}) {
  if (!evidence) {
    return null;
  }

  const relevance = percentage(evidence.score);
  const credibility = percentage(evidence.credibility);

  const roleClass = role.toLowerCase().replace(/\s+/g, "-");

  return (
    <article className={`evidence-card ${roleClass}`}>
      <div className="evidence-card__top">
        <div className="evidence-card__source">
          <div className="evidence-card__icon">
            <Globe size={16} />
          </div>

          <div className="evidence-card__identity">
            <h4>
              {evidence.title || "Untitled source"}
            </h4>

            {evidence.url && (
              <span className="evidence-card__domain">
                {(() => {
                  try {
                    return new URL(evidence.url).hostname;
                  } catch {
                    return evidence.url;
                  }
                })()}
              </span>
            )}
          </div>
        </div>

        <span className={`evidence-card__role ${roleClass}`}>
          {role === "Supporting" && (
            <ShieldCheck size={13} />
          )}

          {role === "Retrieved" && (
            <Search size={13} />
          )}

          {role}
        </span>
      </div>

      {evidence.content && (
        <div className="evidence-card__excerpt">
          <span className="evidence-card__excerpt-label">
            Evidence
          </span>

          <p>
            {evidence.content}
          </p>
        </div>
      )}

      <div className="evidence-card__metrics">
        {relevance !== null && (
          <div className="evidence-metric">
            <span>Retrieval relevance</span>
            <strong>{relevance}</strong>
          </div>
        )}

        {credibility !== null && (
          <div className="evidence-metric">
            <span>Source credibility</span>
            <strong>{credibility}</strong>
          </div>
        )}
      </div>

      {evidence.query_used && (
        <div className="evidence-card__query">
          <Search size={13} />

          <span>
            Search: {evidence.query_used}
          </span>
        </div>
      )}

      {evidence.url && (
        <a
          className="evidence-card__link"
          href={evidence.url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Open source
          <ExternalLink size={14} />
        </a>
      )}
    </article>
  );
}

export default EvidenceCard;