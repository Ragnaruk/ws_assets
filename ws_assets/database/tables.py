from datetime import datetime

import sqlalchemy as sa  # type: ignore

metadata = sa.MetaData()


class Tables:
    asset = sa.Table(
        "Asset",
        metadata,
        sa.Column(
            "id",
            sa.INTEGER,
            primary_key=True,
            autoincrement=True,
            comment="Unique asset ID.",
        ),
        sa.Column("symbol", sa.TEXT, nullable=False, comment="Asset name."),
    )

    point = sa.Table(
        "Point",
        metadata,
        sa.Column(
            "id",
            sa.INTEGER,
            primary_key=True,
            autoincrement=True,
            comment="Unique point ID.",
        ),
        sa.Column(
            "asset_id",
            sa.INTEGER,
            sa.ForeignKey("Asset.id", ondelete="CASCADE"),
            nullable=False,
            comment="Asset ID.",
        ),
        sa.Column("value", sa.FLOAT, nullable=False, comment="Asset value."),
        sa.Column(
            "ts",
            sa.TIMESTAMP,
            nullable=False,
            default=datetime.utcnow,
            comment="Point timestamp.",
            index=True,
        ),
    )
