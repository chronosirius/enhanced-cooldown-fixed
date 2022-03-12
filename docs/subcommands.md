# Subcommands

Subcommands are technically options for commands, meaning to make subcommands, you may need long chains of options and if/elif/else conditionals.

This library provides a way to make subcommands, similar to subcommands in `discord-py-interactions<=3.0.2`.

Has features from [modified commands](./Enhanced-commands).

## Status

100% working, all working well.

## How to use

Here's some examples of subcommand usage:

```py
# optional
from interactions.ext.enhanced import base
...
# sets up bot.base, optional
bot.load("interactions.ext.enhanced")
...
# create a base command:
the_base = bot.base("the_base", scope=874781880489222154)
# or without loading:
the_base = base(bot, "the_base", scope=874781880489222154)

# create a subcommand with an optional group and required name:
@the_base.subcommand(
    group="the_group",
    name="the_name",
    description="A simple subcommand",
)
async def the_group(
    ctx: interactions.CommandContext,
):
    await ctx.send("1")

# another subcommand in the same group:
@the_base.subcommand(
    group="the_group",
    name="the_name2",
    description="A simple subcommand",
)
async def the_group2(
    ctx: interactions.CommandContext,
):
    await ctx.send("2")

# another subcommand in the same group with some options:
@the_base.subcommand(
    group="the_group",
    name="the_name3",
    description="A simple subcommand",
    options=[
        interactions.Option(
            type=interactions.OptionType.STRING,
            name="the_string",
            description="A string",
            required=True,
        ),
    ],
)
async def the_group3(
    ctx: interactions.CommandContext,
    the_string,
):
    await ctx.send(f"3 {the_string}")

# a subcommand in a different group:
@the_base.subcommand(
    group="the_group2",
    name="the_name4",
    description="A simple subcommand4",
)
async def the_group24(
    ctx: interactions.CommandContext,
):
    await ctx.send("4")

# a subcommand with no group:
@the_base.subcommand(
    name="the_name5",
    description="A simple subcommand5",
)
async def the_name5(
    ctx: interactions.CommandContext,
):
    await ctx.send("5")

# finishes the command:
the_base.finish()
```

This approach that I took is similar to the one in `discord-py-interactions<=3.0.2`, and the least complicated way to do it.

## How to use inside of extensions

``main.py``:

```py
import interactions

bot = interactions.Bot(...)
bot.load("interactions.ext.enhanced")  # optional

...

# load cog before bot.start()
bot.load("cog")

bot.start()
```

``cog.py``:

```py
from interactions.ext.enhanced import (
    ext_subcommand_base,
    EnhancedExtension,
)


class Cog(EnhancedExtension):
    def __init__(self, bot):
        self.bot = bot

    the_base = ext_subcommand_base("the_base", scope=874781880489222154)

    @the_base.subcommand(name="name1", description="subcommand")
    async def b(self, ctx):
        await ctx.send("You used /the_base name1")

    @the_base.subcommand(group="group1", name="name2", description="group subcommand")
    async def c(self, ctx):
        await ctx.send("You used /the_base group1 name2")

    the_base.finish()


def setup(bot):
    return Cog(bot)
```

## [API Reference](./API-Reference#subcommands)
