from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
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

game = Table('game', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('problem_title', String(length=140)),
    Column('problem_description', String(length=1400)),
    Column('timestamp', DateTime),
    Column('start_time', DateTime),
    Column('long_time', Integer),
    Column('attend_person', Integer),
    Column('max_person', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['game'].columns['end_time'].drop()
    pre_meta.tables['game'].columns['sample_input'].drop()
    pre_meta.tables['game'].columns['sample_output'].drop()
    post_meta.tables['game'].columns['long_time'].create()
    post_meta.tables['game'].columns['timestamp'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['game'].columns['end_time'].create()
    pre_meta.tables['game'].columns['sample_input'].create()
    pre_meta.tables['game'].columns['sample_output'].create()
    post_meta.tables['game'].columns['long_time'].drop()
    post_meta.tables['game'].columns['timestamp'].drop()
