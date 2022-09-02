# Alternate extension

The alternate extension has enhanced syntax for the `Extension` class.

## Status

100% functional, all working well.

## How to use

You can just `client.load("ext")` the extension as normal.

`ext.py`:
```py
from interactions.ext.enhanced import AltExt

ext = AltExt("ExtName")

@ext.command()
async def hello(ctx):
    await ctx.send("Hello!")

# all the extension decorators are in AltExt with the naming style the same as those in Client.

# the setup function is automatically added
```

## [API Reference](./API-Reference#alt-ext)
