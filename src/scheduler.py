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

import _http
import cache
import event
import constant
import dash_apis
import ws_manager
import console_event
import workprog_event
import streaming_event
from constant import BEACON_KIND, IPCAM_KIND, SCANNER_KIND, SPEAKER_KIND
from constant import ROUTER_KIND


if constant.IS_DEV:
  INTERVAL = 30  # 30s
else:
  INTERVAL = 10 # 10s

DETECTED_INTERVAL = 30
DETECTED_REPEATER_TIME = 5
REFRESH_INTERVAL = 30
EXPIRE_INTERVAL = 15


def _handle_scanner_list_loop(scanner_kind):
  scanner_fut = asyncio.ensure_future(cache.refresh_scanner_list(scanner_kind))

  def scanner_list_repeater(f):
    asyncio.get_event_loop().call_later(INTERVAL, _handle_scanner_list_loop, scanner_kind)
  scanner_fut.add_done_callback(scanner_list_repeater)


def _handle_beacon_list_loop(beacon_kind):
  beacon_fut = asyncio.ensure_future(cache.refresh_beacon_list(beacon_kind))

  def beacon_list_repeater(f):
    asyncio.get_event_loop().call_later(INTERVAL, _handle_beacon_list_loop, beacon_kind)
  beacon_fut.add_done_callback(beacon_list_repeater)


def _handle_cam_list_loop(cam_kind):
  cam_fut = asyncio.ensure_future(cache.refresh_cam_list(cam_kind))

  def cam_list_repeater(f):
    asyncio.get_event_loop().call_later(INTERVAL, _handle_cam_list_loop, cam_kind)
  cam_fut.add_done_callback(cam_list_repeater)


def _handle_speaker_list_loop(speaker_kind):
  speaker_fut = asyncio.ensure_future(cache.refresh_speaker_list(speaker_kind))

  def speaker_list_repeater(f):
    asyncio.get_event_loop().call_later(INTERVAL, _handle_speaker_list_loop, speaker_kind)
  speaker_fut.add_done_callback(speaker_list_repeater)


def _handle_router_list_loop(router_kind):
  router_fut = asyncio.ensure_future(cache.refresh_router_list(router_kind))

  def router_list_repeater(f):
    asyncio.get_event_loop().call_later(INTERVAL, _handle_router_list_loop, router_kind)
  router_fut.add_done_callback(router_list_repeater)


def _handle_refresh():
  refresh_future = asyncio.ensure_future(_send_refresh())

  def refresh_repeater(f):
    asyncio.get_event_loop().call_later(REFRESH_INTERVAL, _handle_refresh)

  refresh_future.add_done_callback(refresh_repeater)


def _handle_event_expire():
  expire_future = asyncio.ensure_future(event.expire_ws())

  def event_expire_repeater(f):
    asyncio.get_event_loop().call_later(EXPIRE_INTERVAL, _handle_event_expire)

  expire_future.add_done_callback(event_expire_repeater)


def _handle_streaming_expire():
  expire_future = asyncio.ensure_future(streaming_event.expire_ws())

  def streaming_expire_repeater(f):
    asyncio.get_event_loop().call_later(EXPIRE_INTERVAL, _handle_streaming_expire)

  expire_future.add_done_callback(streaming_expire_repeater)


def _handle_console_expire():
  expire_future = asyncio.ensure_future(console_event.expire_ws())

  def console_expire_repeater(f):
    asyncio.get_event_loop().call_later(EXPIRE_INTERVAL, _handle_console_expire)

  expire_future.add_done_callback(console_expire_repeater)


def _handle_workprog_expire():
  expire_future = asyncio.ensure_future(workprog_event.expire_ws())

  def console_expire_repeater(f):
    asyncio.get_event_loop().call_later(EXPIRE_INTERVAL, _handle_console_expire)

  expire_future.add_done_callback(console_expire_repeater)


async def _send_refresh():
  cur_time = time.time()
  for _wsobj in ws_manager.get_all_location_ws_obj():
    try:
      _resp = {'e': 'refresh',
               'v': True,
               '_t': cur_time}
      await event._fire_ws_response(_wsobj, _resp)
    except:
      logging.warning("failed to send refresh.", exc_info=True)


def start():
  _handle_scanner_list_loop(SCANNER_KIND)
  _handle_beacon_list_loop(BEACON_KIND)  # Include NEW_BEACON_KIND in dash_apis.py
  _handle_cam_list_loop(IPCAM_KIND)
  _handle_speaker_list_loop(SPEAKER_KIND)
  _handle_router_list_loop(ROUTER_KIND)
  _handle_refresh()
  _handle_event_expire()
  _handle_streaming_expire()
  _handle_console_expire()
  _handle_workprog_expire()
