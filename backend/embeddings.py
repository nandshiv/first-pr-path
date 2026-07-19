from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models import DocumentChunk, PullRequest, Issue
from github_client import fetch_pr_comments
import uuid

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_and_store_prs(db: Session, repo_id: str, owner: str, repo_name: str, limit: int = 10):
    model = get_model()

    prs = (
        db.query(PullRequest)
        .filter(PullRequest.repo_id == repo_id, PullRequest.state == "closed")
        .limit(limit)
        .all()
    )

    chunks_created = 0
    for pr in prs:
        already_embedded = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.source_type == "pr_body", DocumentChunk.source_id == str(pr.github_pr_number))
            .first()
        )
        if already_embedded:
            continue

        if pr.body:
            embedding = model.encode(pr.body)
            chunk = DocumentChunk(
                id=uuid.uuid4(),
                repo_id=repo_id,
                source_type="pr_body",
                source_id=str(pr.github_pr_number),
                chunk_text=pr.body,
                embedding=embedding
            )
            db.add(chunk)
            chunks_created += 1

        raw_comments = fetch_pr_comments(owner, repo_name, pr.github_pr_number)
        for comment in raw_comments:
            text = comment.get("body")
            if not text:
                continue
            embedding = model.encode(text)
            chunk = DocumentChunk(
                id=uuid.uuid4(),
                repo_id=repo_id,
                source_type="pr_comment",
                source_id=str(pr.github_pr_number),
                chunk_text=text,
                embedding=embedding
            )
            db.add(chunk)
            chunks_created += 1

    db.commit()
    return chunks_created

def retrieve_relevant_chunks(db:Session , repo_id: str , query_text: str , top_k:int =5):
    model = get_model()
    query_embedding = model.encode(query_text)
    results = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.repo_id == repo_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )
    return results