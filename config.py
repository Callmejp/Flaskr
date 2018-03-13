import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = 'a random string'

MAIL_SERVER = 'localhost'
MAIL_PORT = 25
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['1321715290@qq.com']
# pagination
POSTS_PER_PAGE = 5

WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

url = 'https://m.runoob.com/api/compile.php'
headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)', 'Host': 'm.runoob.com'}
languageId = {'perl': '14', 'c++': '7', 'python': '15'}

UPLOADED_PHOTOS_DEST = basedir

