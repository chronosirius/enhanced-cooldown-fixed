"""
Credit to @dontbanmeplz for the original code regarding cooldowns, and merging into better-interactions.
"""
from time import time
from functools import wraps
from interactions import CommandContext, User, Guild, Channel


class cooldown:
    def __init__(self, function, cal: function = None, cool: int = 10, typ="user"):
        if typ not in {"user", User, "guild", Guild, "channel", Channel}:
            exit()
        self.function = function
        self.js = {}
        self.cool = cool
        self.cal = cal

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
