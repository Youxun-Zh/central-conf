CREATE TABLE `pro_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `email` varchar(32) NOT NULL DEFAULT '' COMMENT 'E-mail',
  `nickname` varchar(32) NOT NULL DEFAULT '' COMMENT '昵称',
  `password` varchar(64) NOT NULL DEFAULT '' COMMENT '密码',
  `role` varchar(32) NOT NULL DEFAULT '' COMMENT '角色',
  `note` varchar(32) NOT NULL DEFAULT '' COMMENT '备注',
  `active` tinyint(4) unsigned NOT NULL DEFAULT '1' COMMENT '状态',
  `create_time` datetime NOT NULL DEFAULT '2017-07-01 00:00:00' COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8 COMMENT='用户表';

CREATE TABLE `pro_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '组名称',
  `short_name` varchar(32) NOT NULL DEFAULT '' COMMENT '组缩略名称',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '状态',
  `note` varchar(64) NOT NULL DEFAULT '' COMMENT '备注',
  `uid` smallint(6) NOT NULL DEFAULT '0' COMMENT '创建人',
  `mid` smallint(6) NOT NULL DEFAULT '0' COMMENT '修改用户',
  `create_time` datetime NOT NULL DEFAULT '2017-07-01 00:00:00' COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `ix_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8 COMMENT='用户组表';

CREATE TABLE `pro_user_group_ship` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '状态',
  `note` varchar(64) NOT NULL DEFAULT '' COMMENT '备注',
  `uid` smallint(6) NOT NULL DEFAULT '0' COMMENT '所属用户',
  `gid` smallint(6) NOT NULL DEFAULT '0' COMMENT '所属组',
  `mid` smallint(6) NOT NULL DEFAULT '0' COMMENT '修改用户',
  `create_time` datetime NOT NULL DEFAULT '2017-07-01 00:00:00' COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_gid_uid` (`gid`, `uid`),
  KEY `ix_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户与组关系表';

CREATE TABLE `pro_project` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '项目名称',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '0' COMMENT '状态',
  `note` varchar(64) NOT NULL DEFAULT '' COMMENT '备注',
  `secret_key` char(32) NOT NULL DEFAULT '' COMMENT '密钥',
  `expire_date` datetime NOT NULL DEFAULT '2017-07-01 00:00:00' COMMENT '过期时间',
  `gid` smallint(6) NOT NULL DEFAULT '0' COMMENT '所属组',
  `uid` smallint(6) NOT NULL DEFAULT '0' COMMENT '创建用户',
  `mid` smallint(6) NOT NULL DEFAULT '0' COMMENT '修改用户',
  `create_time` datetime NOT NULL DEFAULT '2017-07-01 00:00:00' COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_gid_name` (`gid`, `name`),
  KEY `ix_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10001 DEFAULT CHARSET=utf8 COMMENT='项目表';

CREATE TABLE `pro_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键',
  `project` varchar(32) NOT NULL DEFAULT '' COMMENT '项目名称',
  `project_id` int(11) NOT NULL DEFAULT '0' COMMENT '项目ID',
  `module` varchar(32) NOT NULL DEFAULT '' COMMENT '模块名称',
  `name` varchar(32) NOT NULL DEFAULT '' COMMENT '配置名称',
  `value` varchar(256) NOT NULL DEFAULT '' COMMENT '配置项值',
  `status` tinyint(4) unsigned NOT NULL DEFAULT '1' COMMENT '状态',
  `version` smallint(6) unsigned NOT NULL DEFAULT '1' COMMENT '版本',
  `note` varchar(64) NOT NULL DEFAULT '' COMMENT '备注',
  `uid` smallint(6) NOT NULL DEFAULT '0' COMMENT '创建用户',
  `gid` smallint(6) NOT NULL DEFAULT '0' COMMENT '所属组',
  `mid` smallint(6) NOT NULL DEFAULT '0' COMMENT '修改用户',
  `white_list` varchar(512) NOT NULL DEFAULT '' COMMENT '白名单',
  `create_time` datetime NOT NULL DEFAULT '2017-07-01 00:00:00' COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_project_module_name` (`project`, `module`, `name`),
  KEY `ix_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10001 DEFAULT CHARSET=utf8 COMMENT='配置表';