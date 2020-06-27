import sqlalchemy as sa
from .base import Base

__all__ = ['AlbumSong']

class AlbumSong(Base):
    __tablename__ = 'AlbumSong'
    __table_args__ = {'schema': 'google'}

    id = sa.Column(
        sa.BigInteger(),
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )

    title = sa.Column(sa.String(256), nullable=False)
    album = sa.Column(sa.String(256), nullable=False)
    artist = sa.Column(sa.String(256), nullable=False)
    duration = sa.Column(sa.String(256), nullable=False)
    play_count = sa.Column(sa.String(256), nullable=False)
