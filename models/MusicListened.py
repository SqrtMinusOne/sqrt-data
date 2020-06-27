import sqlalchemy as sa
from .base import Base

__all__ = ['MusicListened']

class MusicListened(Base):
    __tablename__ = 'MusicListened'
    __table_args__ = {'schema': 'google'}

    id = sa.Column(
        sa.BigInteger(),
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )

    artist = sa.Column(sa.String(256), nullable=False)
    title = sa.Column(sa.Text(), nullable=False)
    time = sa.Column(sa.DateTime(), nullable=False)

    song_id = sa.Column(sa.BigInteger(), sa.ForeignKey(f'google.AlbumSong.id'), nullable=True)

