import binascii
import datetime
import hashlib
import json
import os
import time
from functools import lru_cache

import settings
from common import constants
from common.response_context import ResponseCode, ResponseMessage
from mako.lookup import TemplateLookup
from mako.template import Template
from strix.http import HTTPRequest, HTTPResponse
from strix.urls import redirect
from utils import helper

mylookup = TemplateLookup(directories=[settings.TEMPLATE_DIR], output_encoding="utf-8",
                          encoding_errors="replace", input_encoding="utf-8")


class BaseHandler(HTTPRequest):
    """
    The base handler.
    """
    def get_current_user(self):
        uid, nickname, role = 0, "", constants.UserRole.MEMBER
        info = self.get_secure_cookie("user", cookie_secret=self.cookie_secret)
        infos = info.split(".")
        if len(infos) > 1:
            uid, nickname, role = infos
        return uid, nickname, role

    def get_groups(self, uid):
        groups, data = helper.get_groups_by_user(uid)
        groups = [-1] if not data else [item[0] for item in groups]
        return groups

    def get_groups_name(self, groups):
        data, no = helper.get_groups_name(groups)
        if no:
            data = dict(data)
        return data


class HomeHandler(BaseHandler):
    """
    When the user has login, show the all configs, otherwise jump to login html.
    """
    def get(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response
        group_ids = self.get_groups(current_uid)
        g_id_names, _ = helper.get_groups_name(group_ids)
        raw_configs = helper.get_configs_from_group(group_ids)

        conf_name = self.get_argument("conf", "")

        configs = []
        for item in raw_configs:
            if not conf_name or conf_name == item[3]:
                item = list(item)
                item[5] = nickname
                item[6] = dict(g_id_names).get(item[6])
                configs.append(item)

        params = {"uid": current_uid,
                  "nickname": nickname,
                  "configs": configs,
                  "conf": conf_name}
        template = mylookup.get_template("home.html")
        response.context = template.render(**params).decode()
        return response


class LogInHandler(BaseHandler):
    """
    Log in.
    """
    def get(self):
        response = HTTPResponse()

        # Check user is or not login.
        current_uid, _, _ = self.get_current_user()
        if current_uid:
            response.redirect("/")
            return response

        flag, = [self.get_argument(arg) for arg in ("flag",)]
        flag = True if flag == "1" else False
        email = self.get_argument("email", "")
        template = mylookup.get_template("login.html")
        response.context = template.render(flag=flag, email=email).decode()
        return response

    def post(self):
        response = HTTPResponse()

        email, password = [self.get_data(arg) for arg in ("email", "password")]
        uid, nickname, role, flag = helper.check_user_password(email, password)
        if not flag:
            template = mylookup.get_template("login.html")
            response.context = template.render(flag=1, email=email).decode()
            return response

        # Set user info to cookie.
        value = "{}.{}.{}".format(uid, nickname, role)
        response.set_secure_cookie("user", value, cookie_secret=self.cookie_secret)
        response.redirect("/")
        return response


class LogOutHandler(BaseHandler):
    """
    Log out.
    """
    def get(self, uid):
        response = HTTPResponse()
        current_uid, _, _ = self.get_current_user()

        if current_uid == uid:
            response.clear_cookie("user")
            response.redirect("/login")
        else:
            response.redirect("/")
        return response


class InviteUserHandler(BaseHandler):
    """
    Invite user to join this system. Create the user when send invitation.
    TODO: invite url need cipher.
    """
    def post(self, gid):
        email = self.get_data("email")
        helper.create_invitation_user(email, gid, constants.UserRole.MANAGER)
        uid = helper.get_new_invitation_user(email)
        if uid:
            flag = helper.send_invite(email, uid)

        response = HTTPResponse()
        response.redirect("/user-group/{}?invite_flag={}".format(gid, True))
        return response 


class UserPasswordHandler(BaseHandler):
    """
    After inviting user, set up the user's password.
    """
    def get(self, uid):
        response = HTTPResponse()
        template = mylookup.get_template("user-password.html")

        params = {
            "l_flag": False,
            "uid": uid,
            "p_flag": False,
            "email": "",
        }

        timestamp = self.get_argument("timestamp", 0)
        now = datetime.datetime.now()
        if not (timestamp and timestamp.isdigit()):
            params["l_flag"] = True
            response.context = template.render(**params).decode()
            return response 
        link_time = datetime.datetime.fromtimestamp(float(timestamp))
        if link_time > now or link_time+datetime.timedelta(hours=6) < now:
            params["l_flag"] = True
            response.context = template.render(**params).decode()
            return response 

        unactive_users, _ = helper.get_unactive_users()
        # unactive_user_ids = [item[0] for item in unactive_users]
        unactive_user_ids = dict(unactive_users).keys()
        uid = int(uid)
        if uid not in unactive_user_ids:
            params["l_flag"] = True
            response.context = template.render(**params).decode()
            return response

        email = dict(unactive_users).get(uid, "")
        if not email:
            params["l_flag"] = True
        params["email"] = email
        response.context = template.render(**params).decode()
        return response 

    def post(self, uid):
        response = HTTPResponse()
        template = mylookup.get_template("user-password.html")

        params = {
            "l_flag": False,
            "uid": uid,
            "p_flag": False,
            "email": "",
        }

        unactive_users, _ = helper.get_unactive_users()
        # unactive_user_ids = [item[0] for item in unactive_users]
        unactive_user_ids = dict(unactive_users).keys()

        uid = int(uid)
        email = dict(unactive_users).get(uid, "")
        params["email"] = email

        if uid not in unactive_user_ids:
            params["l_flag"] = True
            response.context = template.render(**params).decode()
            return response

        password, repassword = [self.get_data(field) for field in ("password", "repassword")]
        if password != repassword:
            params["p_flag"] = True
            response.context = template.render(**params).decode()
            return response

        nickname = self.get_data("nickname")
        flag = helper.set_user_password(uid, password, nickname)

        response.redirect("/login?email={}".format(email))
        return response 


class NewProjectHandler(BaseHandler):
    """New a project.
    """
    def get(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "g_flag": False,
                  "p_flag": False,
                  }

        template = mylookup.get_template("project.html")
        response.context = template.render(**params).decode()
        return response 

    def post(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "g_flag": False,
                  "p_flag": False,
                  }

        fields = ("group", "project", "note")
        g_name, p_name, note = [self.get_data(field, "") for field in fields]

        gids = self.get_groups(current_uid)
        if not gids:
            response.redirect("/group")
            return response

        g_id_names, _ = helper.get_groups_name(gids)
        g_name_ids = {name: g_id for g_id, name in g_id_names}
        gid = g_name_ids.get(g_name)
        if not (g_name and gid):
            params["g_flag"] = True
            template = mylookup.get_template("project.html")
            response.context = template.render(**params).decode()
            return response

        projects, no = helper.get_projects_by_group(gids)
        if p_name in list(dict(projects).values()):
            params["p_flag"] = True
            template = mylookup.get_template("project.html")
            response.context = template.render(**params).decode()
            return response

        secret_key, expire_date = helper.gen_project_secret_key_and_expire_date()
        active = 1
        p_params = [p_name, gid, active, note, current_uid, current_uid, secret_key, expire_date]
        p_id, _ = helper.create_project(p_params, current_uid)
        if p_id:
            response.redirect("/projects/{}".format(p_id))
        else:
            params["p_flag"] = True
            template = mylookup.get_template("project.html")
            response.context = template.render(**params).decode()
        return response


class ProjectsHandler(BaseHandler):
    """
    """
    def get(self, project_id):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        # check project_id

        gids = self.get_groups(current_uid)
        g_id_names, _ = helper.get_groups_name(gids)

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "pid": project_id,
                  }

        if project_id:
            p_val = helper.get_project_detail(project_id)

            gid = p_val.get("gid", -1)
            if gid not in gids:
                response.redirect("/group")
                return response

            p_val["g_name"] = dict(g_id_names).get(gid)
            params["g_flag"] = False
            params["p_flag"] = False
            params["up_flag"] = False
            params.update(p_val)
            template = mylookup.get_template("/project-detail.html")
            response.context = template.render(**params).decode()
            return response
        else:
            gids = self.get_groups(current_uid)
            p_details, _ = helper.get_projects_detail(gids)
            p_details = [list(item) for item in p_details]
            for item in p_details:
                item[3] = dict(g_id_names).get(item[3])
            params["projects"] = p_details

            template = mylookup.get_template("/projects.html")
            response.context = template.render(**params).decode()
            return response


    def post(self, project_id):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        # check project_id

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "pid": project_id,
                  "up_flag": False,
                  "g_flag": False,
                  "p_flag": False,
                  "g_name": "",
                  "name": "",
                  "note": "",
                  "secret_key": "",
                  "expire_date": "",
                  }

        fields = ("group", "project", "note", "secret_key", "expire_date")
        g_name, p_name, note, secret_key, expire_date = [self.get_data(field, "") for field in fields]

        params["g_name"] = g_name
        params["name"] = p_name
        params["note"] = note
        params["secret_key"] = secret_key
        params["expire_date"] = expire_date

        gids = self.get_groups(current_uid)
        if not gids:
            response.redirect("/group")
            return response

        g_id_names, _ = helper.get_groups_name(gids)
        g_name_ids = {name: g_id for g_id, name in g_id_names}
        gid = g_name_ids.get(g_name)
        if not (g_name and gid):
            params["g_flag"] = True
            template = mylookup.get_template("project-detail.html")
            response.context = template.render(**params).decode()
            return response

        projects, no = helper.get_projects_by_group(gids)
        projects = [item for item in projects if item[0] != int(project_id)]
        if p_name in list(dict(projects).values()):
            params["p_flag"] = True
            template = mylookup.get_template("project-detail.html")
            response.context = template.render(**params).decode()
            return response

        p_params = [p_name, gid, note, current_uid, project_id]
        _, flag = helper.update_project(p_params)
        if flag:
            params["up_flag"] = True
        else:
            params["p_flag"] = True
        template = mylookup.get_template("project-detail.html")
        response.context = template.render(**params).decode()
        return response


class NewConfHandler(BaseHandler):
    """New a config.
    """
    def get(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()

        if not current_uid:
            response.redirect("/login")
            return response

        groups = self.get_groups(current_uid)
        if not groups:
            response.redirect("/group")
            return response

        projects, _ = helper.get_projects_by_group(groups)
        if not projects:
            response.redirect("/project")
            return response

        g_id_names = helper.get_groups_id_and_name(groups)
        params = {"nickname": nickname,
                  "uid": current_uid,
                  "groups": g_id_names,
                  "p_flag": False,
                  "v_flag": False}

        template = mylookup.get_template("conf.html")
        response.context = template.render(**params).decode()
        return response 

    def post(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()

        if not current_uid:
            response.redirect("/login")
            return response

        groups = self.get_groups(current_uid)
        if not groups:
            response.redirect("/group")
            return response

        g_id_names = helper.get_groups_id_and_name(groups)
        params = {"nickname": nickname,
                  "uid": current_uid,
                  "groups": g_id_names,
                  "p_flag": False,
                  "g_flag": False,
                  "v_flag": False}

        fields = ("project", "module", "name", "value")
        project, module, name, value = [self.get_data(arg) for arg in fields]

        projects, _ = helper.get_projects_by_group(groups)
        if project not in dict(projects).values():
            params["p_flag"] = True
            template = mylookup.get_template("conf.html")
            response.context = template.render(**params).decode()
            return response

        try:
            value = json.loads(value)
        except:
            flags = {"v_flag": True}
            params.update(flags)
            template = mylookup.get_template("conf.html")
            response.context = template.render(**params).decode()
            return response

        g_name_ids = {name: g_id for g_id, name in g_id_names}
        g_id, _ = helper.get_group_by_project_name(project)

        if g_id not in groups:
            flags = {"p_flag": True}
            params.update(flags)
            template = mylookup.get_template("conf.html")
            response.context = template.render(**params).decode()
            return response

        value = json.dumps(value)
        flag = helper.create_conf(project, module, name, value, current_uid, g_id)
        if flag:
            conf_id = helper.get_new_conf(current_uid)
            response.redirect("/confs/{}".format(conf_id))
        else:
            flags = {"p_flag": True, "v_flag": True}
            params.update(flags)
            template = mylookup.get_template("conf.html")
            response.context = template.render(**params).decode()
        return response


class ConfsHandler(BaseHandler):
    def get(self, conf_id):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()

        if not current_uid:
            response.redirect("/login")
            return response

        groups = self.get_groups(current_uid)
        if not groups:
            response.redirect("/group")
            return response

        g_id_names = helper.get_groups_id_and_name(groups)
        params = {"nickname": nickname,
                  "uid": current_uid,
                  "p_flag": False,
                  "v_flag": False,
                  "g_flag": False,
                  "up_flag": False,
                  # "group": "",
                  "conf_id": conf_id}

        conf_val = helper.get_conf(conf_id)
        params.update(conf_val)
        # params["group"] = dict(g_id_names).get(conf_val.get("group", 0), "")

        if params.get("value"):
            params["value"] = json.loads(params["value"])

        template = mylookup.get_template("conf-detail.html")
        response.context = template.render(**params).decode()
        return response 

    def post(self, conf_id):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()

        if not current_uid:
            response.redirect("/login")
            return response
        groups = self.get_groups(current_uid)
        if not groups:
            response.redirect("/group")
            return response

        g_id_names = helper.get_groups_id_and_name(groups)
        params = {"nickname": nickname,
                  "uid": current_uid,
                  "conf_id": conf_id,
                  "projcet": " ",
                  "module": " ",
                  "name": " ",
                  "value": " ",
                  "up_flag": False,
                  "g_flag": False,
                  "v_flag": False,
                  "p_flag": False}

        fields = ("project", "module", "name", "value")
        project, module, name, value = [self.get_data(arg) for arg in fields]
        try:
            value = value.replace("'", '"')
            avalue = json.loads(value)
            params["project"] = project
            params["module"] = module
            params["name"] = name
            params["value"] = avalue
        except:
            params["v_flag"] = True
            template = mylookup.get_template("conf-detail.html")
            response.context = template.render(**params).decode()
            return response

        flag = helper.update_conf(conf_id, project, module, name, value, current_uid)
        if not flag:
            params["g_flag"] = True
        else:
            params["up_flag"] = True
        template = mylookup.get_template("conf-detail.html")
        response.context = template.render(**params).decode()
        return response


class UserHandler(BaseHandler):
    """
    Show and setup the user.
    """
    def get(self, uid):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()

        if current_uid != uid:
            response.redirect("/")
            return response

        gids = self.get_groups(current_uid)
        g_id_names = self.get_groups_name(gids)

        user_info, _ = helper.get_user_detail(uid)
        groups = dict(g_id_names).values()
        groups = "; ".join(groups)

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "groups": groups,
                  }
        fields = ("email", "nickname", "create_time")
        params["email"] = user_info[0]
        params["nickname"] = user_info[1]
        params["create_time"] = user_info[2]

        template = mylookup.get_template("/user-detail.html")
        response.context = template.render(**params).decode()
        return response

class NewGroupHandler(BaseHandler):
    """
    Show the all groups.
    """
    def get(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "g_flag": False,
                  }

        template = mylookup.get_template("/group.html")
        response.context = template.render(**params).decode()
        return response

    def post(self):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        fields = ("group", "group-shortcut", "note")
        name, shortcut, note = [self.get_data(field) for field in fields]

        gids = self.get_groups(current_uid)
        g_id_names = self.get_groups_name(gids)
        g_names = dict(g_id_names).values()
        if name in g_names:
            params["g_flag"] = True
            template = mylookup.get_template("/group.html")
            response.context = template.render(**params).decode()
            return response

        g_params = [name, shortcut, note, current_uid]
        gid, flag = helper.create_group(*g_params)

        response.redirect("/groups/{}".format(gid))
        return response


class GroupsHandler(BaseHandler):
    """
    Setup and show the each group.
    """
    def get(self, gid):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "gid": gid,
                  }

        if gid:
            g_val = helper.get_group_detail(gid)
            params["g_flag"] = False
            params["up_flag"] = False
            params.update(g_val)
            template = mylookup.get_template("/group-detail.html")
            response.context = template.render(**params).decode()
            return response
        else:
            gids = self.get_groups(current_uid)
            g_details, _ = helper.get_groups_detail(gids)
            params["g_details"] = g_details

            template = mylookup.get_template("/groups.html")
            response.context = template.render(**params).decode()
            return response

    def post(self, gid):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        gids = self.get_groups(current_uid)
        if not gid or int(gid) not in gids:
            response.redirect("/groups/")
            return response

        fields = ("group", "group-shortcut", "note")
        name, shortcut, note = [self.get_data(field) for field in fields]

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "g_flag": False,
                  "up_flag": False,
                  "gid": gid
                  }

        gids.remove(int(gid))
        g_id_names = self.get_groups_name(gids)
        g_names = dict(g_id_names).values()
        if name in g_names:
            params["g_flag"] = True
            template = mylookup.get_template("/group-detail.html")
            response.context = template.render(**params).decode()
            return response

        g_params = [name, shortcut, note, current_uid, gid]
        _, flag = helper.update_group(*g_params)

        g_val = helper.get_group_detail(gid)
        params["up_flag"] = True
        params.update(g_val)
        template = mylookup.get_template("/group-detail.html")
        response.context = template.render(**params).decode()
        return response


class UserToGroupHandler(BaseHandler):
    """Show the all users in this group.
    """
    def get(self, gid):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        gids = self.get_groups(current_uid)
        if not gid or int(gid) not in gids:
            response.redirect("/groups/")
            return response

        g_users, _ = helper.get_uids_by_gid(gid)
        all_users, _ = helper.get_users()
        add_user_url = "/groups/{gid}/add-user/{uid}"
        remove_user_url = "/groups/{gid}/remove-user/{uid}"

        g_uids = []

        group_users = []
        for g_u in g_users:
            tmp = list(g_u)
            g_uids.append(tmp[0])
            url = remove_user_url.format(gid=gid, uid=tmp[0])
            tmp.append(url)
            group_users.append(tmp)

        no_group_users = []
        for n_g_u in all_users:
            tmp = list(n_g_u)
            if tmp[0] not in g_uids:
                url = add_user_url.format(gid=gid, uid=tmp[0])
                tmp.append("")
                tmp.append(url)
                no_group_users.append(tmp)

        params = {"nickname": nickname,
                  "uid": current_uid,
                  "gid": gid,
                  "group_users": group_users,
                  "no_group_users": no_group_users,
                  "invite_flag": False,
                  }

        invite_flag = self.get_argument("invite_flag", False)
        template = mylookup.get_template("/user-group.html")
        response.context = template.render(**params).decode()
        return response


class UserAddToGroupHandler(BaseHandler):
    def get(self, gid, uid):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        helper.update_user_group_ship(gid, uid, status=1)
        response.redirect("/user-group/{}".format(gid))
        return response


class UserRemoveFromGroupHandler(BaseHandler):
    def get(self, gid, uid):
        response = HTTPResponse()
        current_uid, nickname, role = self.get_current_user()
        if not current_uid:
            response.redirect("/login")
            return response

        helper.update_user_group_ship(gid, uid, status=0)
        response.redirect("/user-group/{}".format(gid))
        return response


class ConfPullHandler(BaseHandler):

    @lru_cache(maxsize=1024)
    def get(self):
        context = {
            "code": ResponseCode.SUCCESS,
            "msg": ResponseMessage.SUCCESS
        }
        response = HTTPResponse()
        response.set_header("Content-Type", "application/json")

        params = ("project", "module", "name", "timestamp", "sign", "user")
        project, module, name, ts, sign, user = [self.get_argument(arg, "") for arg in params]

        if not ts:
            context["code"] = ResponseCode.PARAMETERS_ERROR
            context["msg"] = ResponseMessage.PARAMETERS_ERROR
            response.context = json.dumps(context)
            return response

        if float(ts) > time.time():
            context["code"] = ResponseCode.EXPIRES_ERROR
            context["msg"] = ResponseMessage.EXPIRES_ERROR
            response.context = json.dumps(context)
            return response

        info = "{}{}{}".format(module, name, project)
        conf_tag = binascii.crc32(info.encode())
        conf = helper.get_conf_from_kv(conf_tag)
        if not conf:
            context["code"] = ResponseCode.CONF_NOT_EXISTS_ERROR
            context["msg"] = ResponseMessage.CONF_NOT_EXISTS_ERROR
            response.context = json.dumps(context)
            return response

        # value, secret_key = conf.split("::")
        project_key_expire = helper.get_conf_from_kv(project)
        secret_key, expire_date = project_key_expire.split("::")
        raw_sign_info = "{}{}{}{}".format(info, ts, user, secret_key)
        raw_sign = hashlib.md5(raw_sign_info.encode()).hexdigest()

        # if raw_sign != sign:
        #     context["code"] = ResponseCode.SIGN_ERROR
        #     context["msg"] = ResponseMessage.SIGN_ERROR
        #     response.context = json.dumps(context)
        #     return response

        context["data"] = {
            name: conf,
        }
        response.context = json.dumps(context)
        return response