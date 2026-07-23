"""initial_schema

Revision ID: 11d664f58ec8
Revises:
Create Date: 2026-07-23 22:49:03.553163

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


# revision identifiers, used by Alembic.
revision: str = "11d664f58ec8"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "repos",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("github_url", sa.String(), nullable=False),
        sa.Column("owner", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("last_synced_sha", sa.String(), nullable=True),
        sa.Column("index_status", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_url"),
    )

    op.create_table(
        "commits",
        sa.Column("sha", sa.String(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("authored_at", sa.DateTime(), nullable=True),
        sa.Column("message", sa.String(), nullable=True),
        sa.Column("files_changed", sa.ARRAY(sa.String()), nullable=True),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("sha"),
    )

    op.create_index(
        "ix_commits_repo_id",
        "commits",
        ["repo_id"],
    )

    op.create_table(
        "document_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_id", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=True),
        sa.Column("chunk_text", sa.String(), nullable=False),
        sa.Column("embedding", Vector(384), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_document_chunks_repo_id",
        "document_chunks",
        ["repo_id"],
    )

    op.create_table(
        "file_centrality",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.Column("centrality_score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_file_centrality_repo_id",
        "file_centrality",
        ["repo_id"],
    )

    op.create_table(
        "file_couplings",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("file_a", sa.String(), nullable=False),
        sa.Column("file_b", sa.String(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_file_couplings_repo_id",
        "file_couplings",
        ["repo_id"],
    )

    op.create_table(
        "issues",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("github_issue_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("labels", sa.ARRAY(sa.String()), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_issues_repo_id",
        "issues",
        ["repo_id"],
    )

    op.create_table(
        "pull_requests",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("github_pr_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("body", sa.String(), nullable=True),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("merged_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_pull_requests_repo_id",
        "pull_requests",
        ["repo_id"],
    )

    op.create_table(
        "repo_files",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("repo_id", sa.UUID(), nullable=False),
        sa.Column("file_path", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["repo_id"], ["repos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_repo_files_repo_id",
        "repo_files",
        ["repo_id"],
    )

    op.create_table(
        "resolution_reports",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("issue_id", sa.UUID(), nullable=False),
        sa.Column("pr_url", sa.String(), nullable=True),
        sa.Column("reported_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_resolution_reports_issue_id",
        "resolution_reports",
        ["issue_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_resolution_reports_issue_id", table_name="resolution_reports")
    op.drop_table("resolution_reports")

    op.drop_index("ix_repo_files_repo_id", table_name="repo_files")
    op.drop_table("repo_files")

    op.drop_index("ix_pull_requests_repo_id", table_name="pull_requests")
    op.drop_table("pull_requests")

    op.drop_index("ix_issues_repo_id", table_name="issues")
    op.drop_table("issues")

    op.drop_index("ix_file_couplings_repo_id", table_name="file_couplings")
    op.drop_table("file_couplings")

    op.drop_index("ix_file_centrality_repo_id", table_name="file_centrality")
    op.drop_table("file_centrality")

    op.drop_index("ix_document_chunks_repo_id", table_name="document_chunks")
    op.drop_table("document_chunks")

    op.drop_index("ix_commits_repo_id", table_name="commits")
    op.drop_table("commits")

    op.drop_table("repos")