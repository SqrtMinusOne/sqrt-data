import sqlalchemy as sa
from .base import Base

__all__ = ['VkMessage']


class VkMessage(Base):
    __tablename__ = 'VkMessage'
    __table_args__ = {'schema': 'vk'}
    
    id = sa.Column(
        sa.BigInteger(),
        primary_key=True,
        nullable=False,
        unique=True,
        autoincrement=True,
    )
    target_id = sa.Column(sa.BigInteger(), sa.ForeignKey('vk.VkUser.id'), nullable=False)
    sender = sa.Column(sa.String(256), nullable=False, index=True)
    recepient = sa.Column(sa.String(256), nullable=False, index=True)
    message = sa.Column(sa.Text(), nullable=False)
    date = sa.Column(sa.DateTime(), nullable=False, index=True)
    is_edited = sa.Column(sa.Boolean(), nullable=False)