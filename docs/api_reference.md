# API Reference

## Subcommands

### *class* `SubcommandSetup`

<ul>

A class you get when using `base_var = client.base("base_name", ...)`

Use this class to create subcommands by using the `@base_name.subcommand(...)` decorator.

Parameters:

* `(?)client: Client`: The client that the subcommand belongs to. *Not required if you load the extension.*
* `base: str`: The base name of the subcommand.
* `?description: str`: The description of the subcommand. Defaults to `"No description"`.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
* `?default_permission: bool`: The default permission of the subcommand.

Methods:

<ul>

#### *func* `subcommand`

<ul>

Decorator that creates a subcommand for the corresponding base.

`name` is required.

```py
@base_var.subcommand(
    group="group_name",
    name="subcommand_name",
    description="subcommand_description",
    options=[...]
)
```

Parameters:

* `?group: str`: The group of the subcommand.
* `name: str`: The name of the subcommand.
* `?description: str`: The description of the subcommand.
* `?options: list[Option]`: The options of the subcommand.

</ul>

#### *func* `finish`

<ul>

Function that finishes the setup of the base command.

Use this when you are done creating subcommands for a specified base.

```py
base_var.finish()
```

</ul>

</ul>

</ul>

### *class* `ExternalSubcommandSetup`

<ul>

A class you get when using `base_var = extension_base("base_name", ...)`

Use this class to create subcommands by using the `@base_name.subcommand(...)` decorator.

Parameters:

* `base: str`: The base name of the subcommand.
* `?description: str`: The description of the subcommand.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
* `?default_permission: bool`: The default permission of the subcommand.

Methods:

<ul>

#### *func* `subcommand` (same as `SubcommandSetup`)

<ul>

Decorator that creates a subcommand for the corresponding base.

`name` is required.

```py
@base_var.subcommand(
    group="group_name",
    name="subcommand_name",
    description="subcommand_description",
    options=[...]
)
```

Parameters:

* `?group: str`: The group of the subcommand.
* `name: str`: The name of the subcommand.
* `?description: str`: The description of the subcommand.
* `?options: list[Option]`: The options of the subcommand.

</ul>

#### *func* `finish` (same as `SubcommandSetup`)

<ul>

Function that finishes the setup of the base command.

Use this when you are done creating subcommands for a specified base.

```py
base_var.finish()
```

</ul>

</ul>

</ul>

### *func* `subcommand_base`

<ul>

Use this function to initialize a base for future subcommands.

Kwargs are optional.

To use this function without loading the extension, pass in the client as the first argument.

```py
base_name = client.base(
    "base_name",
    description="Description of the base",
    scope=123456789,
    default_permission=True
)
# or
from interactions.ext.better_interactions import subcommand_base
base_name = subcommand_base(
    client,
    "base_name",
    description="Description of the base",
    scope=123456789,
    default_permission=True
)
```

Parameters:

* `(?)self: Client`: The client that the base belongs to. *Not needed if you load the extension and use `client.base(...)`.*
* `base: str`: The base name of the base.
* `?description: str`: The description of the base.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
* `?default_permission: bool`: The default permission of the base.

</ul>

### *func* `ext_subcommand_base`

<ul>

Use this function to initialize a base for future subcommands inside extensions.

Kwargs are optional.

```py
base_name = ext_subcommand_base(
    "base_name",
    description="Description of the base",
    scope=123456789,
    default_permission=True
)
```

Parameters:

* `base: str`: The base name of the base.
* `?description: str`: The description of the base.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
* `?default_permission: bool`: The default permission of the base.

</ul>

## Better commands

### *func* command

<ul>

A modified decorator for creating slash commands.

Makes `name` and `description` optional, and adds ability to use `BetterOption`s.

Full-blown example:

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

Parameters:

* `?type: int | ApplicationCommandType`: The type of application command. Defaults to `ApplicationCommandType.CHAT_INPUT`.
* `?name: str`: The name of the command. Defaults to function name.
* `?description: str`: The description of the command. Defaults to function docstring or `"No description"`.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the command.
* `?options: list[Option]`: The options of the command.
* `?default_permission: bool`: The default permission of the command.

</ul>

### *func* `extension_command`

<ul>

A modified decorator for creating slash commands inside `Extension`s.

Makes `name` and `description` optional, and adds ability to use `BetterOption`s.

Same parameters as `interactions.ext.better_interactions.command`.

</ul>

### *func* `autodefer`

<ul>

Set up a command to be automatically deferred after some time.

Note: This will not work if blocking code is used (such as the requests module).

Usage:

```py
@bot.command(...)
@autodefer(...)
async def foo(ctx, ...):
    ...
```

Parameters:

* `?delay: float | int`: How long to wait before deferring in seconds. Defaults to `2`.
* `?ephemeral: bool`: If the command should be deferred hidden. Defaults to `False`.
* `?edit_origin: bool`: If the command should be deferred with the origin message. Defaults to `False`.

</ul>

## Better components

### *func* `ActionRow`

<ul>

A helper function that passes arguments to `ActionRow`.

Previous:

```py
row = ActionRow(components=[...])
```

Now:

```py
row = ActionRow(...)
```

Parameters:

* `*args: tuple(Button | SelectMenu | TextInput)`: The components to add to the `ActionRow`.

Returns:

`ActionRow`

</ul>

### *func* `Button`

<ul>

A helper function that passes arguments to `Button`.

Previous:

```py
button = Button(style=1, label="1", custom_id="1", ...)
```

Now:

```py
row = ActionRow(1, "1", custom_id="1", ...)
```

Parameters:

* `style: ButtonStyle | int`: The style of the button.
* `label: str`: The label of the button.
* `(?)custom_id: str`: The custom id of the button. *Required if the button is not a `ButtonStyle.LINK`.*
* `(?)url: str`: The URL of the button. *Required if the button is a `ButtonStyle.LINK`.*
* `?emoji: Emoji`: The emoji of the button.
* `?disabled: bool`: Whether the button is disabled. Defaults to `False`.

Returns:

`Button`

</ul>

### *func* `SelectMenu`

<ul>

A helper function that passes arguments to `SelectMenu`.

Parame

</ul>
