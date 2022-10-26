######################################
#                                    #
#               diary                #
#                                    #
#                MIT                 #
#     Copyright (C) 2022 dodaucy     #
#  https://github.com/dodaucy/diary  #
#                                    #
######################################


import time

from databases import Database
from fastapi import Cookie, HTTPException, Request, status


class RateLimitHandler:
    def __init__(self, database: Database, allow_requests: int, in_time: int) -> None:
        self.db = database
        self.rate_limit = {}
        self.capacity = allow_requests
        self.rate = in_time / allow_requests

    async def trigger(self, request: Request, token: str = Cookie("")) -> None:
        """Rate limit by ip address"""

        # Get time
        current_time = time.time()

        # Add ip to rate limit if not already in it
        if request.client.host not in self.rate_limit:
            self.rate_limit[request.client.host] = {
                "tokens": self.capacity,
                "last_request": current_time
            }

        self.rate_limit[request.client.host]['tokens'] += (current_time - self.rate_limit[request.client.host]['last_request']) * (1 / self.rate)

        if self.rate_limit[request.client.host]['tokens'] > self.capacity:
            self.rate_limit[request.client.host]['tokens'] = self.capacity

        self.rate_limit[request.client.host]['last_request'] = current_time

        # Clean up
        for key in list(self.rate_limit.keys()):
            if self.rate_limit[key]['last_request'] < current_time - self.rate * self.capacity:
                del self.rate_limit[key]

        # Check if rate limit is exceeded
        if self.rate_limit[request.client.host]['tokens'] < 1:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {round(((1 - self.rate_limit[request.client.host]['tokens']) * self.rate) + 0.01, 3)} seconds."
            )

        self.rate_limit[request.client.host]['tokens'] -= 1

        # Update last request
        if token:
            await self.db.execute(
                "UPDATE sessions SET last_request = UNIX_TIMESTAMP() WHERE token = :token",
                {
                    "token": token
                }
            )
