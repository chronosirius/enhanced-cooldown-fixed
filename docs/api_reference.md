# API Reference

## Extensions

### *class* `EnhancedExtension`

<ul>

Enables modified external commands, subcommands, callbacks, and more.

Use this class instead of `Extension` when using extensions.

```py
# extension.py
from interactions.ext.enhanced import EnhancedExtension

class Example(EnhancedExtension):
    ...

def setup(client):
    Example(client)
```

</ul>

### *class* `Enhanced`

<ul>

This is the core of this library, initialized when loading the extension.

It applies hooks to the client for additional and modified features.

```py
# main.py
client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
```

<ul>

Parameters:

* `(?)client: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
* `?debug_scope: int | Guild | list[int] | list[Guild]`: The debug scope to apply to global commands.
* `?add_subcommand: bool`: Whether to add subcommand hooks to the client. Defaults to `True`.
* `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.
* `?modify_command: bool`: Whether to modify the command decorator. Defaults to `True`.

</ul>

</ul>

## Subcommands

### *class* `Subcommand`

<ul>

A class that represents a subcommand.

DO NOT INITIALIZE THIS CLASS DIRECTLY.

Parameters:

* `name: str`: The name of the subcommand.
* `description: str`: The description of the subcommand.
* `coro: Coroutine`: The coroutine to run when the subcommand is called.
* `options: dict`: The options of the subcommand.

Attributes other than above:

* `_options: Option`: The subcommand as an `Option`.

</ul>

### *class* `Group`

<ul>

A class that represents a subcommand group.

DO NOT INITIALIZE THIS CLASS DIRECTLY.

Parameters:

* `group: str`: The name of the subcommand group.
* `description: str`: The description of the subcommand group.
* `subcommand: Subcommand`: The initial subcommand in the group.

Properties:

* `_options: Option`: The subcommand group as an `Option`.

</ul>

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
* `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.

Methods:

<ul>

#### *func* `subcommand`

<ul>

Decorator that creates a subcommand for the corresponding base.

`name` is required.

</ul>

```py
@base_var.subcommand(
    group="group_name",
    name="subcommand_name",
    description="subcommand_description",
    options=[...]
)
```

<ul>

<ul>

<ul>

Parameters:

* `?group: str`: The group of the subcommand.
* `name: str`: The name of the subcommand.
* `?description: str`: The description of the subcommand.
* `?options: list[Option]`: The options of the subcommand.

</ul>

</ul>

</ul>

<ul>

<ul>

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

</ul>

```py
@base_var.subcommand(
    group="group_name",
    name="subcommand_name",
    description="subcommand_description",
    options=[...]
)
```

<ul>

<ul>

<ul>

Parameters:

* `?group: str`: The group of the subcommand.
* `name: str`: The name of the subcommand.
* `?description: str`: The description of the subcommand.
* `?options: list[Option]`: The options of the subcommand.

</ul>

</ul>

</ul>

<ul>

<ul>

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
from interactions.ext.enhanced import subcommand_base
base_name = subcommand_base(
    client,
    "base_name",
    description="Description of the base",
    scope=123456789,
    default_permission=True
)
```

<ul>

Parameters:

* `(?)self: Client`: The client that the base belongs to. *Not needed if you load the extension and use `client.base(...)`.*
* `base: str`: The base name of the base.
* `?description: str`: The description of the base.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
* `?default_permission: bool`: The default permission of the base.
* `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.

</ul>

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

<ul>

Parameters:

* `base: str`: The base name of the base.
* `?description: str`: The description of the base.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
* `?default_permission: bool`: The default permission of the base.

</ul>

</ul>

## Enhanced commands

### *func* command

<ul>

A modified decorator for creating slash commands.

Makes `name` and `description` optional, and adds ability to use `EnhancedOption`s.

Full-blown example:

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

<ul>

Parameters:

* `?type: int | ApplicationCommandType`: The type of application command. Defaults to `ApplicationCommandType.CHAT_INPUT`.
* `?name: str`: The name of the command. Defaults to function name.
* `?description: str`: The description of the command. Defaults to function docstring or `"No description"`.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the command.
* `?options: list[Option]`: The options of the command.
* `?default_permission: bool`: The default permission of the command.
* `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.

</ul>

</ul>

### *func* `extension_command`

<ul>

A modified decorator for creating slash commands inside `Extension`s.

Makes `name` and `description` optional, and adds ability to use `EnhancedOption`s.

Same parameters as `interactions.ext.enhanced.command`.

Parameters:

* `?type: int | ApplicationCommandType`: The type of application command. Defaults to `ApplicationCommandType.CHAT_INPUT`.
* `?name: str`: The name of the command. Defaults to function name.
* `?description: str`: The description of the command. Defaults to function docstring or `"No description"`.
* `?scope: int | Guild | list[int] | list[Guild]`: The scope of the command.
* `?options: list[Option]`: The options of the command.
* `?default_permission: bool`: The default permission of the command.
* `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.

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

<ul>

Parameters:

* `?delay: float | int`: How long to wait before deferring in seconds. Defaults to `2`.
* `?ephemeral: bool`: If the command should be deferred hidden. Defaults to `False`.
* `?edit_origin: bool`: If the command should be deferred with the origin message. Defaults to `False`.

</ul>

</ul>

### *class* `EnhancedOption`

<ul>

An alternative way of providing options by typehinting.

Basic example:

</ul>

```py
@bot.command(...)
async def command(ctx, name: EnhancedOption(int, "description") = 5):
    ...
```

<ul>

Full-blown example:

</ul>

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

<ul>

Parameters:

* `?type: type | int | OptionType`: The type of the option.
* `?description: str`: The description of the option. Defaults to the docstring or `"No description"`.
* `?name: str`: The name of the option. Defaults to the argument name.
* `?choices: list[Choice]`: The choices of the option.
* `?channel_types: list[ChannelType]`: The channel types of the option. *Only used if the option type is a channel.*
* `?min_value: int`: The minimum value of the option. *Only used if the option type is a number or integer.*
* `?max_value: int`: The maximum value of the option. *Only used if the option type is a number or integer.*
* `?autocomplete: bool`: If the option should be autocompleted.
* `?focused: bool`: If the option should be focused.
* `?value: str`: The value of the option.

</ul>

## Enhanced components

### *func* `ActionRow`

<ul>

A helper function that passes arguments to `ActionRow`.

Previous:

</ul>

```py
row = ActionRow(components=[...])
```

<ul>

Now:

</ul>

```py
row = ActionRow(...)
```

<ul>

Parameters:

* `*args: tuple[Button | SelectMenu | TextInput]`: The components to add to the `ActionRow`.

Returns:

`ActionRow`

</ul>

### *func* `Button`

<ul>

A helper function that passes arguments to `Button`.

Previous:

</ul>

```py
button = Button(style=1, label="1", custom_id="1", ...)
```

<ul>

Now:

</ul>

```py
button = Button(1, "1", custom_id="1", ...)
```

<ul>

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

</ul>

```py
option = SelectOption(label="1", value="1", ...)
```

<ul>

Now:

</ul>

```py
option = SelectOption("1", "1", ...)
```

<ul>

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

</ul>

```py
select = SelectMenu(custom_id="s", options=[...], ...)
```

<ul>

Now:

</ul>

```py
select = SelectMenu("s", [...], ...)
```

<ul>

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

</ul>

```py
ti = TextInput(custom_id="ti", label="ti", style=1, ...)
```

<ul>

Now:

</ul>

```py
ti = TextInput("ti", "ti", 1, ...)
```

<ul>

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

</ul>

```py
modal = Modal(custom_id="modal", title="Modal", components=[...])
```

<ul>

Now:

</ul>

```py
modal = Modal("modal", "Modal", [...])
```

<ul>

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

</ul>

```py
rows = spread_to_rows(..., max_in_row=...)
```

<ul>

Parameters:

* `*components: tuple[ActionRow | Button | SelectMenu]`: The components to spread, use `None` to explicit start a new row.
* `?max_in_row: int`: The maximum number of components in a row. Defaults to `5`.

Returns:

`list[ActionRow]`

</ul>

## Enhanced callbacks

### *func* `component`

<ul>

A modified decorator that allows you to add more information to the `custom_id` and use `startswith` or `regex` to invoke the callback.

</ul>

```py
bot.load("interactions.ext.enhanced")

# startswith:
@bot.component("test", startswith=True)
async def test(ctx):
    ...

# regex:
@bot.component(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(ctx):
    ...
```

<ul>

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

</ul>

```py
bot.load("interactions.ext.enhanced")

# startswith:
@bot.modal("test", startswith=True)
async def test(ctx):
    ...

# regex:
@bot.modal(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(ctx):
    ...
```

<ul>

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

</ul>

```py
# main.py:
bot.load("interactions.ext.enhanced")

# startswith:
@extension_component("test", startswith=True)
async def test(self, ctx):
    ...

# regex:
@extension_component(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(self, ctx):
    ...
```

<ul>

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

</ul>

```py
# main.py:
bot.load("interactions.ext.enhanced")

# startswith:
@extension_modal("test", startswith=True)
async def test(self, ctx):
    ...

# regex:
@extension_modal(r"^[a-z0-9_-]{1,32}$", regex=True)
async def test(self, ctx):
    ...
```

<ul>

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

</ul>

```py
from interactions.ext.enhanced import cooldown

async def cooldown_error(ctx, delta):
    ...

@client.command(...)
@cooldown(seconds=..., ..., error=cooldown_error, type=...)
async def cooldown_command(ctx, ...):
    ...
```

<ul>

Parameters:

* `*delta_args: tuple[datetime.timedelta arguments]`: The arguments to pass to `datetime.timedelta`.
* `?error: Coroutine`: The function to call if the user is on cooldown. Defaults to `None`.
* `?type: str | User | Channel | Guild`: The type of cooldown. Defaults to `None`.
* `**delta_kwargs: dict[datetime.timedelta arguments]`: The keyword arguments to pass to `datetime.timedelta`.

</ul>
