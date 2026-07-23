import { useState } from "react";

const LANGUAGE_OPTIONS = [
  "Python",
  "JavaScript",
  "TypeScript",
  "React",
  "Go",
  "Rust",
];
const EXPERIENCE_OPTIONS = [
  "New to open source",
  "Some experience",
  "Experienced",
];

function IntakeForm({ onSubmit, isSubmitting }) {
  const [repoUrl, setRepoUrl] = useState("");
  const [selectedLanguages, setSelectedLanguages] = useState([]);
  const [experience, setExperience] = useState("New to open source");
  const [interests, setInterests] = useState("");

  const toggleLanguage = (lang) => {
    if (selectedLanguages.includes(lang)) {
      setSelectedLanguages(selectedLanguages.filter((l) => l !== lang));
    } else {
      setSelectedLanguages([...selectedLanguages, lang]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const skillProfileText = `Comfortable with ${selectedLanguages.join(", ") || "no specific languages"}. ${experience}. Interested in ${interests || "anything"}.`;
    onSubmit({ repoUrl, skillProfileText });
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{ maxWidth: "480px", margin: "0 auto" }}
    >
      <label
        htmlFor="repo-url"
        style={{
          display: "block",
          marginBottom: "0.4rem",
          fontSize: "0.9rem",
          color: "var(--text-muted)",
        }}
      >
        GitHub repo URL
      </label>
      <input
        id="repo-url"
        type="text"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        placeholder="https://github.com/owner/repo"
        required
        style={{
          width: "100%",
          padding: "0.6rem 0.8rem",
          borderRadius: "var(--radius)",
          border: "1px solid var(--border)",
          background: "var(--surface)",
          color: "var(--text)",
          fontFamily: "monospace",
          marginBottom: "1.2rem",
        }}
      />

      <span
        id="languages-label"
        style={{
          display: "block",
          marginBottom: "0.4rem",
          fontSize: "0.9rem",
          color: "var(--text-muted)",
        }}
      >
        Languages you know
      </span>
      <div
        role="group"
        aria-labelledby="languages-label"
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          marginBottom: "1.2rem",
        }}
      >
        {LANGUAGE_OPTIONS.map((lang) => (
          <button
            type="button"
            key={lang}
            onClick={() => toggleLanguage(lang)}
            style={{
              padding: "0.4rem 0.8rem",
              borderRadius: "var(--radius)",
              border: "1px solid var(--border)",
              background: selectedLanguages.includes(lang)
                ? "var(--accent-weak)"
                : "var(--surface)",
              color: selectedLanguages.includes(lang)
                ? "var(--accent)"
                : "var(--text)",
              cursor: "pointer",
              fontSize: "0.85rem",
            }}
          >
            {lang}
          </button>
        ))}
      </div>

      <label
        htmlFor="experience-level"
        style={{
          display: "block",
          marginBottom: "0.4rem",
          fontSize: "0.9rem",
          color: "var(--text-muted)",
        }}
      >
        Experience level
      </label>
      <select
        id="experience-level"
        value={experience}
        onChange={(e) => setExperience(e.target.value)}
        style={{
          width: "100%",
          padding: "0.6rem 0.8rem",
          borderRadius: "var(--radius)",
          border: "1px solid var(--border)",
          background: "var(--surface)",
          color: "var(--text)",
          marginBottom: "1.2rem",
        }}
      >
        {EXPERIENCE_OPTIONS.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>

      <label
        htmlFor="interests"
        style={{
          display: "block",
          marginBottom: "0.4rem",
          fontSize: "0.9rem",
          color: "var(--text-muted)",
        }}
      >
        Interests (optional)
      </label>
      <input
        id="interests"
        type="text"
        value={interests}
        onChange={(e) => setInterests(e.target.value)}
        placeholder="e.g. backend, testing, docs"
        style={{
          width: "100%",
          padding: "0.6rem 0.8rem",
          borderRadius: "var(--radius)",
          border: "1px solid var(--border)",
          background: "var(--surface)",
          color: "var(--text)",
          marginBottom: "1.5rem",
        }}
      />

      <button
        type="submit"
        disabled={isSubmitting}
        style={{
          width: "100%",
          padding: "0.7rem",
          borderRadius: "var(--radius)",
          border: "none",
          background: isSubmitting ? "var(--border)" : "var(--accent)",
          color: isSubmitting ? "var(--text-muted)" : "white",
          fontSize: "0.95rem",
          cursor: isSubmitting ? "not-allowed" : "pointer",
        }}
      >
        {isSubmitting ? "Analyzing repository..." : "Find my first issue"}
      </button>
    </form>
  );
}

export default IntakeForm;
