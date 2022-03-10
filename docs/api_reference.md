# API Reference

## Table of Contents

* [API Reference](#api-reference)
* [Table of Contents](#table-of-contents)
* [Subcommands](#subcommands)
  * [SubcommandSetup](#class-subcommandsetup)
    * [subcommand](#func-subcommand)
    * [finish](#func-finish)
  * [ExternalSubcommandSetup](#class-externalsubcommandsetup)
    * [subcommand](#func-subcommand-same-as-subcommandsetup)
    * [finish](#func-finish-same-as-subcommandsetup)
  * [subcommand_base](#func-subcommandbase)
  * [ext_subcommand_base](#func-extsubcommandbase)
* [Better commands](#better-commands)
  * [command](#func-command)
  * [extension_command](#func-extension_command)
  * [autodefer](#func-autodefer)
* [Better components](#better-components)
  * [ActionRow](#func-actionrow)
  * [Button](#func-button)
  * [SelectOption](#func-selectoption)
  * [SelectMenu](#func-selectmenu)
  * [TextInput](#func-textinput)
  * [Modal](#func-modal)
  * [spread_to_rows](#func-spread_to_rows)
* [Better callbacks](#better-callbacks)
  * [component](#func-component)
  * [modal](#func-modal-callback)
  * [extension_component](#func-extension_component)
  * [extension_modal](#func-extension_modal)
* [Cooldown](#cooldown)
  * [cooldown](#func-cooldown)

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
* `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.

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

* `*args: tuple[Button | SelectMenu | TextInput]`: The components to add to the `ActionRow`.

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
button = Button(1, "1", custom_id="1", ...)
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

### *func* `SelectOption`

<ul>

A helper function that passes arguments to `SelectOption`.

Before:

```py
option = SelectOption(label="1", value="1", ...)
```

Now:

```py
option = SelectOption("1", "1", ...)
```

Parameters:

* `label: str`: The label of the option.
* `value: str`: The value of the option.
* `?description: str`: The description of the option.
* `?emoji: Emoji`: The emoji of the option.
* `?disabled: bool`: Whether the option is disabled. Defaults to `False`.

Returns:

`SelectOption`

</ul>

### *func* `SelectMenu`

<ul>

A helper function that passes arguments to `SelectMenu`.

Previous:

```py
select = SelectMenu(custom_id="s", options=[...], ...)
```

Now:

```py
select = SelectMenu("s", [...], ...)
```

Parameters:

* `custom_id: str`: The custom id of the select menu.
* `options: list[SelectOption]`: The options of the select menu.
* `?placeholder: str`: The placeholder of the select menu.
* `?min_values: int`: The minimum number of values that can be selected.
* `?max_values: int`: The maximum number of values that can be selected.
* `?disabled: bool`: Whether the select menu is disabled. Defaults to `False`.

Returns:

`SelectMenu`

</ul>

### *func* `TextInput`

<ul>

A helper function that passes arguments to `TextInput`.

Before:

```py
ti = TextInput(custom_id="ti", label="ti", style=1, ...)
```

Now:

```py
ti = TextInput("ti", "ti", 1, ...)
```

Parameters:

* `custom_id: str`: The custom id of the text input.
* `label: str`: The label of the text input.
* `?style: TextInputStyle | int`: The style of the text input.
* `?value: str`: The value of the text input.
* `?required: bool`: Whether the text input is required. Defaults to `True`.
* `?placeholder: str`: The placeholder of the text input.
* `?min_length: int`: The minimum length of the text input.
* `?max_length: int`: The maximum length of the text input.

Returns:

`TextInput`

</ul>

### *func* `Modal`

<ul>

A helper function that passes arguments to `Modal`.

Before:

```py
modal = Modal(custom_id="modal", title="Modal", components=[...])
```

Now:

```py
modal = Modal("modal", "Modal", [...])
```

Parameters:

* `custom_id: str`: The custom id of the modal.
* `title: str`: The title of the modal.
* `components: list[TextInput]`: The components of the modal.

Returns:

`Modal`

</ul>

### *func* spread_to_rows

<ul>

A helper function that spreads your components into `ActionRow`s of a set size.

```py
rows = spread_to_rows(..., max_in_row=...)
```

Parameters:

* `*components: tuple[ActionRow | Button | SelectMenu]`: The components to spread, use `None` to explicit start a new row.
* `?max_in_row: int`: The maximum number of components in a row. Defaults to `5`.

Returns:

`list[ActionRow]`

</ul>

## Better callbacks

### *func* `component`

<ul>

A modified decorator that allows you to add more information to the `custom_id` and use `startswith` or `regex` to invoke the callback.

```py
bot.load("interactions.ext.better_interactions")

# startswith:
@bot.component("test", startswith=True)
async def test(ctx):
    ...

# regex:
@bot.component(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(ctx):
    ...
```

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `component: str | Button | SelectMenu`: The component custom_id or regex to listen to.
* `startswith: bool`: Whether the component custom_id should start with the given string. Defaults to `False`.
* `regex: bool`: Whether the component custom_id should match the given regex. Defaults to `False`.

</ul>

### *func* `modal` (callback)

<ul>

A modified decorator that allows you to add more information to the `custom_id` and use `startswith` or `regex` to invoke the callback.

```py
bot.load("interactions.ext.better_interactions")

# startswith:
@bot.modal("test", startswith=True)
async def test(ctx):
    ...

# regex:
@bot.modal(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(ctx):
    ...
```

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `modal: str | Modal`: The modal custom_id or regex to listen to.
* `startswith: bool`: Whether the modal custom_id should start with the given string. Defaults to `False`.
* `regex: bool`: Whether the modal custom_id should match the given regex. Defaults to `False`.

</ul>

### *func* `extension_component`

<ul>

A modified decorator that allows you to add more information to the `custom_id` and use `startswith` or `regex` to invoke the callback inside of `Extension`s.

```py
# main.py:
bot.load("interactions.ext.better_interactions")

# startswith:
@extension_component("test", startswith=True)
async def test(self, ctx):
    ...

# regex:
@extension_component(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(self, ctx):
    ...
```

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `component: str | Button | SelectMenu`: The component custom_id or regex to listen to.
* `startswith: bool`: Whether the component custom_id should start with the given string. Defaults to `False`.
* `regex: bool`: Whether the component custom_id should match the given regex. Defaults to `False`.

</ul>

### *func* `extension_modal`

<ul>

A modified decorator that allows you to add more information to the `custom_id` and use `startswith` or `regex` to invoke the callback inside of `Extension`s.

```py
# main.py:
bot.load("interactions.ext.better_interactions")

# startswith:
@extension_modal("test", startswith=True)
async def test(self, ctx):
    ...

# regex:
@extension_modal(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(self, ctx):
    ...
```

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `modal: str | Modal`: The modal custom_id or regex to listen to.
* `startswith: bool`: Whether the modal custom_id should start with the given string. Defaults to `False`.
* `regex: bool`: Whether the modal custom_id should match the given regex. Defaults to `False`.

</ul>

## Cooldown

### *func* `cooldown`

<ul>

A decorator for handling cooldowns.

Parameters for `datetime.timedelta` are `days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0`.

```py
from interactions.ext.better_interactions import cooldown

async def cooldown_error(ctx, delta):
    ...

@client.command(...)
@cooldown(seconds=..., ..., error=cooldown_error, type=...)
async def cooldown_command(ctx, ...):
    ...
```

Parameters:

* `*delta_args: tuple[datetime.timedelta arguments]`: The arguments to pass to `datetime.timedelta`.
* `?error: Coroutine`: The function to call if the user is on cooldown. Defaults to `None`.
* `?type: str | User | Channel | Guild`: The type of cooldown. Defaults to `None`.
* `**delta_kwargs: dict[datetime.timedelta arguments]`: The keyword arguments to pass to `datetime.timedelta`.

</ul>
