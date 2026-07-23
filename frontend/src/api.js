const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export async function createRepo(url) {
  const response = await fetch(`${API_BASE}/repos`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!response.ok) {
    throw new Error("Failed to index repo");
  }
  return response.json();
}

export async function getRecommendations(repoId, skillProfileText) {
  const url = `${API_BASE}/repos/${repoId}/recommendations?skill_profile=${encodeURIComponent(skillProfileText)}`;
  const response = await fetch(url, { method: "POST" });
  if (!response.ok) {
    throw new Error("Failed to get recommendations");
  }
  return response.json();
}

export async function explainFile(repoId, filePath) {
  const url = `${API_BASE}/repos/${repoId}/explain?file_path=${encodeURIComponent(filePath)}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch explanation");
  }
  return response.json();
}

export async function getRepoDetails(repoId) {
  const url = `${API_BASE}/repos/${repoId}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch repo details");
  }
  return response.json();
}

export async function getCentrality(repoId) {
  const url = `${API_BASE}/repos/${repoId}/centrality`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch file centrality");
  }
  return response.json();
}

export async function getRepoFiles(repoId) {
  const url = `${API_BASE}/repos/${repoId}/files`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error("Failed to fetch repo file tree");
  }
  return response.json();
}
