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
import asyncio

import _http
import cache
import constant
import external
import rdb_helper
import ws_manager
from constant import THIRD_BASE_URL, BASE_URL, STREAM_BASE_URL, PA_URL
from constant import SCANNER_KIND, STREAM_SERVER_DISCONNECT
from constant import BEACON_KIND, NEW_BEACON_KIND


OFFSET_SEC = 20
SKEC_TOKEN = '''c24609a47b9f7615a9acd157ed07af1e'''  # skec developer Token
SKEC_SMART_USER_ID = '''39c4676ad6a00079728f2c33da0d1e10'''  # skecsmart@gmail.com
ACCOUNT_ID = '''d526b46a854d018d355b90ee2527fd4e'''  # Galaxy A30


def _get_user_header(is_json=False):
  headers = {
    'Authorization': 'Bearer {}'.format(SKEC_TOKEN)
  }
  if is_json:
    headers['Content-Type'] = 'application/json'
  return headers


async def handle_speaker_data(speaker_data, topic):
  headers = {'Content-Type': 'application/json'}
  _data = {
    'e': topic,
    'v': speaker_data,
  }
  try:
    url = "{base}pa/event/speaker".format(base=PA_URL)
    data = json.dumps(_data)
    _resp = await _http.request(_http.POST, url, headers, data)
    if _resp['status'] == 200:
      if json.loads(_resp['body']):
        logging.info("Set speaker data to PA server successful.")
        return True
      else:
        logging.warning("Failed speaker data set to PA server.")
        return False
    else:
      raise Exception("Invalid response. Please confirm the request again.")
  except:
    logging.exception("Raise error while speaker set to PA server.",
                      speaker_data)
    return False


async def update_scanner(hub_obj):
  try:
    url = "{base}hubs/{hub_id}".format(base=THIRD_BASE_URL,
                                       hub_id=hub_obj['id'])
    headers = _get_user_header(is_json=True)
    data = json.dumps({"custom": hub_obj['custom']})
    logging.info("Update scanner location request. url : %s, data : %s",
                 url, data)
    _resp = await _http.request(_http.POST, url, headers, data)
    if _resp['status'] == 200:
      logging.info("update scanner location successful. Code : %s", _resp['status'])
      await cache.set_device_data(hub_obj, is_force=True)
      asyncio.ensure_future(external.send_update_scanner(hub_obj))
      return True
    else:
      logging.warning("Failed update scanner location. Code : %s", _resp['status'])
      return False
  except:
    logging.exception("Raise error while update scanner location. hub : %s",
                      hub_obj)
    return False


async def update_cam_location(cam_data):
  try:
    url = "{base}gadgets/{cam_data}".format(base=THIRD_BASE_URL,
                                            cam_data=cam_data['id'])
    headers = _get_user_header(is_json=True)
    data = json.dumps({"custom": cam_data['custom']})
    logging.info("Update cam location request. url : %s, data : %s",
                 url, data)
    _resp = await _http.request(_http.POST, url, headers, data)
    if _resp['status'] == 200:
      logging.info("update cam location successful.")
      await cache.set_device_data(cam_data, is_force=True)
      return True
    else:
      logging.warning("Failed update cam location.")
      return False
  except:
    logging.exception("Raise error while update cam location.",
                      cam_data)
    return False


async def update_beacon_location(beacons_data):
  try:
    url = "{base}gadgets/{beacons_data}".format(base=THIRD_BASE_URL,
                                                beacons_data=beacons_data['id'])
    headers = _get_user_header(is_json=True)
    data = json.dumps({"custom": beacons_data['custom']})
    logging.info("Update beacon location request. url : %s, data : %s",
                 url, data)
    _resp = await _http.request(_http.POST, url, headers, data)
    if _resp['status'] == 200:
      logging.info("update beacon location successful. Resp : %s", _resp)
      await cache.set_device_data(beacons_data, is_force=True)
      return True
    else:
      logging.warning("Failed update beacon location. Resp : %s", _resp)
      return False
  except:
    logging.warning("Raise error while get beacon list. url : %s",
                    url, exc_info=True)
    return False


async def update_speaker_location(speaker_data):
  try:
    url = "{base}gadgets/{speaker_data}".format(base=THIRD_BASE_URL,
                                                speaker_data=speaker_data['id'])
    headers = _get_user_header(is_json=True)
    data = json.dumps(speaker_data)
    logging.info("Update speaker location request. url : %s, data : %s",
                 url, data)
    _resp = await _http.request(_http.POST, url, headers, data)
    if _resp['status'] == 200:
      logging.info("update speaker location successful.")
      await cache.set_device_data(speaker_data, is_force=True)
      return True
    else:
      logging.warning("Failed update speaker location.")
      return False
  except:
    logging.exception("Raise error while speaker location.",
                      speaker_data)
    return False


async def update_router_location(router_data):
  try:
    url = "{base}gadgets/{router_data}".format(base=THIRD_BASE_URL,
                                               router_data=router_data['id'])
    headers = _get_user_header(is_json=True)
    data = json.dumps(router_data)
    logging.info("Update router location request. url : %s, data : %s",
                 url, data)
    _resp = await _http.request(_http.POST, url, headers, data)
    if _resp['status'] == 200:
      logging.info("update router location successful.")
      await cache.set_device_data(router_data, is_force=True)
      return True
    else:
      logging.warning("Failed update router location. resp : %s", _resp)
      return False
  except:
    logging.exception("Raise error while router location.",
                      router_data)
    return False


async def get_scanner_list(kind):
  try:
    if constant.IS_DEV:
      url = "{base}hub-kinds/{kind}/hubs".format(base=THIRD_BASE_URL,
                                                kind=kind)
      headers = _get_user_header()
      params = {
          'kind': 0,
          'issuer': 1
      }
      logging.info("Get scanner list request. url :%s, params : %s", url, params)
      _resp = await _http.request(_http.GET, url, headers, params=params)
    else:
      url = "http://api.mib.io/i/v1/users/{}/hubs".format(SKEC_SMART_USER_ID)
      headers = {"Src": "{}.".format(ACCOUNT_ID)}
      logging.info("Get scanner list request. url :%s", url)
      _resp = await _http.request(_http.GET, url, headers)
    if _resp['status'] == 200:
      _scanners = json.loads(_resp['body'])
      if constant.IS_DEV:
        return _scanners
      else:
        return _scanners['v']
    else:
      logging.warning("Failed to get scanner list. response: %s", _resp)
      return []
  except:
    logging.exception("Raise error while get scanner list. url : %s", url)
    return []


async def get_beacon_list(product_id):
  try:
    if constant.IS_DEV:
      url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                  pid=product_id)
      headers = _get_user_header()
    else:
      url = "http://api.mib.io/i/v1/users/{}/gadgets".format(SKEC_SMART_USER_ID)
      headers = {"Src": "{}.".format(ACCOUNT_ID)}
    logging.info("Get beacon list request. url : %s", url)
    _resp = await _http.request(_http.GET, url, headers)
    if _resp['status'] == 200:
      new_beacons_list = []
      _gadgets = json.loads(_resp['body'])
      if constant.IS_DEV:
        for gadget in _gadgets:
          if gadget['hub_id']:
            _hub_chk = await rdb_helper.get_device_data_info(gadget['hub_id'])
            if _hub_chk:
              new_beacons_list.append(gadget)
            else:
              hub_chk = await get_scanner_info(gadget['hub_id'])
              new_beacons_list.append(gadget)
              await rdb_helper.set_device_data_info(hub_chk['id'], hub_chk)
        return new_beacons_list
      else:
        for gadget in _gadgets['v']:
          if gadget['hub_id']:
            _hub_chk = await rdb_helper.get_device_data_info(gadget['hub_id'])
            if _hub_chk:
              if gadget['kind'] in [BEACON_KIND, NEW_BEACON_KIND]:
                new_beacons_list.append(gadget)
            else:
              hub_chk = await get_scanner_info(gadget['hub_id'])
              if gadget['kind'] in [BEACON_KIND, NEW_BEACON_KIND]:
                new_beacons_list.append(gadget)
                await rdb_helper.set_device_data_info(hub_chk['id'], hub_chk)
        return new_beacons_list
    else:
      logging.warning("Failed to get beacon list. response: %s", _resp)
      return []
  except:
    logging.exception("Raise error while get beacon list. url : %s", url)
    return []


async def get_cam_list(pid):
  try:
    url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                pid=pid)
    headers = _get_user_header()
    logging.info("Get cam list request. url : %s", url)
    _resp = await _http.request(_http.GET, url, headers)

    if _resp['status'] == 200:
      ret_list = []
      _gadgets = json.loads(_resp['body'])
      for gadget in _gadgets:
        if gadget['hub_id']:
          ret_list.append(gadget)
      return ret_list
    else:
      logging.warning("Failed to get cam list. response: %s", _resp)
      return []
  except:
    logging.warning("Raise error while get cam list. url : %s", url)
    return []


async def get_speaker_list(pid):
  try:
    url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                pid=pid)
    headers = _get_user_header()
    logging.info("Get speaker list request. url : %s", url)
    _resp = await _http.request(_http.GET, url, headers)

    if _resp['status'] == 200:
      ret_list = []
      _gadgets = json.loads(_resp['body'])
      for gadget in _gadgets:
        if gadget['hub_id']:
          ret_list.append(gadget)
      return ret_list
    else:
      logging.warning("Failed to get speaker list. response: %s", _resp)
      return []
  except:
    logging.warning("Raise error while get speaker list. url : %s", url)
    return []


async def get_router_list(pid):
  try:
    url = "{base}products/{pid}/gadgets".format(base=THIRD_BASE_URL,
                                                pid=pid)
    headers = _get_user_header()
    logging.info("Get router list request. url : %s", url)
    _resp = await _http.request(_http.GET, url, headers)

    if _resp['status'] == 200:
      ret_list = []
      _gadgets = json.loads(_resp['body'])
      for gadget in _gadgets:
        if gadget['hub_id']:
          ret_list.append(gadget)
      return ret_list
    else:
      logging.warning("Failed to get router list. response: %s", _resp)
      return []
  except:
    logging.warning("Raise error while get router list. url : %s", url)
    return []


async def get_beacon_info(beacon_id):
  try:
    url = "{base}gadgets/{bid}".format(base=BASE_URL, bid=beacon_id)
    headers = _get_user_header()
    logging.info("Get beacon info request. url : %s", url)
    _resp = await _http.request(_http.GET, url, headers)
    if _resp['status'] == 200:
      _gadget = json.loads(_resp['body'])
      return _gadget['v']
    else:
      logging.info("Failed to get beacon data. response: %s", _resp)
      return {}
  except:
    logging.exception("Raise error while get beacon info. url : %s", url)
    return {}


async def get_scanner_info(hub_id, org_id=None):
  try:
    url = "{base}hubs/{hid}".format(base=BASE_URL, hid=hub_id)
    headers = _get_user_header()
    logging.info("Get hub info request. url : %s", url)
    _resp = await _http.request(_http.GET, url, headers)
    if _resp['status'] == 200:
      _scanner = json.loads(_resp['body'])
      return _scanner['v']
    else:
      logging.warning("Failed to get hub data. response: %s", _resp)
      return {}
  except:
    logging.exception("Raise error while get hub info. url : %s", url)
    return {}


async def get_detected_beacons(hub_id, query_id=None, start_ts=None, end_ts=None):
  url = "{base}hubs/{hid}/location".format(base=BASE_URL, hid=hub_id)
  params = {}
  headers = _get_user_header()
  try:
    if not query_id:
      params['start_ts'] = str(start_ts)
      params['end_ts'] = str(end_ts)
    else:
      params['query_id'] = str(query_id)
    logging.info("Get detected beacons request. url : %s, params : %s",
                 url, params)
    _resp = await _http.request(_http.GET, url, headers, params=params)
    if _resp['status'] == 200:
      detcted_data = json.loads(_resp['body'])
      ret = detcted_data['v']
      return ret
    else:
      logging.warning("Failed to Get Detected Beacons Response. %s, header :%s, params : %s",
                      _resp, headers, params)
      return {}
  except:
    logging.exception("Raise error while get detected beacons. url : %s, params : %s",
                      url, params)
    return {}


async def open_stream(req_list, client_id):
  url = '{base}/ipcams/stream/open'.format(base=STREAM_BASE_URL)
  try:
    logging.info("Open Stream Request. request: %s, client_id: %s",
                 req_list, client_id)
    params = {}
    params['client_id'] = str(client_id)
    _ws = ws_manager.get_ws(client_id)
    if _ws['internal']:
      params['internal'] = 1
    else:
      params['internal'] = 0
    _resp = await _http.request(_http.POST, url, headers=None,
                                body=json.dumps(req_list), params=params)
    if _resp['status'] == 200:
      logging.info("open stream successful. Code: %s", _resp['status'])
      _data = json.loads(_resp['body'])
      return _data
    else:
      raise Exception("Failed open stream. url: %s", url)
  except:
    _ret_list = []
    logging.exception("Raise error while open stream. url: %s", url)
    for _req_data in req_list:
      _ret_list.append({_req_data['gid']: STREAM_SERVER_DISCONNECT})
    return _ret_list


async def close_stream(req_list, client_id):
  url = '{base}/ipcams/stream/close'.format(base=STREAM_BASE_URL)
  params = {}
  params['client_id'] = str(client_id)
  try:
    logging.info("Close Stream Request. request: %s", req_list)
    _resp = await _http.request(_http.POST, url, headers=None,
                                body=json.dumps(req_list), params=params)
    if _resp['status'] == 200:
      logging.info("close stream successful. Code: %s", _resp['status'])
      _data = json.loads(_resp['body'])
      return _data
    else:
      logging.warning("Failed close stream. url: %s", url)
      return False
  except:
    logging.exception("Raise error while open stream. url: %s", url)
    return False
