# [[file:../../../org/mpd.org::*Models][Models:1]]
import sqlalchemy as sa
from sqrt_data_service.models import Base

__all__ = ['MpdSong']

class MpdSong(Base):
    __tablename__ = 'MpdSong'
    __table_args__ = {'schema': 'mpd'}

    id = sa.Column(
        sa.BigInteger(),
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )

    file = sa.Column(
        sa.Text(),
        nullable=False,
        unique=True
    )

    duration = sa.Column(sa.Integer(), nullable=False)
    artist = sa.Column(sa.Text(), nullable=True)
    album_artist = sa.Column(sa.Text(), nullable=False)
    album = sa.Column(sa.Text(), nullable=False)
    title = sa.Column(sa.Text(), nullable=False)
    year = sa.Column(sa.Integer(), nullable=True)
    musicbrainz_trackid = sa.Column(sa.String(256), nullable=True)
# Models:1 ends here
