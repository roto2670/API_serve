# -*- coding: utf-8 -*-
# Copyright 2019-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


import logging
import aiohttp


GET = 'get'
POST = 'post'
DELETE = 'delete'


async def get(url, headers=None):
  ret = await request(GET, url, headers)
  return ret


async def post(url, headers=None, body=None):
  ret = await request(POST, url, headers, body)
  return ret


async def delete(url, headers=None, body=None):
  ret = await request(DELETE, url, headers, body)
  return ret


def _build_response(status, headers, body):
  _headers = {}
  for _k, _v in headers.items():
    _headers[_k.decode('utf-8')] = _v.decode('utf-8')
  return {'status': status,
          'headers': _headers,
          'body': body}


async def request(method, url, headers=None, body=None, params=None):
  _headers = headers or {}
  logging.debug("Requests:\n#REQ %s\n#REQ url: %s\n#REQ headers: %s\n#REQ body: %s",
                method, url, headers, body)
  async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
    if method == GET:
      async with session.get(url, headers=_headers, params=params) as resp:
        if resp.headers['Content-Type'] == 'application/octet-stream':
          _body = await resp.read()
        else:
          _body = await resp.text()
        _resp = _build_response(resp.status, dict(resp.raw_headers), _body)
    elif method == POST:
      async with session.post(url, headers=_headers, data=body, params=params) as resp:
        _body = await resp.text()
        _resp = _build_response(resp.status, dict(resp.raw_headers), _body)
    elif method == DELETE:
      async with session.delete(url, headers=_headers, params=params) as resp:
        _body = await resp.text()
        _resp = _build_response(resp.status, dict(resp.raw_headers), _body)
  return _resp
