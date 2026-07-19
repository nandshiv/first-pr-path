import networkx as nx
from sqlalchemy.orm import Session
from models import Commit , FileCentrality
import uuid

def build_coupling_graph(db: Session, repo_id: str):
    commits = (
        db.query(Commit)
        .filter(Commit.repo_id == repo_id, Commit.files_changed.isnot(None))
        .all()
    )

    G = nx.Graph()

    for commit in commits:
        files = commit.files_changed
        if not files or len(files) < 2:
            continue

        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                file_a, file_b = files[i], files[j]
                if G.has_edge(file_a, file_b):
                    G[file_a][file_b]["weight"] += 1
                else:
                    G.add_edge(file_a, file_b, weight=1)

    return G

def compute_centrality(G: nx.Graph):
    if G.number_of_nodes() == 0:
        return {}
    return nx.degree_centrality(G)

def save_centrality_scores(db: Session, repo_id: str):
    G = build_coupling_graph(db, repo_id)
    scores = compute_centrality(G)

    db.query(FileCentrality).filter(FileCentrality.repo_id == repo_id).delete()

    for file_path, score in scores.items():
        entry = FileCentrality(
            id=uuid.uuid4(),
            repo_id=repo_id,
            file_path=file_path,
            centrality_score=score
        )
        db.add(entry)

    db.commit()
    return len(scores)