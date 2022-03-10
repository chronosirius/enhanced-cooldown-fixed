# Better commands

Better commands are modified commands that have a default name and description.

Also, you can typehint the parameters of the function instead of specifying them in the decorator. This feature is compatible with [subcommands](./subcommands.md).

## Status

100% functional, all working well.

## How to use

In your bot, you must use this line:

```py
bot = interactions.Client(...)
bot.load("interactions.ext.better_interactions")
```

Then, you can do stuff like this:

```py
@bot.command()
async def ping(ctx):
    """Says pong!"""
    await ctx.send("pong")
```

The default name in this case is `ping`, and the default description is `Says pong!`.

The function name is the default name, while the docstring is the default description.

To specify options in the parameter, use this syntax:

```py
from interactions import OptionType, Channel
from interactions.ext.better_interactions import BetterOption

@bot.command()
async def options(
    ctx,
    option1: BetterOption(str, "option description"),
    option2: BetterOption(OptionType.MENTIONABLE, "option description"),
    option3: BetterOption(Channel, "option description"),
):
    """Says something!"""
    await ctx.send("something")
```

Another, more IDE friendly, and recommended way is to use `typing_extensions.Annotated`:

```py
from interactions import OptionType, Channel
from interactions.ext.better_interactions import BetterOption
from typing_extensions import Annotated

@bot.command()
async def options(
    ctx,
    option1: Annotated[str, BetterOption(description="...")],
    option2: Annotated[OptionType.MENTIONABLE, BetterOption(description="...")],
    option3: Annotated[Channel, BetterOption(description="...")],
):
    """Says something!"""
    await ctx.send("something")
```

These are all different ways of providing options in the respective parameters.

This will also work for `Extension`s! Use the `extension_command` decorator from this library.

## [API Reference](./api_reference.md)
