# [[file:../../../org/youtube.org::*Video][Video:1]]
import sqlalchemy as sa
from sqrt_data.models import Base

__all__ = ['Video']


class Video(Base):
    __table_args__ = {'schema': 'youtube'}
    __tablename__ = 'video'

    id = sa.Column(
        sa.String(256),
        primary_key=True,
    )
    channel_id = sa.Column(
        sa.String(256), sa.ForeignKey('youtube.channel.id'), nullable=False
    )
    category_id = sa.Column(
        sa.Integer(), sa.ForeignKey('youtube.category.id'), nullable=False
    )
    name = sa.Column(sa.Text(), nullable=False)
    url = sa.Column(sa.Text(), nullable=False)
    language = sa.Column(sa.String(256), nullable=False)
    duration = sa.Column(sa.Integer(), nullable=False)
    created = sa.Column(sa.Date(), nullable=False)
# Video:1 ends here
