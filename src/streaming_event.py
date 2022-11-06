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


"""
streaming event handling
"""


import rdb_helper
import logging
import time
import ws_manager
import asyncio
import json

from constant import IPCAM_KIND

EXPIRED = []


async def _fire_ws_response(ws_obj, data):
  if not ws_obj._closed:
    await ws_obj.send_str(json.dumps(data))
    logging.info("Send to client successful!")
  else:
    logging.warning("cannot send refresh data")
    EXPIRED.append(ws_obj)


async def _reopen_stream(gadget_ids):
  _t = time.time()

  _client_ids = set([])
  for _gid, _data in gadget_ids.items():
    _client_id_list = await rdb_helper.get_open_streaming_data(_gid)
    for _client_id in _client_id_list:
      _client_ids.add(_client_id)

  logging.info("Clients for reopen stream: %s", _client_ids)

  for _client_id in _client_ids:
    _gids = await rdb_helper.get_open_streaming_data(_client_id)
    _ws = ws_manager.get_ws(int(_client_id))
    _ret_list = []
    if _ws:
      _ret_list = await _get_ret_list(_ws, _gids, gadget_ids)

    _data = {'e': 'reopen_stream',
             'v': _ret_list,
             '_t': _t}
    logging.info("Create sending data to client: %s", _data)

    try:
      asyncio.ensure_future(_fire_ws_response(_ws['ws_obj'], _data))
    except:
      logging.warning("failed to send online data event", exc_info=True)
  return ''


async def _sync():
  _device_data = await rdb_helper.get_all_of_device_data()
  _gid_dict = {}
  for _device in _device_data.values():
    if _device['kind'] == IPCAM_KIND and 'ip' in _device['custom']:
      _gid_dict[_device['id']] = _device['custom']['ip']
  _ret = {}
  for _gid, _ip in _gid_dict.items():
    _client_ids = await rdb_helper.get_open_streaming_data(_gid)
    _ret[_ip] = _client_ids
  return _ret


async def _get_ret_list(_ws, _gids, gadget_ids):
  _ret_list = []
  for _gid in _gids:
    if _gid in gadget_ids:
      if isinstance(gadget_ids[_gid], int):
        _result = gadget_ids[_gid]
        _ret = {_gid: _result}
        _ret_list.append(_ret)
      else:
        if _ws['internal']:
          _result = gadget_ids[_gid]['in_addr']
          _ret = {_gid: _result}
          _ret_list.append(_ret)
        else:
          _result = gadget_ids[_gid]['ex_addr']
          _ret = {_gid: _result}
          _ret_list.append(_ret)
  return _ret_list


async def expire_ws():
  logging.info("Expired object lenght : %s", len(EXPIRED))
  while EXPIRED:
    ws_obj = EXPIRED.pop()
    ws_manager.remove_ws_obj(ws_obj)
    logging.info("Expire ws obj. ID : %s", id(ws_obj))
  logging.debug("Remain WS location tracking obj length : %s",
                len(ws_manager.get_all_location_ws_obj()))
  logging.debug("Remain WS ipcam obj length : %s",
                len(ws_manager.get_all_ipcam_ws_obj()))


async def refresh_handle(refresh_data):
  logging.info("From streaming refresh data: %s", refresh_data)
  await _reopen_stream(refresh_data)
  return ''


async def sync_handle():
  logging.info("From streaming server sync request.")
  _ret = await _sync()
  return _ret
