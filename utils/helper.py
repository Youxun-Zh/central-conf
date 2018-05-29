import bcrypt
import binascii
import datetime
import hashlib
import random
import smtplib
import socket
import string
import time
from collections import OrderedDict

import settings
from common import constants, sqls
from libs import mysql_client, objsync

DB = mysql_client.MysqlClient(using=True)

host = socket.gethostbyname(socket.gethostname())
selfAddr = "{}:{}".format(host, settings.RAFT_PORT)
PARTNERS = list(filter(lambda x: x != selfAddr, settings.RAFT_NODES))
kv_storage = objsync.KVStorage(selfAddr, PARTNERS)


def get_groups_by_user(user):
    groups, no = DB.execute(sqls.GROUP_SQL, (user,), flag=True)
    return groups, no


def get_configs_from_group(groups):
    data = []
    for gid in groups:
        g_data, no = DB.executemany(sqls.GROUP_CONFIGS_SQL, (gid,))
        if no:
            data.extend(g_data)
    return data


def get_groups_name(groups):
    data, no = DB.executemany(sqls.GET_GROUPS_NAME_SQL, (groups, ))
    return data, no


def get_projects_by_group(groups):
    data, no = DB.executemany(sqls.GET_PROJECTS_SQL, (groups, ))
    return data, no


def get_group_by_project_name(p_name):
    data, no = DB.execute(sqls.GET_GROUP_BY_PNAME_SQL, (p_name, ))
    g_id = -1 if not data else data[0]
    return g_id, no


def get_project_detail(pid):
    data, no = DB.execute(sqls.GET_PROJECT_DETAIL_SQL, [pid, ])
    detail = {
        "name": "",
        "gid": "",
        "secret_key": "",
        "expire_date": "",
        "note": "",
    }
    if no:
        fields = ("name", "note", "gid", "secret_key", "expire_date")
        detail = dict(zip(fields, data))
    return detail


def get_projects_detail(pids):
    ####
    data, no = DB.executemany(sqls.GET_PROJECTS_DETAIL_SQL, (pids, ))
    # detail = [{
    #     "id": "",
    #     "name": "",
    #     "gid": "",
    #     "secret_key": "",
    #     "expire_date": "",
    #     "note": "",
    #     "create_time": "",
    #     "update_time": ""
    # }]
    # if no:
    #     fields = ("id", "name", "note", "gid", "secret_key", "expire_date", "create_time", "update_time")
    #     detail = [dict(zip(fields, item)) for item in data]
    # return detail, no
    return data, no


def create_project(params, uid):
    project_id = 0
    data, no = DB.execute(sqls.CREATE_PROJECT_SQL, params)
    if no:
        project = params[0]

        secret_key, expire_date = get_secret_key_from_project(project)
        key_expire = "{}::{}".format(secret_key, expire_date.strftime("%Y-%m-%d %H:%M:%s"))

        ldb_secret_key_expire = kv_storage.get(project)
        if ldb_secret_key_expire != key_expire:
            kv_storage.set(project, key_expire)

        data, no = DB.execute(sqls.GET_NEW_PROJECTS_SQL, [uid,])
        if no:
            project_id = data[0]
    return project_id, no


def update_project(params):
    data, no = DB.execute(sqls.UPDATE_PROJECT_SQL, params)

    project = params[0]
    secret_key, expire_date = get_secret_key_from_project(project)
    key_expire = "{}::{}".format(secret_key, expire_date.strftime("%Y-%m-%d %H:%M:%s"))

    ldb_secret_key_expire = kv_storage.get(project)
    if ldb_secret_key_expire != key_expire:
        kv_storage.set(project, key_expire)
    return data, no


def gen_project_secret_key_and_expire_date(length=16):
    elements = random.sample(string.digits+string.ascii_letters, k=length)
    secret_key = "".join(elements)
    now = datetime.datetime.now()
    expire_date = now + datetime.timedelta(days=365)
    return secret_key, expire_date


def create_user(email, nickname, password, role):
    if isinstance(password, str):
        password = password.encode()
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    args = (email, nickname, password, role)
    data, no = DB.execute(sqls.CREATE_USER_SQL, args)
    return data, no


def get_user_detail(uid):
    data, no = DB.execute(sqls.GET_USER_DETAIL_SQL, (uid,))
    return data, no


def get_nickname(uid):
    data, no = DB.execute(sqls.SELECT_NICKNAME_SQL, (uid,))
    nickname = data[0] if no else ""
    return nickname, no


def check_user_password(email, password):
    uid, nickname, role, flag = 0, "", constants.UserRole.MEMBER, False
    data, no = DB.execute(sqls.GET_USER_INFO_SQL, (email,))
    if no:
        uid, nickname, role, hashed = data
        if bcrypt.checkpw(password.encode(), hashed.encode()):
            flag = True
    return uid, nickname, role, flag


def set_user_password(uid, password, nickname):
    flag = False
    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    data, no = DB.execute(sqls.UPDATE_PASSWORD, (password, nickname, uid))
    if no:
        flag = True
    return flag


def create_group(name, shortcut, note, uid):
    gid, flag = 0, False
    now = datetime.datetime.now()
    _, no = DB.execute(sqls.CREATE_GROUP_SQL, (name, shortcut, note, uid, uid, now, now))
    if no:
        data, no = DB.execute(sqls.GET_CREATE_GROUP_SQL, (uid,))
        gid = data[0] if no else -1
        if gid:
            _, no = DB.execute(sqls.CREATE_GROUP_SHIP_SQL, (uid, gid, now, now, uid))
            flag = True
    return gid, flag


def update_group(name, shortcut, note, uid, gid):
    data, no = DB.execute(sqls.UPDATE_GROUP_SQL, (name, shortcut, note, uid, gid))
    return data, no


def get_groups_id_and_name(gids):
    data, no = DB.executemany(sqls.GET_GROUPS_NAME_SQL, (gids,))
    return data
    # for gid in gids:
    #     data, no = DB.executemany(sqls.GET_GROUP_SQL, (gid,))
    #     if no:
    #         g_id_names.append(data)
    # return g_id_names
    # fields = ("id", "name")
    # g_id_names = []
    # for gid in gids:
    #     data, no = DB.executemany(sqls.GET_GROUP_SQL, (gid,))
    #     if no and len(data) == len(fields):
    #         conf = OrderedDict.fromkeys(fields)
    #         for index, key in enumerate(conf.keys()):
    #             conf[key] = data[index]
    #         g_id_names.append(dict(conf))
    # return g_id_names


def get_group_detail(gid):
    fields = ("name", "short_name", "note")
    data, no = DB.execute(sqls.GET_GROUP_DETAIL_SQL, (gid,))
    data = dict(zip(fields, data))
    if not data:
        data = {"name": "", "short_name": "", "note": ""}
    return data


def get_groups_detail(gids):
    data, no = DB.executemany(sqls.GET_GROUPS_DETAIL_SQL, (gids, ))
    # fields = ("gid", "name", "short_name", "note", "create_time", "update_time")
    # details = [dict(zip(fields, item)) for item in data]
    return data, no


def get_secret_key_from_project(pid):
    data, no = DB.execute(sqls.GET_SECRET_KEY_SQL, (pid,))
    return data


def create_conf(project, module, name, value, uid, gid):
    now = datetime.datetime.now()
    params = (project, module, name, value, uid, gid, uid, now, now)
    data, no = DB.execute(sqls.CREATE_CONF_SQL, params)

    flag = False
    if no:
        flag = True
        info = "{}{}{}".format(module, name, project)

        conf_tag = binascii.crc32(info.encode())
        kv_storage.set(str(conf_tag), value)

        secret_key, expire_date = get_secret_key_from_project(project)
        key_expire = "{}::{}".format(secret_key, expire_date.strftime("%Y-%m-%d %H:%M:%s"))

        ldb_secret_key_expire = kv_storage.get(project)
        if ldb_secret_key_expire != key_expire:
            kv_storage.set(project, key_expire)
    return flag


def get_new_conf(uid):
    data, no = DB.execute(sqls.GET_NEW_CONF_SQL, (uid,))
    conf_id = data[0]
    return conf_id


def get_conf_detail(conf_id):
    pass


def update_conf(conf_id, project, module, name, value, uid):
    now = datetime.datetime.now()
    params = (project, module, name, value, uid, conf_id)
    data, no = DB.execute(sqls.UPDATE_CONF_SQL, params)

    flag = False
    if no:
        flag = True
        info = "{}{}{}".format(module, name, project)
        conf_tag = binascii.crc32(info.encode())
        kv_storage.set(str(conf_tag), value)
        # secret_key, expire_date = get_secret_key_from_project(gid)
        # key_expire = "{}::{}".format(secret_key, expire_date.strftime("%Y-%m-%d %H:%M:%s"))
        # kv_storage.set(project, secret_key)
    return flag


def get_conf(conf_id):
    fields = (("project", ""), ("module", ""), ("name", ""), ("value", ""), ("group", ""))
    conf = OrderedDict(fields)
    conf_id = conf_id if conf_id else -1
    data, no = DB.execute(sqls.GET_CONF_SQL, (conf_id,))
    if no and len(data) == len(fields):
        for index, key in enumerate(conf.keys()):
            conf[key] = data[index]
    return conf


def get_conf_from_kv(conf_tag):
    # value = kv_storage.get(str(conf_tag).encode())
    value = kv_storage.get(str(conf_tag))
    return value


def create_invitation_user(email, gid, role):
    active = 0
    now = datetime.datetime.now()
    params = (email, active, role, now, now)
    data, no = DB.execute(sqls.CREATE_INVITE_USER_SQL, params)
    if no:
        data, no = DB.execute(sqls.GET_NEW_CREATE_USER_SQL, ())
        if no:
            uid = data[0]
            DB.execute(sqls.CREATE_GROUP_SHIP_SQL, (uid, gid, now, now, uid))
    return data, no


def send_invite_email(mail_from, mail_to, body, project):
    smtp = smtplib.SMTP(settings.SMTP_CONF.get("HOST"), settings.SMTP_CONF.get("PORT"))
    smtp.sendmail(mail_from, mail_to, body)
    smtp.quit()


def send_invite(email, uid):
    mail_from = settings.MAIL_FROM
    mail_to = [email]
    ts = int(time.time())
    url = "{}/{}/password?timestamp={}".format(settings.PROJECT_HOST, uid, ts)
    body = """请点击如下链接，设置密码，进入中央配置系统。
           链接：{}""".format(url)
    project = "中央配置系统"
    send_invite_email(mail_from, mail_to, body.encode(), project)


def get_new_invitation_user(email):
    data, no = DB.execute(sqls.GET_NEW_INVITE_USER_SQL, (email,))
    uid = -1 if not no else data[0]
    return uid


def get_unactive_users():
    data, no = DB.executemany(sqls.GET_UNACTIVE_USERSG_SQL, ())
    return data, no


def get_uids_by_gid(gid):
    data, no = DB.executemany(sqls.GET_USER_GROUP_SHIP_SQL, (gid,))
    return data, no


def get_users():
    data, no = DB.executemany(sqls.GET_USERS_SQL, ())
    return data, no


def update_user_group_ship(gid, uid, status):
    data, no = DB.executemany(sqls.UPDATE_USER_GROUP_SHIP_SQL, (status, gid, uid))
    return data, no