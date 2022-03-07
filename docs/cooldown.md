# Cooldown

Cooldowns are used to set a timer/cooldown/slowmode for a slash command.

They can be set to cooldown for a specific `User`, `Channel`, or `Guild`.

You can specify the amount of time to cooldown for, by specifying microseconds, milliseconds, seconds, minutes, hours, days, and/or weeks

You can also specify an optional coroutine to execute if the command is on cooldown.

## Status

100% functional, all working well.

## How to use

Here is an example of the usage of cooldowns:

```py
async def cooldown_error(ctx, amount):
    await ctx.send(f"You have been ratelimited for {amount} seconds.")

@bot.command(scope=924871439776108544)
@cooldown(seconds=10, error=cooldown_error, type="user")
async def cooldown_10(ctx):
    """Cooldown 10 seconds"""
    await ctx.send("Cooldown 10 seconds")
```

## [API Reference](./api_reference.md)
