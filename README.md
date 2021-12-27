# interactions-better-components
[![PyPI - Downloads](https://img.shields.io/pypi/dm/interactions-better-components?color=blue&style=for-the-badge)](https://pypi.org/project/interactions-better-components/)

Better components for discord-py-interactions

## Installation:
```
pip install -U interactions-better-components
```

---------------------

## What is this library?
This is `interactions-better-components`, a library for `discord-py-interactions` which modifies component callbacks, and adds useful helper functions.

## What does this have?
Listed below are all the features this library currently has:
- Component callbacks are modified so you can enable checking if the `custom_id` of the component starts with the one provided in the decorator
- `ActionRow` function which enables usage of `ActionRow(...)`
- `spread_to_rows` function which allows components to be spread to multiple `ActionRow`s

---------------------

# New component callback
The new component callbacks are modified so you can enable checking if the `custom_id` of the component starts with the one provided in the decorator.

## How to use:
In your bot, you must use this line:
```py
from better_components import setup
...
bot = interactions.Client(...)
setup(bot)
```

Then, you can use the decorator!

If you want to use `interactions-wait-for` with this extension, you must add `use_wait_for=True` to the function.

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
