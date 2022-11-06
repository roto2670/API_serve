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
import dash_apis


"""
cloud event handling
"""


EXPIRED = []


async def _fire_ws_response(ws_obj, data):
  if not ws_obj._closed:
    await ws_obj.send_str(json.dumps(data))
  else:
    logging.warning("cannot send event data")
    EXPIRED.append(ws_obj)


async def _handle_added_event(topic, value):
  _t = time.time()
  if topic.split('.')[0] == 'hub':
    _kind = 'hub'
    _key = value['id']
  else:
    _kind = value['kind']
    _key = value['id']
  await rdb_helper.set_device_data_info(_key, value)
  _data = {'e': 'added',
           'v': value,
           'kind': _kind,
           '_t': _t}

  _l_wss = ws_manager.get_all_location_ws_obj()

  for _ws in _l_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("failed to send add location event data", exc_info=True)

  if _kind == 'ipcam':
    _i_wss = ws_manager.get_all_ipcam_ws_obj()
    for _ws in _i_wss:
      try:
        asyncio.ensure_future(_fire_ws_response(_ws, _data))
      except:
        logging.warning("failed to send add ipcam event data", exc_info=True)

  if _kind == 'speaker':
    await dash_apis.handle_speaker_data(value, 'added')
    _s_wss = ws_manager.get_all_speaker_ws_obj()
    for _ws in _s_wss:
      try:
        asyncio.ensure_future(_fire_ws_response(_ws, _data))
      except:
        logging.warning("failed to send add speaker event data", exc_info=True)

  return ''


async def _handle_updated_event(topic, value):
  _t = time.time()
  _kind = None
  if topic.split('.')[0] == 'hub':
    _kind = 'hub'
    _key = value['id']
  else:
    _key = value['id']
  _data = await rdb_helper.get_device_data_info(_key)
  if _data is None:
    return ''
  _data.update(value)
  await rdb_helper.set_device_data_info(_key, _data)
  if not _kind:
    _kind = _data['kind']
  _data = {'e': 'updated',
           'v': value,
           'kind': _kind,
           '_t': _t}

  _l_wss = ws_manager.get_all_location_ws_obj()
  for _ws in _l_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("failed to send update location event data", exc_info=True)

  if _kind == 'ipcam':
    _i_wss = ws_manager.get_all_ipcam_ws_obj()
    for _ws in _i_wss:
      try:
        asyncio.ensure_future(_fire_ws_response(_ws, _data))
      except:
        logging.warning("failed to send update ipcam event data", exc_info=True)

  if _kind == 'speaker':
    await dash_apis.handle_speaker_data(value, 'updated')
    _s_wss = ws_manager.get_all_speaker_ws_obj()
    for _ws in _s_wss:
      try:
        asyncio.ensure_future(_fire_ws_response(_ws, _data))
      except:
        logging.warning("failed to send update speaker event data", exc_info=True)
  return ''


async def _handle_removed_event(topic, value):
  _t = time.time()
  if topic.split('.')[0] == 'hub':
    _kind = 'hub'
    _key = value['id']
  else:
    _key = value['id']
    _kind = value['kind']
  await rdb_helper.delete_device_data_info(_key)
  _data = { 'e': 'removed',
            'v': value,
            'kind': _kind,
            '_t': _t }

  _l_wss = ws_manager.get_all_location_ws_obj()

  for _ws in _l_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("failed to send remove location event data", exc_info=True)

  if _kind == 'ipcam':
    _i_wss = ws_manager.get_all_ipcam_ws_obj()
    for _ws in _i_wss:
      try:
        asyncio.ensure_future(_fire_ws_response(_ws, _data))
      except:
        logging.warning("failed to send remove ipcam event data", exc_info=True)

  if _kind == 'speaker':
    await dash_apis.handle_speaker_data(value, 'removed')
    _s_wss = ws_manager.get_all_speaker_ws_obj()
    for _ws in _s_wss:
      try:
        asyncio.ensure_future(_fire_ws_response(_ws, _data))
      except:
        logging.warning("failed to send remove speaker event data", exc_info=True)
  return ''


async def _handle_detected_event(topic, value):
  _t = time.time()
  _key = _t
  await rdb_helper.set_device_detected_data_info(_key, value)
  _data = { 'e': 'detected',
            'v': value,
            '_t': _t }
  _wss = ws_manager.get_all_location_ws_obj()
  for _ws in _wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("failed to send detected event data", exc_info=True)
  asyncio.ensure_future(external.send_detected_data(value))
  return ''


async def _handle_online_event(topic, value):
  _t = time.time()
  _key = value['id']
  await rdb_helper.set_device_data_info(_key, value)
  _data = { 'e': 'on',
            'v': value,
            'kind': 'hub',
            '_t': _t }
  _wss = ws_manager.get_all_location_ws_obj()
  for _ws in _wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("failed to send online data event", exc_info=True)
  return ''


async def _handle_offline_event(topic, value):
  _t = time.time()
  _key = value['id']
  await rdb_helper.set_device_data_info(_key, value)
  _data = { 'e': 'off',
            'v': value,
            'kind': 'hub',
            '_t': _t }
  _wss = ws_manager.get_all_location_ws_obj()
  for _ws in _wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("failed to send offline data event", exc_info=True)
  return ''


FUNC_MAP = {
  'hub.added': _handle_added_event,
  'gadget.paired': _handle_added_event,
  'gadget.added': _handle_added_event,
  'gadget.connected': _handle_added_event,
  'hub.changed': _handle_updated_event,
  'gadget.changed': _handle_updated_event,
  'hub.removed': _handle_removed_event,
  'gadget.removed': _handle_removed_event,
  'gadget.unpaired': _handle_removed_event,
  'gadget.disconnected': _handle_removed_event,
  'gadget.detected': _handle_detected_event,
  'hub.online': _handle_online_event,
  'hub.offline': _handle_offline_event
}


async def expire_ws():
  logging.info("Expired object length : %s", len(EXPIRED))
  while EXPIRED:
    ws_obj = EXPIRED.pop()
    ws_manager.remove_ws_obj(ws_obj)
    logging.info("Expire ws obj. ID : %s", id(ws_obj))
  logging.debug("Remain WS location tracking obj length : %s",
                len(ws_manager.get_all_location_ws_obj()))
  logging.debug("Remain WS ipcam obj length : %s",
                len(ws_manager.get_all_ipcam_ws_obj()))
  logging.debug("Remain WS speaker obj length : %s",
                len(ws_manager.get_all_speaker_ws_obj()))


async def handle(topic, value):
  _ret = ''
  logging.info("## From cloud topic : %s, value : %s", topic, value)
  if topic in FUNC_MAP:
    _func = FUNC_MAP[topic]
    _return_body = await _func(topic, value)
  else:
    logging.debug("Not handle event: %s", topic)
    _ret = '-1'
  return _ret
