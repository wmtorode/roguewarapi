import time


class CacheObject:

    def __init__(self, data, expiry):
        self.data = data
        self.expireTime = time.time() + expiry


class CacheManager:

    def __init__(self):
        self.cache = {}

    def getCacheItem(self, key):
        if key in self.cache:
            if time.time() < self.cache[key].expireTime:
                return self.cache[key].data
        return None

    def placeCacheItem(self, key, item, expire=60):

        self.cache[key] = CacheObject(item, expire)