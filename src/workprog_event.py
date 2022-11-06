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

import ws_manager

EXPIRED = []
ADD_KIND = '''add'''
UPDATE_KIND = '''update'''
REMOVE_KIND = '''remove'''
FAILED_KIND = '''failed'''

BASEPOINT_EVENT = '''update_basepoint_list'''
TUNNEL_EVENT = '''update_tunnel_list'''
BLAST_EVENT = '''update_blast_list'''
BLAST_INFO_EVENT = '''update_blast_info_list'''
WORK_EVENT = '''update_work_list'''
WORK_HISTORY_EVENT = '''update_work_history_list'''
PAUSE_HISTORY_EVENT = '''update_pause_history_list'''
WORK_EQUIPMENT_EVENT = '''update_work_equipment_list'''
MESSAGE_EVENT = '''update_message_list'''
TEAM_EVENT = '''update_team_list'''
ACTIVITY_EVENT = '''update_activity_list'''
CHARGING_EVENT = '''update_charging_list'''
BLASTING_EVENT = '''update_blasting_list'''


async def _fire_ws_response(ws_obj, data):
  if not ws_obj._closed:
    await ws_obj.send_str(json.dumps(data))
  else:
    logging.warning("cannot send event data")
    EXPIRED.append(ws_obj)


async def _fire_event(event, kind, value):
  _t = time.time()
  _data = {'e': event,
           'kind': kind,
           'v': value,
           '_t': _t}

  _l_wss = ws_manager.get_all_location_ws_obj()
  _w_wss = ws_manager.get_all_workprog_ws_obj()
  logging.info("### l wss : %s", len(_l_wss))
  logging.info("### w wss : %s", len(_w_wss))

  for _ws in _l_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("Failed to send location event data. Kind : %s",
                      kind, exc_info=True)
  for _ws in _w_wss:
    try:
      asyncio.ensure_future(_fire_ws_response(_ws, _data))
    except:
      logging.warning("Failed to send workprog event data. Kind : %s",
                      kind, exc_info=True)
  return ''


async def _handle_base_point_added_event(topic, value):
  asyncio.ensure_future(_fire_event(BASEPOINT_EVENT, ADD_KIND, value))
  return ''


async def _handle_base_point_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(BASEPOINT_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_base_point_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(BASEPOINT_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_tunnel_added_event(topic, value):
  asyncio.ensure_future(_fire_event(TUNNEL_EVENT, ADD_KIND, value))
  return ''


async def _handle_tunnel_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(TUNNEL_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_tunnel_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(TUNNEL_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_blast_added_event(topic, value):
  asyncio.ensure_future(_fire_event(BLAST_EVENT, ADD_KIND, value))
  return ''


async def _handle_blast_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(BLAST_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_blast_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(BLAST_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_blast_info_added_event(topic, value):
  asyncio.ensure_future(_fire_event(BLAST_INFO_EVENT, ADD_KIND, value))
  return ''


async def _handle_blast_info_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(BLAST_INFO_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_blast_info_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(BLAST_INFO_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_work_added_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_EVENT, ADD_KIND, value))
  return ''


async def _handle_work_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_work_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_work_history_added_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_HISTORY_EVENT, ADD_KIND, value))
  return ''


async def _handle_work_history_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_HISTORY_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_work_history_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_HISTORY_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_pause_history_added_event(topic, value):
  asyncio.ensure_future(_fire_event(PAUSE_HISTORY_EVENT, ADD_KIND, value))
  return ''


async def _handle_pause_history_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(PAUSE_HISTORY_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_pause_history_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(PAUSE_HISTORY_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_work_equipment_added_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_EQUIPMENT_EVENT, ADD_KIND, value))
  return ''


async def _handle_work_equipment_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_EQUIPMENT_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_work_equipment_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(WORK_EQUIPMENT_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_message_added_event(topic, value):
  asyncio.ensure_future(_fire_event(MESSAGE_EVENT, ADD_KIND, value))
  return ''


async def _handle_message_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(MESSAGE_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_message_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(MESSAGE_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_team_added_event(topic, value):
  asyncio.ensure_future(_fire_event(TEAM_EVENT, ADD_KIND, value))
  return ''


async def _handle_team_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(TEAM_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_team_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(TEAM_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_activity_added_event(topic, value):
  asyncio.ensure_future(_fire_event(ACTIVITY_EVENT, ADD_KIND, value))
  return ''


async def _handle_activity_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(ACTIVITY_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_activity_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(ACTIVITY_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_charging_added_event(topic, value):
  asyncio.ensure_future(_fire_event(CHARGING_EVENT, ADD_KIND, value))
  return ''


async def _handle_charging_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(CHARGING_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_charging_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(CHARGING_EVENT, UPDATE_KIND, value))
  return ''


async def _handle_blasting_added_event(topic, value):
  asyncio.ensure_future(_fire_event(BLASTING_EVENT, ADD_KIND, value))
  return ''


async def _handle_blasting_removed_event(topic, value):
  asyncio.ensure_future(_fire_event(BLASTING_EVENT, REMOVE_KIND, value))
  return ''


async def _handle_blasting_updated_event(topic, value):
  asyncio.ensure_future(_fire_event(BLASTING_EVENT, UPDATE_KIND, value))
  return ''


FUNC_MAP = {
  'basepoint.added': _handle_base_point_added_event,
  'basepoint.removed': _handle_base_point_removed_event,
  'basepoint.updated': _handle_base_point_updated_event,
  'tunnel.added': _handle_tunnel_added_event,
  'tunnel.removed': _handle_tunnel_removed_event,
  'tunnel.updated': _handle_tunnel_updated_event,
  'blast.added': _handle_blast_added_event,
  'blast.removed': _handle_blast_removed_event,
  'blast.updated': _handle_blast_updated_event,
  'blastinfo.added': _handle_blast_info_added_event,
  'blastinfo.removed': _handle_blast_info_removed_event,
  'blastinfo.updated': _handle_blast_info_updated_event,
  'work.added': _handle_work_added_event,
  'work.removed': _handle_work_removed_event,
  'work.updated': _handle_work_updated_event,
  'workhistory.added': _handle_work_history_added_event,
  'workhistory.removed': _handle_work_history_removed_event,
  'workhistory.updated': _handle_work_history_updated_event,
  'pausehistory.added': _handle_pause_history_added_event,
  'pausehistory.removed': _handle_pause_history_removed_event,
  'pausehistory.updated': _handle_pause_history_updated_event,
  'workequipment.added': _handle_work_equipment_added_event,
  'workequipment.removed': _handle_work_equipment_removed_event,
  'workequipment.updated': _handle_work_equipment_updated_event,
  'message.added': _handle_message_added_event,
  'message.removed': _handle_message_removed_event,
  'message.updated': _handle_message_updated_event,
  'team.added': _handle_team_added_event,
  'team.removed': _handle_team_removed_event,
  'team.updated': _handle_team_updated_event,
  'activity.added': _handle_activity_added_event,
  'activity.removed': _handle_activity_removed_event,
  'activity.updated': _handle_activity_updated_event,
  'charging.added': _handle_charging_added_event,
  'charging.removed': _handle_charging_removed_event,
  'charging.updated': _handle_charging_updated_event,
  'blasting.added': _handle_blasting_added_event,
  'blasting.removed': _handle_blasting_removed_event,
  'blasting.updated': _handle_blasting_updated_event,
}


async def expire_ws():
  logging.info("Expired object length : %s", len(EXPIRED))
  while EXPIRED:
    ws_obj = EXPIRED.pop()
    ws_manager.remove_ws_obj(ws_obj)
    logging.info("Expire ws obj. ID : %s", id(ws_obj))
  logging.info("Remain WS location tracking obj length : %s",
               len(ws_manager.get_all_location_ws_obj()))
  logging.info("Remain WS workprog obj length : %s",
               len(ws_manager.get_all_workprog_ws_obj()))


async def update_handle(topic, value):
  _ret = ''
  logging.info("## From console topic : %s, value : %s", topic, value)
  if topic in FUNC_MAP:
    _func = FUNC_MAP[topic]
    _return_body = await _func(topic, value)
  else:
    logging.debug("Not handle event: %s", topic)
    _ret = '-1'
  return _ret
