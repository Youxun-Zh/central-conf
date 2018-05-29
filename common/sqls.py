### user part ###
CREATE_USER_SQL = """insert into pro_user (`email`, `nickname`, `password`, `role`) values (%s, %s, %s, %s);"""
GET_USER_INFO_SQL = """select id, nickname, role, password from pro_user where email=%s;"""
SELECT_NICKNAME_SQL = """select nickname from pro_user where id=%s;"""

CREATE_INVITE_USER_SQL = """insert into pro_user (`email`, `active`, `role`, `create_time`, `update_time`) values (%s, %s, %s, %s, %s);"""
GET_NEW_CREATE_USER_SQL = """select id from pro_user order by id desc;"""

GET_USER_DETAIL_SQL = """select email, nickname, create_time, role from pro_user where id=%s;"""


### group part ###
GROUP_CONFIGS_SQL = """select id, project, module, name, value, uid, gid, create_time, update_time from pro_config
where gid=%s and status=1;"""
UPDATE_PASSWORD = """update pro_user set `password`=%s, `nickname`=%s, `active`=1 where id=%s;"""

# for get group's id
GROUP_SQL = """select gid from pro_user_group_ship where uid=%s order by update_time desc;"""
# For get the group's name
GET_GROUP_SQL = """select id, name from pro_group where id=%s order by update_time desc;"""
GET_GROUPS_NAME_SQL = "select id, name from pro_group where id in %s;"

GET_GROUP_DETAIL_SQL = """select name, short_name, note from pro_group where id=%s;"""
GET_GROUPS_DETAIL_SQL = """select id, name, short_name, note, create_time, update_time from pro_group where id in %s;"""

SELECT_USER_GROUP_SQL = """select gid from pro_user_group_ship where uid=%s and status=1 order by update_time desc;"""

CREATE_GROUP_SQL = """insert into pro_group (`name`, `short_name`, `status`, `note`, `uid`, `mid`, `create_time`, `update_time`) 
values (%s, %s, 1, %s, %s, %s, %s, %s);"""
GET_CREATE_GROUP_SQL = """select id from pro_group where mid=%s order by update_time desc;"""
UPDATE_GROUP_SQL = """update pro_group set `name`=%s, `short_name`=%s, `note`=%s, `mid`=%s where id=%s;"""

# ship
CREATE_GROUP_SHIP_SQL = """insert into pro_user_group_ship (`uid`, `gid`, `create_time`, `update_time`, `mid`, `status`) 
values (%s, %s, %s, %s, %s, 1);"""


### project part ###
CREATE_PROJECT_SQL = """insert into pro_project (`name`, `gid`, `status`, `note`, `uid`, `mid`,`secret_key`, `expire_date`) 
values (%s, %s, %s, %s, %s, %s, %s, %s);"""

UPDATE_PROJECT_SQL = """update pro_project set `name`=%s, `gid`=%s, `note`=%s, `mid`=%s where id=%s;"""

GET_PROJECTS_SQL = """select `id`, `name` from pro_project where status !=0 and gid in %s;"""

GET_NEW_PROJECTS_SQL = """select `id`, `name` from pro_project where status !=0 and mid=%s order by update_time desc;"""

GET_PROJECT_DETAIL_SQL = """select `name`, `note`, `gid`, `secret_key`, `expire_date` from pro_project where id=%s;"""
GET_PROJECTS_DETAIL_SQL = """select `id`, `name`, `note`, `gid`, `secret_key`, `expire_date`, `create_time`, `update_time` from pro_project where gid in %s;"""

GET_GROUP_BY_PNAME_SQL = """select `gid` from pro_project where name=%s;"""


### conf part ###
# add status condition status, note, id
GET_CONF_SQL = """select `project`, `module`, `name`, `value`, `gid` from pro_config where id=%s;"""
CREATE_CONF_SQL = """insert into pro_config (`project`, `module`, `name`, `value`, `status`, `uid`, `gid`, `mid`, `create_time`, `update_time`)
values (%s, %s, %s, %s, 1, %s, %s, %s, %s, %s);"""

GET_NEW_CONF_SQL = """select `id` from pro_config where mid=%s order by update_time desc;"""

UPDATE_CONF_SQL = """update pro_config set project=%s, module=%s, name=%s, value=%s, mid=%s where id=%s;"""

# Get the conf's secret_key by project
GET_SECRET_KEY_SQL = """
select `secret_key`, `expire_date` from pro_project where name=%s;
"""


# user-group ship
GET_USER_GROUP_SHIP_SQL="""select a.id, a.email, a.create_time, b.create_time from 
(select uid, create_time from pro_user_group_ship where status=1 and gid= %s) as b 
left join pro_user as a on a.id=b.uid;"""

GET_USERS_SQL="""select id, email, create_time from pro_user where active=1 order by update_time desc;"""

GET_UNACTIVE_USERSG_SQL="""select id, email from pro_user where active=0 order by update_time desc;"""

GET_NEW_INVITE_USER_SQL="""select id from pro_user where active=0 and email=%s order by create_time desc;"""

UPDATE_USER_GROUP_SHIP_SQL = """update pro_user_group_ship set status=%s where gid=%s and uid=%s;"""













