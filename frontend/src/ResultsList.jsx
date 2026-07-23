import { useState } from "react";
import { explainFile } from "./api";

function ResultsList({ recommendations, repoId, onBack }) {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div style={{ textAlign: "center", padding: "2rem 0" }}>
        <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem" }}>
          No matching open issues found for this repo right now.
        </p>
        <button
          onClick={onBack}
          style={{
            background: "none",
            border: "1px solid var(--border)",
            borderRadius: "var(--radius)",
            padding: "0.5rem 1rem",
            color: "var(--accent)",
            cursor: "pointer",
            fontSize: "0.9rem",
          }}
        >
          ← Back to search
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        maxWidth: "640px",
        margin: "0 auto",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      <button
        onClick={onBack}
        style={{
          background: "none",
          border: "none",
          color: "var(--accent)",
          cursor: "pointer",
          fontSize: "0.9rem",
          padding: 0,
          marginBottom: "0.5rem",
          alignSelf: "flex-start",
          display: "flex",
          alignItems: "center",
          gap: "0.3rem",
        }}
      >
        ← Back to search
      </button>

      {recommendations.map((rec) => (
        <IssueCard key={rec.issue_number} rec={rec} repoId={repoId} />
      ))}
    </div>
  );
}

function IssueCard({ rec, repoId }) {
  const [expanded, setExpanded] = useState(false);
  const [explanation, setExplanation] = useState(null);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [showBody, setShowBody] = useState(false);

  const fitPercent = Math.max(
    0,
    Math.min(100, Math.round(rec.similarity * 100)),
  );
  const hasMatchedFile = rec.matched_files && rec.matched_files.length > 0;

  const handleExpand = async () => {
    if (expanded) {
      setExpanded(false);
      return;
    }
    setExpanded(true);
    if (!explanation && hasMatchedFile) {
      setLoadingExplanation(true);
      try {
        const result = await explainFile(repoId, rec.matched_files[0]);
        setExplanation(result);
      } catch (err) {
        console.log(err);
        setExplanation({
          grounded: false,
          explanation: "Could not load explanation right now.",
        });
      }
      setLoadingExplanation(false);
    }
  };

  return (
    <div
      style={{
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)",
        background: "var(--surface)",
        padding: "1.2rem 1.4rem",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "baseline",
        }}
      >
        <span
          className="mono"
          style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}
        >
          #{rec.issue_number}
        </span>
        <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
          {rec.staleness_days === 9999
            ? "no activity date"
            : `updated ${rec.staleness_days}d ago`}
        </span>
      </div>

      <h3
        style={{ margin: "0.4rem 0 0.7rem", fontSize: "1rem", fontWeight: 600 }}
      >
        {rec.title}
      </h3>

      {rec.labels && rec.labels.length > 0 && (
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "0.4rem",
            marginBottom: "0.8rem",
          }}
        >
          {rec.labels.map((label) => (
            <span
              key={label}
              style={{
                fontSize: "0.7rem",
                padding: "0.2rem 0.5rem",
                borderRadius: "4px",
                background: "var(--accent-weak)",
                color: "var(--accent)",
                fontWeight: "500",
              }}
            >
              {label}
            </span>
          ))}
        </div>
      )}

      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "0.6rem",
          marginBottom: "0.8rem",
        }}
      >
        <div
          style={{
            flex: 1,
            height: "6px",
            borderRadius: "3px",
            background: "var(--border)",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${fitPercent}%`,
              height: "100%",
              background: "var(--accent)",
            }}
          />
        </div>
        <span
          style={{
            fontSize: "0.75rem",
            color: "var(--text-muted)",
            whiteSpace: "nowrap",
          }}
        >
          {fitPercent}% match
        </span>
      </div>

      {rec.body && (
        <div style={{ marginBottom: "0.8rem" }}>
          <button
            onClick={() => setShowBody(!showBody)}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent)",
              cursor: "pointer",
              fontSize: "0.85rem",
              padding: 0,
              marginBottom: showBody ? "0.4rem" : 0,
            }}
          >
            {showBody ? "▲ Hide description" : "▼ Show description"}
          </button>
          {showBody && (
            <div
              style={{
                padding: "0.8rem",
                borderRadius: "var(--radius)",
                background: "var(--bg)",
                border: "1px solid var(--border)",
                fontSize: "0.85rem",
                color: "var(--text)",
                maxHeight: "200px",
                overflowY: "auto",
                whiteSpace: "pre-wrap",
              }}
            >
              {rec.body}
            </div>
          )}
        </div>
      )}

      {hasMatchedFile && (
        <>
          <button
            onClick={handleExpand}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent)",
              cursor: "pointer",
              fontSize: "0.85rem",
              padding: 0,
            }}
          >
            {expanded
              ? "▲ Hide reasoning"
              : `▼ Why is ${rec.matched_files[0]} built this way?`}
          </button>

          {expanded && (
            <div
              style={{
                marginTop: "0.8rem",
                paddingTop: "0.8rem",
                borderTop: "1px solid var(--border)",
                fontSize: "0.9rem",
                color: "var(--text)",
              }}
            >
              {loadingExplanation ? (
                <span style={{ color: "var(--text-muted)" }}>
                  Reading commit history...
                </span>
              ) : (
                <p style={{ margin: 0 }}>{explanation?.explanation}</p>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ResultsList;
