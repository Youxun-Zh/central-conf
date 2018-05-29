import handlers


urls = ((r"^/$", handlers.HomeHandler),

        (r"^/login$", handlers.LogInHandler),
        (r"^/(?P<uid>\d+)/logout$", handlers.LogOutHandler),

        (r"^/(?P<gid>\d+)/invitation$", handlers.InviteUserHandler),
        (r"^/(?P<uid>\d+)/password$", handlers.UserPasswordHandler),

        (r"^/project$", handlers.NewProjectHandler),
        (r"^/projects/(?P<project_id>\d+)?$", handlers.ProjectsHandler),

        (r"^/conf$", handlers.NewConfHandler),
        (r"^/confs/(?P<conf_id>\d+)$", handlers.ConfsHandler),

        # (r"^/users$", handlers.UsersHandler),
        (r"^/users/(?P<uid>\d+)$", handlers.UserHandler),

        (r"^/group$", handlers.NewGroupHandler),
        (r"^/groups/(?P<gid>\d+)?$", handlers.GroupsHandler),

        (r"^/user-group/(?P<gid>\d+)$", handlers.UserToGroupHandler),

        (r"^/groups/(?P<gid>\d+)/add-user/(?P<uid>\d+)$", handlers.UserAddToGroupHandler),
        (r"^/groups/(?P<gid>\d+)/remove-user/(?P<uid>\d+)$", handlers.UserRemoveFromGroupHandler),

        (r"^/conf-pull$", handlers.ConfPullHandler),
       )