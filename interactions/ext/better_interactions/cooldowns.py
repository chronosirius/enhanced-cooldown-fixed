"""
Credit to @dontbanmeplz for the original code regarding cooldowns, and merging into better-interactions.
"""
from functools import wraps
from time import time as _time
from typing import Callable, Coroutine, Optional, Union
from datetime import datetime, timedelta

from interactions import Channel, CommandContext, Guild, User, Member

"""
class cooldown:
    def __init__(
        self,
        function: Optional[Coroutine] = None,
        cal: Optional[Coroutine] = None,
        cool: Optional[Union[float, int]] = 10,
        typ: Optional[Union[str, User, Channel, Guild]] = "user",
    ):
        if typ not in {"user", User, "guild", Guild, "channel", Channel}:
            raise TypeError("Invalid type provided for `typ`!")
        self.function = function
        self.js = {}
        self.cool = cool
        self.cal = cal
        self.typ = typ

    def _clean_timers(self):
        jsondata = [obj for obj in self.js if time() - self.js[obj] >= self.cool]
        self.js = jsondata

    def data(self, ctx):
        typ = self.typ
        js = self.js

        if typ in {"user", User}:
            id = str(ctx.author.user.id)
        elif typ in {"channel", Channel}:
            id = str(ctx.channel.id)
        elif typ in {"guild", Guild}:
            id = str(ctx.guild.id)
        else:
            raise TypeError(f"Invalid type: {typ}")

        data = js.get(id, time())
        if not js.get(id, None):
            js[id] = data
            return (True, data)
        if time() - data < self.cool:
            return (False, data)
        data = time()
        return (True, data)

    def __call__(self, func):
        @wraps(func)
        async def new_func(ctx: CommandContext, *args, **kwargs):
            data = self.data(ctx)
            if data[0]:
                return await func(ctx, *args, **kwargs)
            if self.cal:
                return await self.function(ctx, self.cool - (time() - data[1]))
            await ctx.send("This command is currently on cooldown")
            new_data = filter(lambda attr: attr not in dir(type(func)), dir(func))
            for new_attr in new_data:
                old_attr = getattr(func, new_attr)
                setattr(new_func, new_attr, old_attr)

        return new_func
"""

"""
class cooldown:
    def __init__(
        self,
        time: Optional[Union[float, int]] = 10,
        cooldown_function: Optional[Coroutine] = None,
        type: Optional[Union[str, User, Channel, Guild]] = "user",
    ):
        if type not in {"user", User, "guild", Guild, "channel", Channel}:
            raise TypeError("Invalid type provided for `type`!")

        self.time = time
        self.cooldown_function = cooldown_function
        self.type = type

        self.func = None
        self.json = {}

    def reset_cooldown(self):
        self.json = [obj for obj in self.json if _time() - self.json[obj] >= self.time]

    def cooldown_passed(self, ctx):
        if self.type in {"user", User}:
            id = str(ctx.author.user.id)
        elif self.type in {"channel", Channel}:
            id = str(ctx.channel.id)
        elif self.type in {"guild", Guild}:
            id = str(ctx.guild.id)
        else:
            raise TypeError(f"Invalid type: {self.type}")

        data = self.json.get(id, _time())
        if not self.json.get(id, None):
            self.json[id] = data
            return True, data
        if _time() - data < self.time:
            return False, data
        return True, data

    def __call__(self, func):
        @wraps(func)
        async def new_func(ctx: CommandContext, *args, **kwargs):
            cooled, data = self.cooldown_passed(ctx)
            if cooled:
                return await func(ctx, *args, **kwargs)
            if self.cooldown_function:
                return await self.cooldown_function(ctx, self.time - (_time() - data))
            await ctx.send("This command is currently on cooldown!")
            # new_data = filter(lambda attr: attr not in dir(type(func)), dir(func))
            # for new_attr in new_data:
            #     old_attr = getattr(func, new_attr)
            #     setattr(new_func, new_attr, old_attr)

        self.func = new_func
        return new_func
"""


def get_id(type, ctx):
    if type == "user" or type is User or type == "member" or type is Member:
        return str(ctx.author.user.id)
    elif type == "channel" or type is Channel:
        return str(ctx.channel.id)
    elif type == "guild" or type is Guild:
        return str(ctx.guild.id)


def cooldown(
    *delta_args,
    error: Optional[Coroutine] = None,
    type: Optional[Union[str, User, Channel, Guild]] = "user",
    **delta_kwargs
):
    delta = timedelta(*delta_args, **delta_kwargs)

    def decorator(func):
        last_called: dict = {}
        if type not in {"user", User, "guild", Guild, "channel", Channel}:
            raise TypeError("Invalid type provided for `type`!")

        @wraps(func)
        async def wrapper(ctx, *args, **kwargs):
            nonlocal last_called
            now = datetime.now()
            id = get_id(type, ctx)
            unique_last_called = last_called.get(id, None)

            if unique_last_called and (now - unique_last_called < delta):
                return await error(ctx, delta - (now - unique_last_called))

            last_called[id] = now
            return await func(ctx, *args, **kwargs)

        return wrapper

    return decorator
