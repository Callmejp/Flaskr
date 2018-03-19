from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
AttendGame = Table('AttendGame', pre_meta,
    Column('user_id', INTEGER),
    Column('game_id', INTEGER),
    Column('code_content', VARCHAR(length=1000)),
)

game = Table('game', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('problem_title', VARCHAR(length=140)),
    Column('problem_description', VARCHAR(length=1400)),
    Column('sample_input', VARCHAR(length=100)),
    Column('sample_output', VARCHAR(length=100)),
    Column('start_time', DATETIME),
    Column('end_time', DATETIME),
    Column('attend_person', INTEGER),
    Column('max_person', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['AttendGame'].drop()
    pre_meta.tables['game'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['AttendGame'].create()
    pre_meta.tables['game'].create()
