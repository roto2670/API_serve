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


import os
import json
import time
import asyncio
import logging
import logging.handlers
from uuid import uuid4

import constant
import rdb_helper
import dash_apis
import scheduler
import event
import ws_manager
import streaming_event
import console_event
import workprog_event
import cache
from constant import SCANNER_KIND, IPCAM_KIND, SPEAKER_KIND, ROUTER_KIND
from constant import NEW_BEACON_KIND
from constant import IPCAM_DISCONNECT, BAD_REQUEST
from constant import STATUS_OFF, STATUS_ON

from aiohttp import web


async def _subscribe(ws_resp, client_kind, internal):
  _client_id = None
  _client_id = ws_manager.add_ws(ws_resp, client_kind, internal)
  return _client_id


async def _unsubscribe(ws_resp, client_kind, client_id=None):
  _client_id = client_id or id(ws_resp)
  ws_manager.remove_ws_obj(ws_resp, _client_id)
  return True


async def _get_data(ws_resp, kind):
  _new_ret = []
  if kind == constant.BEACON_KIND:
    _ret = await rdb_helper.get_all_of_device_data()
    for data in _ret.values():
      if data['kind'] in [kind, NEW_BEACON_KIND]:
        _new_ret.append(data)
  elif kind == constant.HUB_KIND:
    _ret = await rdb_helper.get_all_of_device_data()
    for data in _ret.values():
      if 'issuer' in data and data['issuer'] == 'com.thenaran.skec':
        _new_ret.append(data)
  elif kind == constant.IPCAM_KIND:
    _ret = await rdb_helper.get_all_of_device_data()
    for data in _ret.values():
      if data['kind'] == kind:
        _new_ret.append(data)
  elif kind == constant.SPEAKER_KIND:
    _ret = await rdb_helper.get_all_of_device_data()
    for data in _ret.values():
      if data['kind'] == kind:
        _new_ret.append(data)
  elif kind == constant.ROUTER_KIND:
    _ret = await rdb_helper.get_all_of_device_data()
    for data in _ret.values():
      if data['kind'] == kind:
        _new_ret.append(data)
  return _new_ret


async def _update_data(ws_resp, kind, data, client_id=None):
  ret_list = []
  if kind == constant.BEACON_KIND:
    for beacon in data:
      _ret = await dash_apis.update_beacon_location(beacon)
      if not _ret:
        ret_list.append(beacon['id'])
  elif kind == constant.HUB_KIND:
    for hub in data:
      _ret = await dash_apis.update_scanner(hub)
      if not _ret:
        ret_list.append(hub['id'])
  elif kind == constant.IPCAM_KIND:
    for ipcam in data:
      ret = await dash_apis.update_cam_location(ipcam)
      if not ret:
        ret_list.append(ipcam['id'])
  elif kind == constant.SPEAKER_KIND:
    for speaker in data:
      ret = await dash_apis.update_speaker_location(speaker)
      if not ret:
        ret_list.append(speaker['id'])
  elif kind == constant.ROUTER_KIND:
    for router in data:
      ret = await dash_apis.update_router_location(router)
      if not ret:
        ret_list.append(router['id'])
  return ret_list


async def _get_detected_list(ws_resp):
  _ret = await rdb_helper.get_all_detected_data()
  return _ret


async def _open_stream(ws_resp, ids):
  _client_id = id(ws_resp)
  request_list = []
  disconnect_list = []
  error_list = []
  for gadget_id in ids:
    _gadget_data = {}
    _ret = await rdb_helper.get_device_data_info(gadget_id)
    if _ret and 'ip' in _ret['custom']:
      if _ret['status'] == STATUS_ON:
        _gadget_data['gid'] = gadget_id
        _gadget_data['ip'] = _ret['custom']['ip']
        _gadget_data['id'] = _ret['custom']['id']
        _gadget_data['pw'] = _ret['custom']['password']
        request_list.append(_gadget_data)
      else:
        disconnect_list.append(gadget_id)
    else:
      error_list.append(gadget_id)
  url_list = []
  if request_list:
    url_list = await dash_apis.open_stream(request_list, _client_id)
  for disconnect_gid in disconnect_list:
    _disconnect_data = {}
    _disconnect_data[disconnect_gid] = IPCAM_DISCONNECT
    url_list.append(_disconnect_data)
  for error_gid in error_list:
    _error_data = {}
    _error_data[error_gid] = BAD_REQUEST
    url_list.append(_error_data)
  for _data in url_list:
    for _gid, _url in _data.items():
      await rdb_helper.set_open_streaming_data_info(_gid, _client_id)
      await rdb_helper.set_open_streaming_data_info(_client_id, _gid)
  return url_list


async def _close_stream(ws_resp, ids):
  _client_id = id(ws_resp)
  request_list = []
  try:
    for gadget_id in ids:
      _gadget_data = {}
      _ret = await rdb_helper.get_device_data_info(gadget_id)
      if _ret and 'ip' in _ret['custom']:
        if _ret['status'] == STATUS_ON:
          _gadget_data['gid'] = gadget_id
          _gadget_data['ip'] = _ret['custom']['ip']
          request_list.append(_gadget_data)
    for _request in request_list:
      await rdb_helper.delete_open_streaming_data_info(_request['gid'], _client_id)
      await rdb_helper.delete_open_streaming_data_info(_client_id, _request['gid'])
    if request_list:
      response = await dash_apis.close_stream(request_list, _client_id)
      if isinstance(response, list) and not response:
        return []
      elif isinstance(response, list) and response:
        return response
      else:
        return []
    return []
  except:
    logging.exception("Invalid Parameter. ids: %s", str(ids))


__EP_KEY__ = '''e'''


__EP_MAP__ = {
  'subscribe': _subscribe,
  'get_data': _get_data,
  'unsubscribe': _unsubscribe,
  'update_data': _update_data,
  'get_detected_list': _get_detected_list,
  'open_stream' : _open_stream,
  'close_stream' : _close_stream
}


async def websocket_handler(request):
  logging.info('Websocket connection starting')
  resp = web.WebSocketResponse()
  _client_id = id(resp)
  logging.info("ws-%s preparing...", _client_id)
  await resp.prepare(request)
  logging.info("ws-%s connected...", _client_id)

  try:
    async for msg in resp:
      logging.debug("ws-%s in: %s, %s", _client_id, msg.type, msg.data)
      if msg.type == web.WSMsgType.TEXT:
        _ret = {}
        try:
          _data = json.loads(msg.data)
          logging.debug("ws-%s parsed data: %s", _client_id, _data)
          _ret['i'] = _data['i']
          if __EP_KEY__ not in _data:
            #TODO ERROR INVALID FORMAT
            pass
          _ep_name = _data[__EP_KEY__]
          if _ep_name not in _data:
            #TODO ERROR NOT EXISTS EP
            pass
          _func = __EP_MAP__[_ep_name]
          _kwargs = _data['kwargs'] if 'kwargs' in _data else {}
          _value = await _func(resp, **_kwargs)
          _ret['v'] = _value
        except Exception:
          _ret['v'] = 'error'
          _ret['e'] = _data['e']
          logging.warning("FAILED ", exc_info=True)
        _ret['_t'] = time.time()
        await resp.send_str(json.dumps(_ret))
        logging.debug("ws-%s out: %s", _client_id, _ret)
  except Exception:
    logging.warning("ws-%s Fail to handle", _client_id, exc_info=True)
  finally:
    try:
      if ws_manager.get_all_ws_obj():
        ws_manager.remove_ws_obj(resp, _client_id)
      logging.info("ws-%s disconnected.", _client_id)
      await disconnect_close_stream(resp, _client_id)
    except Exception as ex:
      logging.warn("ws-%s Fail to remove", _client_id, exc_info=True)
  return resp


async def disconnect_close_stream(ws_resp, client_id):
  ids = await rdb_helper.get_open_streaming_data(client_id)
  if ids:
    asyncio.ensure_future(_close_stream(ws_resp, ids))


async def on_shutdown(app):
  for ws in ws_manager.get_all_ws_obj():
    try:
      await ws.close()
    except:
      pass


async def _event_handle(event_data):
  for _data in event_data:
    _topic = _data['topic']
    _value = _data['value']
    _return_body = await event.handle(_topic, _value)


async def event_handle(request):
  _req_data = await request.json()
  asyncio.ensure_future(_event_handle(_req_data))
  return web.Response(body='')


async def _ipcam_refresh_handle(refresh_ip_data):
  await streaming_event.refresh_handle(refresh_ip_data['reopen'])


async def ipcam_refresh_handle(request):
  logging.debug("Handle ipcam refresh start!")
  _req_data = await request.json()
  logging.debug("request : %s", _req_data)
  asyncio.ensure_future(_ipcam_refresh_handle(_req_data))
  return web.Response(body='')


async def _ipcam_sync_handle():
  _ret = await streaming_event.sync_handle()
  return _ret


async def ipcam_sync_handle(request):
  logging.debug("Handle ipcam sync start!")
  _ret = await _ipcam_sync_handle()
  return web.Response(body=json.dumps(_ret))


async def _paserver_event_handle(alarm_data):
  for _data in alarm_data:
    _topic = _data['topic']
    _value = _data['value']
    _return_body = await console_event.update_handle(_topic, _value)


async def paserver_event_handle(request):
  logging.debug("Handle paserver event")
  _req_data = await request.json()
  logging.debug("Request body : %s", _req_data)
  asyncio.ensure_future(_paserver_event_handle(_req_data))
  return web.Response(body='')


async def _workprog_event_handle(workprog_data):
  for _data in workprog_data:
    _topic = _data['topic']
    _value = _data['value']
    _return_body = await workprog_event.update_handle(_topic, _value)


async def workprog_event_handle(request):
  logging.debug("Handle workprog event")
  _req_data = await request.json()
  logging.debug("Request body : %s", _req_data)
  asyncio.ensure_future(_workprog_event_handle(_req_data))
  return web.Response(body='')


async def pa_data_init(req):
  _new_ret = []
  _ret = await rdb_helper.get_all_of_device_data()
  for data in _ret.values():
    if data['kind'] == SPEAKER_KIND:
      _new_ret.append(data)
  return web.Response(body=json.dumps(_new_ret))


def _setup_logging(log_dirpath, log_filename):
  """Setup logging.
  """
  _logger = logging.getLogger()
  if _logger.handlers:
    _logger.removeHandler(_logger.handlers[0])

  if constant.IS_DEV:
    level = logging.DEBUG
  else:
    level = logging.INFO
  _logger.setLevel(level)

  # Some optimizations
  logging.logThreads = 0
  logging.logProcesses = 0

  formatter = logging.Formatter("%(levelname)s\t%(created)f\t"
                                "%(lineno)d\t%(module)s\t"
                                "%(funcName)s\t%(message)s")

  # Rotate
  if not os.path.exists(log_dirpath):
    os.makedirs(log_dirpath)
  log_filepath = os.path.join(log_dirpath, log_filename)
  max_bytes = 10485760   # 10MB
  backup_count = 5
  handler = logging.handlers.RotatingFileHandler(log_filepath,
                                                 maxBytes=max_bytes,
                                                 backupCount=backup_count)
  handler.setFormatter(formatter)
  logging.getLogger().addHandler(handler)

  # Streaming
  shandler = logging.StreamHandler()
  shandler.setFormatter(formatter)
  _logger.addHandler(shandler)


def main():
  loop = asyncio.get_event_loop()
  app = web.Application(loop=loop)
  app.router.add_get('/ws', websocket_handler)
  app.router.add_post('/c_event', event_handle)
  app.router.add_post('/ipcams/stream/refresh', ipcam_refresh_handle)
  app.router.add_get('/ipcams/stream/sync', ipcam_sync_handle)
  app.router.add_get('/pa/data/init', pa_data_init)
  app.router.add_post('/paserver/event', paserver_event_handle)
  app.router.add_post('/work/event', workprog_event_handle)
  app.on_shutdown.append(on_shutdown)
  scheduler.start()
  if constant.IS_DEV:
    web.run_app(app, host="0.0.0.0", port=constant.SERVER_PORT)
  else:
    web.run_app(app, port=constant.SERVER_PORT)


if __name__ == '__main__':
  file_name = 'api_server.log'
  if constant.IS_DEV:
    base_dir = '/tmp'
  else:
    base_dir = os.path.join(os.path.expanduser('~'), 'log')
  _setup_logging(base_dir, file_name)
  main()
