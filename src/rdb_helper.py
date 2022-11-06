# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


import json
import logging

import redis

from adt import run_async
from constant import REDIS_HOST, REDIS_PORT
from constant import GADGETS_REDIS_DB, DATA_INFO_EXPIRE_REDIS_DB, STREAMING_REDIS_DB
from constant import GADGET_COUNT_LIST_EXPIRE_REDIS_DB


class RedisStore(object):
  def __init__(self, host, port, db):
    self.store = redis.StrictRedis(host=host, port=port, db=db)

  async def set_data(self, name, key, value):
    try:
      _ret = self.store.hset(name, key, json.dumps(value))
      return True if _ret else False
    except:
      logging.exception("Raise error while set data. key : %s, data : %s",
                        key, value)

  async def has_data(self, name, key):
    ret = self.store.hexists(name, key)
    return True if ret else False

  async def get_data(self, name, key):
    _ret = await self.has_data(name, key)
    if _ret:
      _data = self.store.hget(name, key)
      if _data is None:
        return None
      return json.loads(_data)
    else:
      return None

  async def hdel(self, name, key):
    ret = self.store.hdel(name, key)
    return ret

  async def hincrby(self, name, key, value):
    ret = self.store.hincrby(name, key, value)
    return ret

  async def exists(self, name):
    ret = self.store.exists(name)
    return ret

  async def sadd(self, key, value):
    ret = self.store.sadd(key, value)
    return ret

  async def smembers(self, key):
    ret = self.store.smembers(key)
    return ret

  async def srem(self, key, value):
    ret = self.store.srem(key, value)
    return ret

  async def sismember(self, key, member):
    ret = self.store.sismember(key, member)
    return ret

  async def set(self, name, value, expire_time):
    ret = self.store.set(name, json.dumps(value), expire_time)
    return ret

  async def get_values(self):
    keys = self.store.keys()
    ret = self.store.mget(keys)
    ret_list = []
    for v in ret:
      ret_list.append(json.loads(v.decode('utf-8')))
    return ret_list

  async def get_all(self, name):
    datas = self.store.hgetall(name)
    ret = {k.decode("utf-8"): json.loads(v.decode("utf-8")) for k, v in datas.items()}
    return ret

  async def get_data_of_values(self, name):
    values = self.store.hvals(name)
    if values:
      value_list = []
      for value in values:
        value_list += json.loads(value)
      return list(set(value_list))
    else:
      return []


# AT1 : 1 , AT2: 2
GADGETS = RedisStore(REDIS_HOST, REDIS_PORT, GADGETS_REDIS_DB)
DATA_INFO_EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT,
                                    DATA_INFO_EXPIRE_REDIS_DB)
STREAMING_DATA = RedisStore(REDIS_HOST, REDIS_PORT, STREAMING_REDIS_DB)
GADGET_COUNT_LIST_EXPIRE_CACHE = RedisStore(REDIS_HOST, REDIS_PORT,
                                            GADGET_COUNT_LIST_EXPIRE_REDIS_DB)


# EXPIRE_TIME = 15  # 15s
# EQUIP_EXPIRE_TIME = 120  # 2m
DATA_INFO_EXPIRE_TIME = 20  # 20s
GADGET_COUNT_EXPIRE_TIME = 20  # 20s
# EQUIP_OPERATOR_COUNT_KEY = '''equip-operator'''
DEVICE_DATA_KEY = '''device-data'''
DEVICE_DETECTED_DATA_KEY = '''device-detected-data'''


async def set_device_detected_data_info(key, value, is_force=False):
  await DATA_INFO_EXPIRE_CACHE.set(key, value, DATA_INFO_EXPIRE_TIME)
  try:
    if value:
      gid = value[0]['gid']
      value = await get_device_data_info(gid)
      await GADGET_COUNT_LIST_EXPIRE_CACHE.set(gid, value,
                                               GADGET_COUNT_EXPIRE_TIME)
  except:
    logging.exception("While Error")
  finally:
    return True


async def set_device_data_info(key, value, is_force=False):
  # key -> gid, hid,, value -> dict of data
  await GADGETS.set_data(DEVICE_DATA_KEY, key, value)
  return True


async def delete_device_data_info(key):
  await GADGETS.hdel(DEVICE_DATA_KEY, key)
  return True


async def get_device_data_info(key):
  _ret = await GADGETS.get_data(DEVICE_DATA_KEY, key)
  return _ret


async def get_all_detected_data():
  _ret = await DATA_INFO_EXPIRE_CACHE.get_values()
  return _ret


async def get_all_of_device_data():
  _ret = await GADGETS.get_all(DEVICE_DATA_KEY)
  return _ret


async def get_open_streaming_data(key):
  _ret = await STREAMING_DATA.smembers(key)
  if _ret:
    value_set = set([])
    for value in _ret:
      value_set.add(value.decode('utf-8'))
    return list(value_set)
  else:
    return []


async def set_open_streaming_data_info(key, value):
  await STREAMING_DATA.sadd(key, value)
  return True


async def delete_open_streaming_data_info(key, value):
  await STREAMING_DATA.srem(key, value)
  return True
