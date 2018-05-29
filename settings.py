import os


PROJECT_HOST = "http://central-conf.sce.sohuno.com"

SMTP_CONF = {
    "HOST": "10.16.68.141",
    "PORT": 25,
}
MAIL_FROM = "user18601@sohu.com"

DEBUG = False

PROJECT_DIR = os.path.dirname(__file__)

SECRET_KEY = "177563172dfe935f221e655a3f2887e5"

TEMPLATE_DIR = os.path.join(PROJECT_DIR, "templates")

RAFT_PORT = "4321"
RAFT_NODES = ("127.0.0.1:4321", "127.0.0.1:4321", "127.0.0.1:4321")
LEVELDB_PATH = "/tmp/level"

DATABASES = {
    "default": {
        "DB": "central_conf",
        "USER": "",
        "PASSWD": "",
        "HOST": "",
        "PORT": 3306,
    },
    "default-slave": {
        "DB": "central_conf",
        "USER": "",
        "PASSWD": "",
        "HOST": "",
        "PORT": 3306,
    },
}

ENGINE_URL = "mysql+mysqldb://{p[USER]}:{p[PASSWD]}@{p[HOST]}:{p[PORT]}/{p[DB]}?charset=utf8mb4"

MYSQLPOOL_BACKEND = 'QueuePool'

MYSQLPOOL_ARGUMENTS = {
    'pool_size': 50,
    "pool_recycle": 3600,
    'pool_timeout': 3,
    'max_overflow': 0,
    'encoding': 'utf-8',
    'echo': False,
    # 'use_threadlocal': False,
    # 'reset_on_return': 'rollback',
}

try:
    from local_settings import *
except ImportError:
    pass