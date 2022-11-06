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
import time
import asyncio
import logging

import external
import ws_manager
import rdb_helper


"""
console event handling
"""


EXPIRED = []
ADD_KIND = '''add'''
UPDATE_KIND = '''update'''
REMOVE_KIND = '''remove'''
FAILED_KIND = '''failed'''

ALARM_EVENT = '''update_alarm_list'''
GROUP_EVENT = '''update_group_list'''
RESERVE_EVENT = '''update_reserve_list'''
STREAMING_EVENT = '''update_streaming_status'''
FAILED_LIST_EVENT = '''failed_list'''
PLAY_LIST_EVENT = '''update_play_list'''
FILE_NONE_EVENT = '''file_none'''


async def _fire_ws_response(ws_obj, data):
  if not ws_obj._closed:
    await ws_obj.send_str(json.dumps(data))
  else:
    logging.warning("cannot send event data")
    EXPIRED.append(ws_obj)


async def _fire_event(event, kind, value):
  _t = time.time()
  _data = {'e': event,
           'kind': kind,
           'v': value,
           '_t': _t}

  _l_wss = ws_manager.get_all_location_ws_obj()
  _s_wss = ws_manager.get_all_speaker_ws_obj()
  logging.info("### l wss : %s", len(_l_wss))
  logging.info("### s wss : %s", len(_s_wss))

  for _ws in _l_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("Failed to send location event data. Kind : %s",
                      kind, exc_info=True)
  for _ws in _s_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("Failed to send speaker event data. Kind : %s",
                      kind, exc_info=True)
  return ''


async def _handle_alarm_added_event(topic, value):
  asyncio.ensure_future(_fire_event(ALARM_EVENT, ADD_KIND, value))
  return ''


async def _handle_alarm_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(ALARM_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_alarm_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(ALARM_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_group_added_event(topic, value):
  asyncio.ensure_future(_fire_event(GROUP_EVENT, ADD_KIND, value))
  return ''


async def _handle_group_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(GROUP_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_group_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(GROUP_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_reserve_added_event(topic, value):
  asyncio.ensure_future(_fire_event(RESERVE_EVENT, ADD_KIND, value))
  return ''


async def _handle_reserve_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(RESERVE_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_reserve_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(RESERVE_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_streaming_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(STREAMING_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_failed_list(topic, value):
  asyncio.ensure_future(_fire_event(FAILED_LIST_EVENT, FAILED_KIND, value))
  return ''


async def _handle_playlist_added_event(topic, value):
  asyncio.ensure_future(_fire_event(PLAY_LIST_EVENT, ADD_KIND, value))
  return ''


async def _handle_playlist_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(PLAY_LIST_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_file_none_event(topic, value):
  asyncio.ensure_future(_fire_event(FILE_NONE_EVENT, FAILED_KIND, value))
  return ''


FUNC_MAP = {
  'alarm.added': _handle_alarm_added_event,
  'alarm.changed': _handle_alarm_updated_event,
  'alarm.removed': _handle_alarm_removed_event,
  'group.added': _handle_group_added_event,
  'group.changed': _handle_group_updated_event,
  'group.removed': _handle_group_removed_event,
  'reserve.added': _handle_reserve_added_event,
  'reserve.changed': _handle_reserve_updated_event,
  'reserve.removed': _handle_reserve_removed_event,
  'streaming.changed': _handle_streaming_updated_event,
  'failed.list': _handle_failed_list,
  'list.add': _handle_playlist_added_event,
  'list.remove': _handle_playlist_removed_event,
  'file.none': _handle_file_none_event
}


async def expire_ws():
  logging.info("Expired object length : %s", len(EXPIRED))
  while EXPIRED:
    ws_obj = EXPIRED.pop()
    ws_manager.remove_ws_obj(ws_obj)
    logging.info("Expire ws obj. ID : %s", id(ws_obj))
  logging.info("Remain WS location tracking obj length : %s",
               len(ws_manager.get_all_location_ws_obj()))
  logging.info("Remain WS speaker obj length : %s",
               len(ws_manager.get_all_speaker_ws_obj()))


async def update_handle(topic, value):
  _ret = ''
  logging.info("## From console topic : %s, value : %s", topic, value)
  if topic in FUNC_MAP:
    _func = FUNC_MAP[topic]
    _return_body = await _func(topic, value)
  else:
    logging.debug("Not handle event: %s", topic)
    _ret = '-1'
  return _ret
