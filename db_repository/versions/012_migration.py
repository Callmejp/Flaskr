from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
AttendGame = Table('AttendGame', post_meta,
    Column('user_id', Integer),
    Column('game_id', Integer),
    Column('code_content', String(length=1000)),
)

game = Table('game', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('problem_title', String(length=140)),
    Column('problem_description', String(length=1400)),
    Column('sample_input', String(length=100)),
    Column('sample_output', String(length=100)),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
    Column('attend_person', Integer),
    Column('max_person', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['AttendGame'].create()
    post_meta.tables['game'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['AttendGame'].drop()
    post_meta.tables['game'].drop()
