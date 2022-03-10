# Better callbacks

Better callbacks are modified callbacks that let you use the ability to add more in the `custom_id`.

There are 2 callbacks:

1. Component callback
2. Modal callback

The purpose of callbacks is so you can interact with multiple `custom_id`s, instead of the one specified.

You can either use `startswith` and see if the`custom_id` starts with the specified string, or use `regex` and see if the `custom_id` matches a regex provided.

## Status

100% functional, all working well.

## How to use

In your bot, you must use this line:

```py
bot = interactions.Client(...)
bot.load("interactions.ext.better_interactions")
```

Then, you can do stuff like this:

Example component callback that uses `startswith`:

```py
@bot.component("test", startswith=True)
async def test(ctx):
    await ctx.send("test")
```

Examples of `custom_ids` that will invoke this callback:

1. `test`
2. `test_1`
3. `testa`
4. `testuwah9d8wha9jf9wf*(&W(&F))`

Examples of `custom_ids` that will not invoke this callback:

1. `TEST`
2. `TeSt`
3. `tesst`
4. `_test`

etc.

Example modal callback that uses regex:

```py
@bot.modal(r"^[a-z0-9_-]{1,32}$", regex=True)
async def modal(ctx, ...):
    await ctx.send("modal")
```

Examples of `custom_ids` that will invoke this callback and match the regex provided:

1. `test`
2. `test_1`
3. `testa`
4. `yoo-_123`

Examples of `custom_ids` that will not invoke this callback:

1. `TEST`
2. `TeSt`
3. `test!@#`
4. `testuwah9d8wha9jf9wf*(&W(&F))`

The `startswith` and `regex` can be used in both component and modal callbacks, but only one can be specified per callback, not both.

## [API Reference](./api_reference.md#better-callbacks)
