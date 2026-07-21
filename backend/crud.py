from sqlalchemy.orm import Session
from models import Repo, Commit, PullRequest, Issue
from github_client import fetch_repo_info, parse_owner_repo_from_url, fetch_commits , fetch_commit_detail
from datetime import datetime


def create_repo_from_url(db: Session, url: str):
    owner, repo_name = parse_owner_repo_from_url(url)
    data = fetch_repo_info(owner, repo_name)

    canonical_owner, canonical_name = data["full_name"].split("/")

    existing = db.query(Repo).filter(Repo.github_url == data["html_url"]).first()
    if existing:
        if existing.owner != canonical_owner or existing.name != canonical_name:
            existing.owner = canonical_owner
            existing.name = canonical_name
            db.commit()
        return existing

    new_repo = Repo(
        github_url=data["html_url"],
        owner=canonical_owner,
        name=canonical_name,
        index_status="pending"
    )

    db.add(new_repo)
    db.commit()
    db.refresh(new_repo)
    return new_repo


def save_commits(db: Session, repo: Repo, raw_commits: list):
    existing_shas = {row.sha for row in db.query(Commit.sha).filter(Commit.repo_id == repo.id).all()}

    new_count = 0
    for raw in raw_commits:
        sha = raw["sha"]
        if sha in existing_shas:
            continue

        commit_data = raw["commit"]
        author_date_str = commit_data.get("author", {}).get("date")
        authored_at = datetime.fromisoformat(author_date_str.replace("Z", "+00:00")) if author_date_str else None

        new_commit = Commit(
            sha=sha,
            repo_id=repo.id,
            authored_at=authored_at,
            message=commit_data.get("message"),
            files_changed=None
        )

        db.add(new_commit)
        new_count += 1

    db.commit()
    return new_count

def backfill_commit_files(db: Session , repo: Repo , limit:int = 20):
    commits_missing_files = (
        db.query(Commit)
        .filter(Commit.repo_id == repo.id , Commit.files_changed.is_(None))
        .limit(limit)
        .all()
    )

    updated_count = 0
    for commit in commits_missing_files:
        files = fetch_commit_detail(repo.owner , repo.name , commit.sha)
        commit.files_changed = files
        updated_count += 1
    
    db.commit()
    return updated_count


def save_pull_requests(db: Session, repo: Repo, raw_prs: list):
    existing_numbers = {row.github_pr_number for row in db.query(PullRequest.github_pr_number).filter(PullRequest.repo_id == repo.id).all()}

    new_count = 0
    for raw in raw_prs:
        number = raw["number"]
        if number in existing_numbers:
            continue

        merged_at_str = raw.get("merged_at")
        merged_at = datetime.fromisoformat(merged_at_str.replace("Z", "+00:00")) if merged_at_str else None

        new_pr = PullRequest(
            repo_id=repo.id,
            github_pr_number=number,
            title=raw.get("title"),
            body=raw.get("body"),
            state=raw.get("state"),
            merged_at=merged_at
        )
        db.add(new_pr)
        new_count += 1

    db.commit()
    return new_count




def save_issues(db: Session, repo: Repo, raw_issues: list):
    existing_numbers = {row.github_issue_number for row in db.query(Issue.github_issue_number).filter(Issue.repo_id == repo.id).all()}

    new_count = 0
    for raw in raw_issues:
        number = raw["number"]
        if number in existing_numbers:
            continue

        updated_at_str = raw.get("updated_at")
        updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")) if updated_at_str else None

        new_issue = Issue(
            repo_id=repo.id,
            github_issue_number=number,
            title=raw.get("title"),
            body=raw.get("body"),
            state=raw.get("state"),
            labels=[label["name"] for label in raw.get("labels", [])],
            updated_at=updated_at
        )
        db.add(new_issue)
        new_count += 1

    db.commit()
    return new_count