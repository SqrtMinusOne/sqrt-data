# [[file:../../../org/mpd.org::*Models][Models:2]]
import sqlalchemy as sa
from sqrt_data_service.models import Base

__all__ = ['SongListened']

class SongListened(Base):
    __tablename__ = 'SongListened'
    __table_args__ = {'schema': 'mpd'}

    song_id = sa.Column(
        sa.BigInteger(),
        sa.ForeignKey('mpd.MpdSong.id'),
        primary_key=True,
        nullable=False
    )

    time = sa.Column(
        sa.DateTime(),
        nullable=False,
        primary_key=True
    )
# Models:2 ends here
