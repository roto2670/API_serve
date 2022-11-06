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


import time
import asyncio
import logging
import subprocess

import adt
import event
import dash_apis
import rdb_helper
import ws_manager

from constant import CONNECT_CODE, STATUS_ON, STATUS_OFF


__ON_OFF__ = {1: 'on', 0: 'off'}


async def refresh_scanner_list(scanner_kind):
  _scanner_list = await dash_apis.get_scanner_list(scanner_kind)
  await set_device_data_list(_scanner_list)


async def refresh_beacon_list(beacon_kind):
  _gadget_list = await dash_apis.get_beacon_list(beacon_kind)
  await set_device_data_list(_gadget_list)


async def _handle_cam(cam_list, ipcam_kind):
  for _cam in cam_list:
    if 'ip' in _cam['custom']:
      result, cmd_line = await adt.run_async(subprocess.getstatusoutput,
                                             "ping -c 1 " + _cam['custom']['ip'])
      _current_status = STATUS_OFF
      if result == 0:
        _current_status = STATUS_ON
      _cam['status'] = _current_status
      _cam_data = await rdb_helper.get_device_data_info(_cam['id'])
      if _cam_data:
        _before_status = _cam_data['status']
        if _current_status != _before_status:
          _ws_obj_list = ws_manager.get_all_ws_obj()
          _t = time.time()
          for _ws_obj in _ws_obj_list:
            _data = {'e': __ON_OFF__[_current_status],
                     'v': _cam,
                     'kind': ipcam_kind,
                     '_t': _t}
            try:
              await event._fire_ws_response(_ws_obj, _data)
              logging.info("Change ipcam status. ip : %s, name : %s, bef : %s, cur : %s",
                           _cam['custom']['ip'], _cam['name'], _before_status,
                           _current_status)
            except:
              logging.warning("failed to send ipcam %s event data",
                              __ON_OFF__[_current_status], exc_info=True)
    await set_device_data(_cam)


async def refresh_cam_list(ipcam_kind):
  _cam_list = await dash_apis.get_cam_list(ipcam_kind)
  await _handle_cam(_cam_list, ipcam_kind)


async def _handle_speaker(speaker_list, speaker_kind):
  for _speaker in speaker_list:
    if 'ip' in _speaker['custom']:
      result, cmd_line = await adt.run_async(subprocess.getstatusoutput,
                                             "ping -c 1 " + _speaker['custom']['ip'])
      _current_status = STATUS_OFF
      if result == 0:
        _current_status = STATUS_ON
      _speaker['status'] = _current_status
      _speaker_data = await rdb_helper.get_device_data_info(_speaker['id'])
      if _speaker_data:
        _before_status = _speaker_data['status']
        if _current_status != _before_status:
          _ws_obj_list = ws_manager.get_all_ws_obj()
          _t = time.time()
          for _ws_obj in _ws_obj_list:
            _data = {'e': __ON_OFF__[_current_status],
                     'v': _speaker,
                     'kind': speaker_kind,
                     '_t': _t}
            try:
              await event._fire_ws_response(_ws_obj, _data)
              logging.info("Change speaker status. ip : %s, name : %s, bef : %s, cur : %s",
                           _speaker['custom']['ip'], _speaker['name'],
                           _before_status, _current_status)
            except:
              logging.warning("failed to send speaker %s event data",
                              __ON_OFF__[_current_status], exc_info=True)
    await set_device_data(_speaker)


async def refresh_speaker_list(speaker_kind):
  _speaker_list = await dash_apis.get_speaker_list(speaker_kind)
  await _handle_speaker(_speaker_list, speaker_kind)


async def _handle_router(router_list, router_kind):
  for _router in router_list:
    if 'ip' in _router['custom']:
      result, cmd_line = await adt.run_async(subprocess.getstatusoutput,
                                             "ping -c 1 " + _router['custom']['ip'])
      _current_status = STATUS_OFF
      if result == 0:
        _current_status = STATUS_ON
      _router['status'] = _current_status
      _router_data = await rdb_helper.get_device_data_info(_router['id'])
      if _router_data:
        _before_status = _router_data['status']
        if _current_status != _before_status:
          _ws_obj_list = ws_manager.get_all_ws_obj()
          _t = time.time()
          for _ws_obj in _ws_obj_list:
            _data = {'e': __ON_OFF__[_current_status],
                     'v': _router,
                     'kind': router_kind,
                     '_t': _t}
            try:
              await event._fire_ws_response(_ws_obj, _data)
              logging.info("Change router status. ip : %s, name : %s, bef : %s, cur : %s",
                           _router['custom']['ip'], _router['name'],
                           _before_status, _current_status)
            except:
              logging.warning("failed to send router %s event data",
                              __ON_OFF__[_current_status], exc_info=True)
    await set_device_data(_router)


async def refresh_router_list(router_kind):
  _router_list = await dash_apis.get_router_list(router_kind)
  await _handle_router(_router_list, router_kind)


async def set_device_data(device_data, is_force=False):
  await rdb_helper.set_device_data_info(device_data['id'], device_data,
                                        is_force=is_force)
  return True


async def set_device_data_list(device_data_list, is_force=False):
  for device_data in device_data_list:
    await rdb_helper.set_device_data_info(device_data['id'], device_data,
                                          is_force=is_force)
  return True
