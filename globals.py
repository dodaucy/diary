######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


from databases import Database

import config
from rate_limit import RateLimitHandler
from settings import Settings


db = Database(config.DATABASE)

settings = Settings(db)

rate_limit_handler = RateLimitHandler(db, config.rate_limit.RATE_LIMIT_ALLOW_REQUESTS, config.rate_limit.RATE_LIMIT_TIME_WINDOW)
login_rate_limit_handler = RateLimitHandler(db, config.rate_limit.LOGIN_RATE_LIMIT_ALLOW_REQUESTS, config.rate_limit.LOGIN_RATE_LIMIT_TIME_WINDOW)
