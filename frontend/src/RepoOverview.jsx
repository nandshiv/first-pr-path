import { useState } from "react";

function buildFileTree(files) {
  const root = { name: "root", isDirectory: true, children: {} };

  files.forEach((file) => {
    const parts = file.file_path.split("/");
    let current = root;

    parts.forEach((part, index) => {
      const isLast = index === parts.length - 1;
      if (!current.children[part]) {
        current.children[part] = {
          name: part,
          path: parts.slice(0, index + 1).join("/"),
          isDirectory: !isLast,
          children: isLast ? null : {},
          centrality_score: isLast ? file.centrality_score : null,
        };
      }
      current = current.children[part];
    });
  });

  function convertToArray(node) {
    if (!node.isDirectory) return node;
    const childrenArray = Object.values(node.children).map(convertToArray);
    childrenArray.sort((a, b) => {
      if (a.isDirectory && !b.isDirectory) return -1;
      if (!a.isDirectory && b.isDirectory) return 1;
      return a.name.localeCompare(b.name);
    });
    node.children = childrenArray;
    return node;
  }

  return convertToArray(root).children;
}

function TreeNode({ node, level = 0 }) {
  const [collapsed, setCollapsed] = useState(level > 0);

  const hasChildren = node.isDirectory && node.children && node.children.length > 0;
  const paddingLeft = `${level * 16}px`;

  const handleToggle = () => {
    if (node.isDirectory) {
      setCollapsed(!collapsed);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column" }}>
      <div
        onClick={handleToggle}
        style={{
          display: "flex",
          alignItems: "center",
          padding: "0.25rem 0.4rem",
          cursor: node.isDirectory ? "pointer" : "default",
          fontSize: "0.85rem",
          paddingLeft,
          userSelect: "none",
          borderRadius: "var(--radius)",
        }}
      >
        {node.isDirectory ? (
          <span style={{ marginRight: "0.4rem", fontSize: "0.7rem", color: "var(--text-muted)", width: "12px", display: "inline-block", textAlign: "center" }}>
            {collapsed ? "▶" : "▼"}
          </span>
        ) : (
          <span style={{ marginRight: "0.4rem", width: "12px", display: "inline-block" }} />
        )}
        
        <span className={node.isDirectory ? "" : "mono"} style={{ color: node.isDirectory ? "var(--text)" : "var(--text-muted)", fontWeight: node.isDirectory ? "500" : "normal" }}>
          {node.name}
        </span>

        {!node.isDirectory && node.centrality_score !== null && node.centrality_score > 0 && (
          <span
            style={{
              marginLeft: "0.5rem",
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: "var(--accent)",
              display: "inline-block",
            }}
            title={`Centrality Score: ${node.centrality_score.toFixed(3)}`}
          />
        )}
      </div>

      {hasChildren && !collapsed && (
        <div style={{ display: "flex", flexDirection: "column" }}>
          {node.children.map((child) => (
            <TreeNode key={child.path} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

function RepoOverview({ details, files }) {
  if (!details) return null;

  const fileTree = files && files.length > 0 ? buildFileTree(files) : [];

  return (
    <div
      style={{
        maxWidth: "640px",
        margin: "0 auto 2rem",
        padding: "1.5rem",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)",
        background: "var(--surface)",
      }}
    >
      <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.25rem", fontWeight: 600 }}>
        {details.name}
      </h2>
      
      {details.description && (
        <p style={{ margin: "0 0 1rem 0", fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.4 }}>
          {details.description}
        </p>
      )}

      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", fontSize: "0.85rem", marginBottom: "1.2rem" }}>
        {details.language && (
          <div>
            <span style={{ color: "var(--text-muted)" }}>Language:</span>{" "}
            <strong>{details.language}</strong>
          </div>
        )}
        <div>
          <span style={{ color: "var(--text-muted)" }}>GitHub:</span>{" "}
          <a
            href={details.github_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "var(--accent)", textDecoration: "none" }}
          >
            {details.owner}/{details.name}
          </a>
        </div>
      </div>

      {fileTree.length > 0 && (
        <div style={{ borderTop: "1px solid var(--border)", paddingTop: "1rem" }}>
          <h4 style={{ margin: "0 0 0.8rem 0", fontSize: "0.8rem", textTransform: "uppercase", letterSpacing: "0.05em", color: "var(--text-muted)" }}>
            Codebase Directory Tree
          </h4>
          <div style={{ display: "flex", flexDirection: "column", maxHeight: "300px", overflowY: "auto", paddingRight: "0.5rem" }}>
            {fileTree.map((child) => (
              <TreeNode key={child.path} node={child} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default RepoOverview;
