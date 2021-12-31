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
- Component callbacks are modified so you can enable checking if the `custom_id` of the component starts with the one provided in the decorator
- `ActionRow` function which enables usage of `ActionRow(...)`
- Component functions for `Button` and `SelectMenu` that has checks so you never have to incorrectly use `Button(...)` or `SelectMenu(...)`
- `spread_to_rows` function which allows components to be spread to multiple `ActionRow`s
- `subcommand` decorator which allows you to create subcommands

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
