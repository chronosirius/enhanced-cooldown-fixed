# Enhanced commands

Enhanced commands are modified commands that have a default name and description.

Also, you can typehint the parameters of the function instead of specifying them in the decorator. This feature is compatible with [subcommands](./Subcommands).

## Status

100% functional, all working well.

## How to use

In your bot, you must use this line:

```py
bot = interactions.Client(...)
bot.load("interactions.ext.enhanced")
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
from interactions.ext.enhanced import EnhancedOption

@bot.command()
async def options(
    ctx,
    option1: EnhancedOption(str, "option description"),
    option2: EnhancedOption(OptionType.MENTIONABLE, "option description"),
    option3: EnhancedOption(Channel, "option description"),
):
    """Says something!"""
    await ctx.send("something")
```

Another, more IDE friendly, and recommended way is to use `typing_extensions.Annotated`:

```py
from interactions import OptionType, Channel
from interactions.ext.enhanced import EnhancedOption
from typing_extensions import Annotated

@bot.command()
async def options(
    ctx,
    option1: Annotated[str, EnhancedOption(description="...")],
    option2: Annotated[OptionType.MENTIONABLE, EnhancedOption(description="...")],
    option3: Annotated[Channel, EnhancedOption(description="...")],
):
    """Says something!"""
    await ctx.send("something")
```

These are all different ways of providing options in the respective parameters.

This will also work for `Extension`s! Use the `extension_command` decorator from this library.

### Debug scope

Tired of specifying the scope of the command? Use the `debug_scope` keyword argument when loading the extension.

Specify it with the scope you want to use.

```py
bot.load("interactions.ext.enhanced", debug_scope=...)
```

If you don't want it to affect a command, add `debug_scope=False` to the command decorator.

## [API Reference](./API-Reference#enhanced-commands)
