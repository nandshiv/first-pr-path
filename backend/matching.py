from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from models import Issue, FileCentrality
from embeddings import get_model
import numpy as np
from datetime import datetime, timezone
from github_client import fetch_issue_state


def score_issues_for_user(db: Session, repo_id: str, skill_profile_text: str, top_n: int = 15):
    model = get_model()
    profile_embedding = model.encode(skill_profile_text)

    rows = db.execute(sql_text("""
        SELECT dc.source_id, dc.chunk_text,
               1 - (dc.embedding <=> :profile_embedding) AS similarity
        FROM document_chunks dc
        WHERE dc.repo_id = :repo_id AND dc.source_type = 'issue_body'
        ORDER BY dc.embedding <=> :profile_embedding
        LIMIT :top_n
    """), {"profile_embedding": str(profile_embedding.tolist()), "repo_id": repo_id, "top_n": top_n}).fetchall()

    scored = []
    for row in rows:
        issue_number = int(row.source_id)
        issue = db.query(Issue).filter(
            Issue.repo_id == repo_id, Issue.github_issue_number == issue_number
        ).first()
        if not issue:
            continue

        matched_files, avg_centrality = _matched_files_for_issue(db, repo_id, issue)
        staleness_days = _staleness_days(issue.updated_at)
        staleness_penalty = min(staleness_days / 365, 1.0)

        fit_score = row.similarity - (0.3 * avg_centrality) - (0.05 * staleness_penalty)

        scored.append({
            "issue": issue,
            "similarity": row.similarity,
            "centrality": avg_centrality,
            "matched_files": matched_files,
            "staleness_days": staleness_days,
            "fit_score": fit_score
        })

    scored.sort(key=lambda x: x["fit_score"], reverse=True)
    return scored


def _avg_centrality_for_issue(db: Session, repo_id: str, issue: Issue):
    all_files = db.query(FileCentrality).filter(FileCentrality.repo_id == repo_id).all()
    if not all_files:
        return 0.0

    issue_text = f"{issue.title or ''} {issue.body or ''}".lower()

    mentioned = []
    for f in all_files:
        full_path = f.file_path.lower()
        basename = full_path.split("/")[-1]
        if full_path in issue_text or basename in issue_text:
            mentioned.append(f)

    if mentioned:
        return sum(f.centrality_score for f in mentioned) / len(mentioned)

    return sum(f.centrality_score for f in all_files) / len(all_files)


def _staleness_days(updated_at):
    if updated_at is None:
        return 9999
    now = datetime.now(timezone.utc)
    if updated_at.tzinfo is None:
        updated_at = updated_at.replace(tzinfo=timezone.utc)
    return (now - updated_at).days

def get_verified_open_issues(db: Session, repo, scored_candidates: list, needed: int = 5):
    verified = []
    for candidate in scored_candidates:
        issue = candidate["issue"]
        current_state = fetch_issue_state(repo.owner, repo.name, issue.github_issue_number)
        if current_state != issue.state:
            issue.state = current_state

        if current_state == "open":
            verified.append(candidate)
        if len(verified) >= needed:
            break

    db.commit()
    return verified

def _matched_files_for_issue(db: Session, repo_id: str, issue: Issue):
    all_files = db.query(FileCentrality).filter(FileCentrality.repo_id == repo_id).all()
    if not all_files:
        return [], 0.0

    issue_text = f"{issue.title or ''} {issue.body or ''}".lower()

    mentioned = []
    for f in all_files:
        full_path = f.file_path.lower()
        basename = full_path.split("/")[-1]
        if full_path in issue_text or basename in issue_text:
            mentioned.append(f)

    if mentioned:
        avg_score = sum(f.centrality_score for f in mentioned) / len(mentioned)
        return [f.file_path for f in mentioned], avg_score

    avg_score = sum(f.centrality_score for f in all_files) / len(all_files)
    return [], avg_score