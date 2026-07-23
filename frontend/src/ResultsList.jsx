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

      <div style={{ marginTop: "0.8rem" }}>
        <button
          onClick={handleExpand}
          style={{
            background: "none",
            border: "none",
            color: "var(--accent)",
            cursor: "pointer",
            fontSize: "0.85rem",
            padding: 0,
            marginBottom: expanded ? "0.8rem" : 0,
          }}
        >
          {expanded ? "▲ Hide details" : "▼ See description & details"}
        </button>

        {expanded && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
              padding: "1rem",
              borderRadius: "var(--radius)",
              background: "var(--bg)",
              border: "1px solid var(--border)",
              marginTop: "0.5rem",
            }}
          >
            {/* Description */}
            {rec.body ? (
              <div>
                <h4 style={{ margin: "0 0 0.4rem 0", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)" }}>
                  Description
                </h4>
                <div
                  style={{
                    fontSize: "0.85rem",
                    color: "var(--text)",
                    maxHeight: "200px",
                    overflowY: "auto",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {rec.body}
                </div>
              </div>
            ) : (
              <div>
                <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                  No description provided for this issue.
                </span>
              </div>
            )}

            {/* Files Context */}
            <div style={{ borderTop: "1px solid var(--border)", paddingTop: "0.8rem" }}>
              <h4 style={{ margin: "0 0 0.6rem 0", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)" }}>
                Codebase Files Context
              </h4>

              {hasMatchedFile ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                  {/* Directly Matched Files */}
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", alignItems: "center" }}>
                    <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginRight: "0.2rem" }}>
                      Matched Files:
                    </span>
                    {rec.matched_files.map((file) => (
                      <span
                        key={file}
                        className="mono"
                        style={{
                          fontSize: "0.7rem",
                          padding: "0.2rem 0.5rem",
                          borderRadius: "4px",
                          background: "var(--surface)",
                          border: "1px solid var(--border)",
                          color: "var(--text-muted)",
                        }}
                      >
                        {file}
                      </span>
                    ))}
                  </div>

                  {/* Related Files */}
                  {rec.related_files && rec.related_files.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", alignItems: "center" }}>
                      <span style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginRight: "0.2rem" }}>
                        Related (co-changed):
                      </span>
                      {rec.related_files.map((file) => (
                        <span
                          key={file}
                          className="mono"
                          style={{
                            fontSize: "0.65rem",
                            padding: "0.15rem 0.4rem",
                            borderRadius: "4px",
                            background: "var(--surface)",
                            border: "1px solid var(--border)",
                            color: "var(--text-muted)",
                          }}
                        >
                          {file}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Why Grounding Explanation */}
                  <div style={{ marginTop: "0.4rem", borderTop: "1px dashed var(--border)", paddingTop: "0.8rem" }}>
                    <h5 style={{ margin: "0 0 0.4rem 0", fontSize: "0.75rem", color: "var(--text-muted)" }}>
                      Why is {rec.matched_files[0]} built this way?
                    </h5>
                    {loadingExplanation ? (
                      <span style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                        Reading commit history...
                      </span>
                    ) : (
                      <p style={{ margin: 0, fontSize: "0.85rem", color: "var(--text)", lineHeight: 1.4 }}>
                        {explanation?.explanation || "Failed to load explanation."}
                      </p>
                    )}
                  </div>
                </div>
              ) : (
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontStyle: "italic" }}>
                  No specific file could be identified from this issue's description.
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ResultsList;
