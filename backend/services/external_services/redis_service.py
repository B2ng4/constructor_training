# import aioredis
# from fastapi import Depends
# from typing import Optional
#
# class RedisService:
#     def __init__(self, redis_url: str = "redis://localhost:6379"):
#         self.redis_url = redis_url
#         self.pool: Optional[aioredis.Redis] = None
#
#     async def connect(self):
#         if not self.pool:
#             self.pool = await aioredis.from_url(self.redis_url, decode_responses=True)
#         return self.pool
#
#     async def close(self):
#         if self.pool:
#             await self.pool.close()
#             self.pool = None

