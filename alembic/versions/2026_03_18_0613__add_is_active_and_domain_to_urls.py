"""add_is_active_and_domain_to_urls

Revision ID: 5f5a907a7d41
Revises: 121776f7731a
Create Date: 2026-03-18 06:13:34.082918

"""
from typing import Sequence, Union
from urllib.parse import urlsplit

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f5a907a7d41'
down_revision: Union[str, Sequence[str], None] = '121776f7731a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def extract_domain(url: str) -> str | None:
    if not url:
        return None
    return urlsplit(url).hostname


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("urls", sa.Column("domain", sa.String(length=255), nullable=True))
    op.add_column(
        "urls",
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=True,
            server_default=sa.true(),
        ),
    )

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT code, url FROM urls")).mappings().all()

    for row in rows:
        domain = extract_domain(row["url"])
        if domain is None:
            raise ValueError(
                f"Could not extract domain for url code={row['code']} url={row['url']}"
            )
        connection.execute(
            sa.text(
                """
                UPDATE urls
                SET domain = :domain, is_active = true
                WHERE code = :code
                """
            ),
            {"code": row["code"], "domain": domain},
        )

    op.alter_column("urls", "domain", nullable=False)
    op.alter_column("urls", "is_active", nullable=False, server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("urls", "is_active")
    op.drop_column("urls", "domain")
