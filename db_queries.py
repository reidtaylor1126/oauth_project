create_site_users = (
    "CREATE TABLE `site_users` ("
    "  `user_id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `email` varchar(24) NOT NULL,"
    "  `fullname` varchar(32) NOT NULL,"
    "  `passhash` varbinary(128) NOT NULL,"
    "  `salt` varbinary(128) NOT NULL,"
    "  `token` varbinary(32), "
    "  `expires` datetime, "
    "  `github_token` varchar(64), "
    "  `google_token` varchar(64), "
    "  PRIMARY KEY (`user_id`)"
    ") ENGINE=InnoDB ;"
)

add_user = ("INSERT INTO `site_users` "
            "(email, fullname, passhash, salt)"
            "VALUES (%s, %s, %s, %s);"
            )

add_from_github = ("INSERT INTO `site_users` "
            "(email, fullname, passhash, salt, github_token)"
            "VALUES (%s, %s, %s, %s, %s);"
            )

q_get_user_by_email = "SELECT * FROM `site_users` WHERE email = (%s);"

q_get_user_by_id = "SELECT * FROM `site_users` WHERE user_id = (%s);"

q_get_user_by_token = ("SELECT * FROM `site_users` "
                       "WHERE token = (%s) AND "
                       "expires > NOW();")

q_get_user_by_github = "SELECT * FROM `site_users` WHERE github_token = (%s)"

q_put_token = ("UPDATE `site_users` "
            "SET token = (%s), expires = (%s)"
            "WHERE user_id = (%s);")

q_del_token = ("UPDATE `site_users` "
               "SET token = NULL, expires = NULL "
               "WHERE token = (%s);")

q_update_password = ("UPDATE `site_users` "
                     "SET passhash = (%s) "
                     "WHERE user_id = (%s) AND passhash = (%s);")