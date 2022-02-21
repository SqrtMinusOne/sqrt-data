# [[file:../../../org/youtube.org::*Watch][Watch:1]]
import sqlalchemy as sa
from sqrt_data.models import Base

__all__ = ['Watch']


class Watch(Base):
    __table_args__ = {'schema': 'youtube'}
    __tablename__ = 'watch'

    video_id = sa.Column(
        sa.String(256),
        sa.ForeignKey('youtube.video.id'),
        primary_key=True,
    )
    date = sa.Column(sa.Date(), nullable=False, primary_key=True)
    kind = sa.Column(sa.String(256), nullable=False, primary_key=True)
    duration = sa.Column(sa.Integer(), nullable=False)
# Watch:1 ends here
