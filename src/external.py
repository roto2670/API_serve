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
import asyncio

import _http
import constant


async def send_detected_data(data):
  if data:
    hub_id = data[0]['hid']
    _equip_data = {
      'hub_id': hub_id,
      'value': data
    }
    _send_url = "{}{}".format(constant.MAIN_SERVER_ADDR,
                              constant.EQUIP_COUNT_URI)
    try:
      asyncio.ensure_future(_http.request(_http.POST, _send_url,
                                          body=json.dumps(_equip_data)))
    except:
      pass


async def send_update_scanner(hub_obj):
  _url = "{}{}".format(constant.MAIN_SERVER_ADDR,
                       constant.UPDATE_SCANNER_URI)
  try:
    asyncio.ensure_future(_http.request(_http.POST, _url,
                                        body=json.dumps(hub_obj)))
  except:
    pass
