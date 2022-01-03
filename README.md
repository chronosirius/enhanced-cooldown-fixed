# better-interactions
[![Discord](https://img.shields.io/discord/924871439776108544?color=blue&label=discord&style=for-the-badge)](https://discord.gg/Y78bpT5aNv) [![PyPI - Downloads](https://img.shields.io/pypi/dm/interactions-better-components?color=blue&style=for-the-badge)](https://pypi.org/project/better-interactions/)

Better interactions for discord-py-interactions

## Installation:
```
pip install -U better-interactions
```

---------------------

## What is this library?
This is `better-interactions`, a library for `discord-py-interactions` which modifies component callbacks, and adds useful helper functions.

## What does this have?
Listed below are all the features this library currently has:
- Subcommands that you can create easily
- Component callbacks are modified so you can enable checking if the `custom_id` of the component starts with the one provided in the decorator
- `ActionRow` function which enables usage of `ActionRow(...)`
- Component functions for `Button` and `SelectMenu` that has checks so you never have to incorrectly use `Button(...)` or `SelectMenu(...)`
- `spread_to_rows` function which allows components to be spread to multiple `ActionRow`s

---------------------

# subcommand
Subcommands are technically options for commands, meaning to make subcommands, you may need long chains of options and if/elif/else conditionals.

This library provides a way to make subcommands, similar to subcommands in `discord-py-interactions<=3.0.2`.

## How to use:
Here's some examples of subcommand usage:
```py
from interactions.ext.better_interactions import setup
...
# sets up bot.base
setup(bot)
...
# create a base command:
the_base = bot.base("the_base", scope=874781880489222154)

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

# anotehr subcommand in the same group with some options:
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

---------------------

# New component callback
The new component callbacks are modified so you can enable checking if the `custom_id` of the component starts with the one provided in the decorator.

## How to use:
In your bot, you must use this line:
```py
from interactions.ext.better_interactions import setup
...
bot = interactions.Client(...)
setup(bot)
```

Then, you can use the decorator!

If you want to use `interactions-wait-for` with this extension, you must add its respective keyword arguments into the setup function as well.

Below is an example of a component callback.
```py
@bot.component("test", startswith=True)
async def startswith_custom_id(ctx):
    await ctx.send(ctx.data.custom_id)
```

The `startswith=True` keyword argument is optional, and if it is not provided, it will default to `False` and will be used like the normal component callbacks.

If you want to check if the `custom_id` of the component starts with the one provided in the decorator, you can use the `startswith=True` keyword argument.

By setting `startswith=True`, the component callback now fires when the `custom_id` of the component starts with the one provided in the decorator.

For example, if you have a component with a `custom_id` of `"test"`, and you set `startswith=True`, the component callback will fire when the `custom_id` of the component starts with `"test"`.

Let's say a button with `custom_id` of `"test1"` is clicked. Since it starts with `"test"`, the component callback will fire.

However, if something like `"tes"` is clicked, the component callback will not fire.

To sum it up, the component callback will fire when the `custom_id` of the component starts with the one provided in the decorator.

## Why should I use this?
This is useful if you want to check if the `custom_id` of the component starts with the one provided in the decorator. In `discord-py-interactions`, the component callbacks are only fired when they are the exact same `custom_id` as the one provided in the decorator. This is not that useful, since you waste a lot of data you could have stored in the component custom IDs. The callbacks provided from `interactions-better-components` fix the aforementioned issue.

---------------------

# ActionRow function
The `ActionRow` function enables usage of `ActionRow(...)` instead of `ActionRow(components=[...])`.

## How to use:
Below is an example of `ActionRow` usage:
```py
@bot.command(
    name="test", description="Test command",
)
async def test(ctx):
    await ctx.send("test", components=[
        ActionRow(select1),
        ActionRow(button1, button2, button3),
    ]
)
```

## Why should I use this?
This is only for aesthetics, making the code look cleaner. Using `ActionRow(...)` is the same as using `ActionRow(components=[...])`, however, it is more readable.

---------------------

# Button and SelectMenu
The `Button` and `SelectMenu` functions are made so you never have to incorrectly use `Button(...)` or `SelectMenu(...)`.

## How to use:
Below is an example of `Button` usage:
```py
from interactions.ext.better_interactions import Button

@bot.command(
    name="test", description="Test command",
)
async def test(ctx):
    await ctx.send("test", components=[
        Button(
            style=1,
            custom_id="test1",
            label="Test 1",
        ),
    ]
)
```
You can import `Button` and `SelectMenu` from `better_interactions` and use them like you would use `Button(...)` and `SelectMenu(...)` from `discord-py-interactions`.

---------------------

# spread_to_rows function
The `spread_to_rows` function allows components to be spread to multiple `ActionRow`s with an optional `max_in_row` argument.

## How to use:
You use the function like this: `spread_to_rows(*components, max_in_row=3)`.

`max_in_row=5` by default.

Separate components by `None` to explicitly start a new row.

Below is an example of `spread_to_rows` usage that spreads components to 2 `ActionRow`s with 5 components each:
```py
@bot.command(
    name="test", description="Test command",
)
async def test(ctx):
    await ctx.send("test", components=spread_to_rows(
        button1, button2, button3, button4, button5, button6, button7, button8, button9, button10,
    )
)
```

---------------------

# subcommand
The `subcommand` function is a decorator that allows you to create a subcommand easily.

## How to use:
Here's 3 examples of subcommand usage:
```py
from interactions.ext.better_interactions import setup
...
setup(bot)
...
# subcommand with 3 terms: `/base subcommand_group subcommand`
@bot.subcommand(
    base="base",
    subcommand_group="subcommand_group",
    name="subcommand",
    description="subcommand description",
)
async def subcommand_with_group(ctx):
    await ctx.send("subcommand with group")

# subcommand with 2 terms: `/base subcommand`
@bot.subcommand(
    base="base",
    name="subcommand",
    description="subcommand description",
)
async def just_subcommand(ctx):
    await ctx.send("just subcommand")

# subcommand with options:
@bot.subcommand(
    base="base",
    subcommand_group="subcommand_group",
    name="subcommand",
    description="subcommand description",
    options=[
        Option(
            name="option",
            description="option description",
        ),
    ]
)
async def subcommand_with_options(ctx, option):
    await ctx.send("subcommand with options")
```
