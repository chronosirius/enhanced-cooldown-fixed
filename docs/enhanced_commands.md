# Enhanced commands

Enhanced commands have the ability to typehint the parameters
of the function instead of specifying them in the decorator.

## Status

100% functional, all working well.

## How to use

To specify options in the parameter, use this syntax:

```py
from interactions import OptionType, Channel
from interactions.ext.enhanced import EnhancedOption, setup_options

@bot.command()
@setup_options
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
from interactions import Role, Channel
from interactions.ext.enhanced import EnhancedOption
from typing_extensions import Annotated

@bot.command()
@setup_options
async def options(
    ctx,
    option1: Annotated[str, EnhancedOption(description="...")],
    option2: Annotated[Role, EnhancedOption(description="...")],
    option3: Annotated[Channel, EnhancedOption(description="...")],
):
    """Says something!"""
    await ctx.send("something")
```

These are all different ways of providing options in the respective parameters.

This will also work for `Extension`s! Use the `extension_command` decorator from this library.

## [API Reference](./API-Reference#enhanced-commands)
