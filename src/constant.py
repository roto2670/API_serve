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


# API Server (self)
IS_DEV = True
SERVER_PORT = 5555

BEACON_KIND = 'mibsskec'
NEW_BEACON_KIND = 'mibs00001'
HUB_KIND = 'hub'
IPCAM_KIND = 'ipcam'
SPEAKER_KIND = 'speaker'
ROUTER_KIND = 'router'

WS_LOCATION_KIND = 'L'
WS_MOI_KIND = 'M'
WS_SPEAKER_KIND = 'P'
WS_WORK_KIND = 'W'


# Main Operation System
MAIN_SERVER_ADDR = 'http://127.0.0.1:5000'

EQUIP_COUNT_URI = '/internal/set/equip_count'
UPDATE_SCANNER_URI = '/internal/scanner/update'


# REDIS
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
GADGETS_REDIS_DB = 1
DATA_INFO_EXPIRE_REDIS_DB = 4
STREAMING_REDIS_DB = 5
GADGET_COUNT_LIST_EXPIRE_REDIS_DB = 6


# Cloud URL
if IS_DEV:
  THIRD_BASE_URL = 'http://192.168.0.14/v1/'
  BASE_URL = 'http://192.168.0.14/i/v1/'
  PA_URL = 'https://192.168.0.50:5561/'
  SCANNER_KIND = 'com.thenaran.skec'
else:
  THIRD_BASE_URL = 'http://172.16.5.4/v1/'
  BASE_URL = 'http://172.16.5.4/i/v1/'
  PA_URL = 'https://172.16.5.6:5561/'
  SCANNER_KIND = 'com.thenaran.skec'


# Streaming Server URL
if IS_DEV:
  STREAM_BASE_URL = 'http://192.168.1.47:5557'
else:
  STREAM_BASE_URL = 'http://172.16.5.5:5557'


# Error Code
IPCAM_DISCONNECT = 1
OPEN_PROCESS_ERROR = 2
STREAM_SERVER_DISCONNECT = 3
IPCAM_TOO_MANY_USER = 4
BAD_REQUEST = 5


# Ping Code
CONNECT_CODE = 0
STATUS_OFF = 0
STATUS_ON = 1
