"""Create MEMORA initial schema."""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("memories", sa.Column("id", sa.String(36), primary_key=True), sa.Column("title", sa.String(240), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("source", sa.String(80), nullable=False), sa.Column("source_ref", sa.String(500), nullable=True), sa.Column("importance", sa.Integer(), nullable=False), sa.Column("tags", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_memories_title", "memories", ["title"])
    op.create_table("skills", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(160), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("instructions", sa.Text(), nullable=False), sa.Column("version", sa.String(40), nullable=False), sa.Column("tags", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_skills_name", "skills", ["name"])

def downgrade():
    op.drop_index("ix_skills_name", table_name="skills")
    op.drop_table("skills")
    op.drop_index("ix_memories_title", table_name="memories")
    op.drop_table("memories")
