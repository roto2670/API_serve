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


from constant import WS_LOCATION_KIND, WS_MOI_KIND, WS_SPEAKER_KIND, WS_WORK_KIND

__WSS__ = {}


def get_ws(client_id):
  _ret = None
  if client_id in __WSS__:
    _ret = __WSS__[client_id]
  return _ret


def get_ws_obj(client_id):
  _ret = None
  if client_id in __WSS__:
    _ret = __WSS__[client_id]['ws_obj']
  return _ret


def add_ws(ws_obj, client_kind=None, internal=None):
  _client_id = id(ws_obj)
  _data = {'ws_obj': ws_obj,
           'client_kind': client_kind,
           'internal': internal,
          }
  __WSS__[_client_id] = _data
  return _client_id


def get_all():
  return __WSS__


def get_all_ws_obj():
  ws_obj_list = []
  for ws in __WSS__.values():
    ws_obj_list.append(ws['ws_obj'])
  return ws_obj_list


def remove_ws_obj(ws_obj, client_id=None):
  _client_id = client_id or id(ws_obj)
  if _client_id in __WSS__:
    del __WSS__[_client_id]


def get_all_location_ws_obj():
  location_ws_obj_list = []
  for ws in __WSS__.values():
    if ws['client_kind'] == WS_LOCATION_KIND:
      location_ws_obj_list.append(ws['ws_obj'])
  return location_ws_obj_list


def get_all_workprog_ws_obj():
  location_ws_obj_list = []
  for ws in __WSS__.values():
    if ws['client_kind'] == WS_WORK_KIND:
      location_ws_obj_list.append(ws['ws_obj'])
  return location_ws_obj_list


def get_all_ipcam_ws_obj():
  ipcam_ws_obj_list = []
  for ws in __WSS__.values():
    if ws['client_kind'] == WS_MOI_KIND:
      ipcam_ws_obj_list.append(ws['ws_obj'])
  return ipcam_ws_obj_list


def get_all_speaker_ws_obj():
  speaker_ws_obj_list = []
  for ws in __WSS__.values():
    if ws['client_kind'] == WS_SPEAKER_KIND:
      speaker_ws_obj_list.append(ws['ws_obj'])
  return speaker_ws_obj_list
