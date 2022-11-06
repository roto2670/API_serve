# -*- coding: utf-8 -*-
# Copyright 2019-2020 Naran Inc. All rights reserved.
#  __    _ _______ ______   _______ __    _
# |  |  | |   _   |    _ | |   _   |  |  | |
# |   |_| |  |_|  |   | || |  |_|  |   |_| |
# |       |       |   |_||_|       |       |
# |  _    |       |    __  |       |  _    |
# | | |   |   _   |   |  | |   _   | | |   |
# |_|  |__|__| |__|___|  |_|__| |__|_|  |__|


import asyncio


def run_async(func, *args):
  async def _do(fn, _args):
    ret = await asyncio.get_event_loop().run_in_executor(
          None, fn, *_args)
    return ret
  return asyncio.ensure_future(_do(func, args))
