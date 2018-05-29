import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
PARDIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARDIR)

import binascii
import subprocess

import leveldb
from libs import mysql_client
# from libs.objsync import ldb
from utils import helper

DB = mysql_client.MysqlClient(using=True)


SELECT_CONF_SQL = """
select module, name, project, value from pro_config where id < %s and status=1 order by id desc;
"""

SELECT_ID_FROM_CONF_SQL = """
select id from pro_config order by id desc limit 1;
"""

SELECT_SECRET_SQL = """
select name, secret_key, expire_date from pro_project where id < %s order by id desc;
"""

SELECT_ID_FROM_PROJECT_SQL = """
select id from pro_project order by id desc limit 1;
"""


def get_all_project_secret():
    data, no = DB.execute(SELECT_ID_FROM_PROJECT_SQL, ())
 
    max_id = data[0]
    interval = 200
    raw_secrets = []
    secrets = []

    for i in range(1, max_id, interval):
        datas, no = DB.executemany(SELECT_SECRET_SQL, (i+interval,))
        raw_secrets.extend(datas)

    for item in raw_secrets:
        project, secret_key, expire_date = item
        key_expire = "{}::{}".format(secret_key, expire_date.strftime("%Y-%m-%d %H:%M    :%s"))
        secrets.append((project, key_expire))

    return secrets


def get_all_available_conf():
    data, no = DB.execute(SELECT_ID_FROM_CONF_SQL, ())
 
    max_id = data[0]
    interval = 200
    raw_confs = []
    confs = []

    for i in range(1, max_id, interval):
        datas, no = DB.executemany(SELECT_CONF_SQL, (i+interval,))
        raw_confs.extend(datas)

    for item in raw_confs:
        module, name, project, conf = item
        info = "{}{}{}".format(module, name, project)
        conf_tag = binascii.crc32(info.encode())
        confs.append((str(conf_tag), conf))
    return confs


def recover_leveldb_data():
    ldb = leveldb.LevelDB("/tmp/test")
    batch = leveldb.WriteBatch()

    count = 1
    confs = get_all_available_conf()
    secrets = get_all_project_secret()

    items = confs + secrets
    for item in items:
        k, v = item
        batch.Put(k.encode(), v.encode())
        if count % 100 == 0:
            ldb.Write(batch)
    else:
        ldb.Write(batch)

    del(ldb)
    print("Recover leveldb success.")


def start_app():
    # import ipdb; ipdb.set_trace()
    # cmd = "python3 /opt/src/app/runserver.py --port=8080"
    server_locate = os.path.join(PARDIR, "runserver.py")
    cmd = "python3 {} --port=8080".format(server_locate)
    subprocess.run(cmd, shell=True)


def main():
    recover_leveldb_data()
    # app run 
    start_app()


if __name__ == "__main__":
    main()
