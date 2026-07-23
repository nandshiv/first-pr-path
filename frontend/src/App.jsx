import { useState } from "react";
import ThemeToggle from "./ThemeToggle";
import IntakeForm from "./IntakeForm";
import { createRepo, getRecommendations } from "./api";
import ResultsList from "./ResultsList";

function App() {
  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [recommendations, setRecommendations] = useState(null);
  const [repoId, setRepoId] = useState(null);

  const handleFormSubmit = async ({ repoUrl, skillProfileText }) => {
    setStatus("loading");
    setErrorMessage("");

    try {
      const repo = await createRepo(repoUrl);
      setRepoId(repo.id);
      const results = await getRecommendations(repo.id, skillProfileText);

      if (!results || results.length === 0) {
        setErrorMessage(
          "No matching open issues found for this repo yet. Try a different repo.",
        );
        setStatus("error");
        return;
      }

      setRecommendations(results);
      setStatus("done");
    } catch (err) {
      console.error(err);
      setErrorMessage(
        err.message || "Something went wrong. Check the console for details.",
      );
      setStatus("error");
    }
  };

  const handleBack = () => {
    setStatus("idle");
    setRecommendations(null);
    setRepoId(null);
    setErrorMessage("");
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <header className="app-header">
        <h2 style={{ margin: 0, fontSize: "1.1rem" }}>First PR Path</h2>
        <ThemeToggle />
      </header>

      <main className="app-main">
        {(status === "idle" || status === "error") && (
          <IntakeForm
            onSubmit={handleFormSubmit}
            isSubmitting={false}
          />
        )}

        {status === "loading" && (
          <div style={{ maxWidth: "640px", margin: "0 auto" }}>
            <h3
              style={{
                textAlign: "center",
                color: "var(--text-muted)",
                marginBottom: "2rem",
                fontSize: "1rem",
                fontWeight: 500,
              }}
            >
              Analyzing repository and matching issues...
            </h3>
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton-card">
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: "0.5rem",
                  }}
                >
                  <div className="skeleton-bar meta" />
                  <div className="skeleton-bar meta" style={{ width: "20%" }} />
                </div>
                <div className="skeleton-bar title" />
                <div
                  className="skeleton-bar badge"
                  style={{ width: "60px", marginBottom: "0.5rem" }}
                />
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.6rem",
                    marginTop: "0.5rem",
                  }}
                >
                  <div className="skeleton-bar progress" style={{ flex: 1 }} />
                  <div className="skeleton-bar meta" style={{ width: "50px" }} />
                </div>
              </div>
            ))}
          </div>
        )}

        {status === "error" && (
          <p
            style={{
              textAlign: "center",
              color: "#B3441E",
              marginTop: "1.5rem",
              maxWidth: "480px",
              margin: "1.5rem auto 0",
            }}
          >
            {errorMessage}
          </p>
        )}

        {status === "done" && (
          <ResultsList
            recommendations={recommendations}
            repoId={repoId}
            onBack={handleBack}
          />
        )}
      </main>
    </div>
  );
}

export default App;
