# [[file:../../../org/youtube.org::*NewPipe][NewPipe:1]]
import sqlalchemy as sa
from sqrt_data.models import Base

__all__ = ['NewPipeMeta']


class NewPipeMeta(Base):
    __table_args__ = {'schema': 'youtube'}
    __tablename__ = '_newpipe_meta'

    video_id = sa.Column(
        sa.String(256),
        primary_key=True,
    )
    access_date = sa.Column(sa.Date(), nullable=False)
    progress = sa.Column(sa.Float(), nullable=True)
    repeat_count = sa.Column(sa.Integer(), nullable=False)
# NewPipe:1 ends here
