import sqlalchemy as sa
from .base import Base

__all__ = ['VkUser']


class VkUser(Base):
    __tablename__ = 'VkUser'
    __table_args__ = {'schema': 'vk'}
    
    id = sa.Column(sa.BigInteger(), primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)
    is_group = sa.Column(sa.Boolean(), nullable=False)