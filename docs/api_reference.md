# API Reference

## alt_ext

### *class* AltExt


An alternate extension class that uses simpler and improved syntax.

You don't need a setup function, there is no unnecessary indentation, and you can use the
extension variable instead of self.

A simple extension:
```py
from ext import AltExt

ext = AltExt("ExtName")

@ext.command()
async def hello(ctx):
    await ctx.send("Hello!")
```

Parameters:

* `name: str`: The name of the extension.
* `**kwargs`: Any attributes to set.

Methods:

#### *func* add


A decorator to add a method to the extension.

Usage:
```py
ext = AltExt("ExtName")

@ext.add
async def method(ctx):
    ...
```

#### *func* autocomplete


A decorator to add an autocomplete callback to the extension.

Same usage as `interactions.extension_autocomplete`.

#### *func* command


A decorator to add a command to the extension.

Same usage as `interactions.extension_command`.

#### *func* component


A decorator to add a component callback to the extension.

Same usage as `interactions.extension_component`.

#### *func* enhanced_component


A decorator to add an enhanced component callback to the extension.

Same usage as `interactions.ext.enhanced.extension_component`.

#### *func* enhanced_modal


A decorator to add an enhanced modal callback to the extension.

Same usage as `interactions.ext.enhanced.extension_modal`.

#### *func* event


A decorator to add a listener to the extension.

Same usage as `interactions.extension_listener`.

#### *func* message_command


A decorator to add a message command to the extension.

Same usage as `interactions.extension_message_command`.

#### *func* modal


A decorator to add a modal callback to the extension.

Same usage as `interactions.extension_modal`.

#### *func* setup

The default setup function for the extension.
#### *func* user_command


A decorator to add a user command to the extension.

Same usage as `interactions.extension_user_command`.

## callbacks

### *func* component


A modified decorator that allows you to add more information to the `custom_id` and use
`startswith` or `regex` to invoke the callback.

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

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `(X)bot: Client`: The bot client.
* `component: str | Button | SelectMenu`: The component custom_id or regex to listen to.
* `?startswith: bool = False`: Whether the component custom_id starts with the given string.
* `?regex: bool = False`: Whether the component custom_id matches the given regex.

### *func* modal


A modified decorator that allows you to add more information to the `custom_id` and use
`startswith` or `regex` to invoke the callback.

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

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `(X)bot: Client`: The bot client.
* `modal: str | Modal`: The modal custom_id or regex to listen to.
* `?startswith: bool = False`: Whether the modal custom_id starts with the given string.
* `?regex: bool`: Whether the modal custom_id matches the given regex.

### *func* extension_component


A modified decorator that allows you to add more information to the `custom_id` and use
`startswith` or `regex` to invoke the callback inside of `Extension`s.

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

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `component: str | Button | SelectMenu`: The component custom_id or regex to listen to.
* `?startswith: bool = False`: Whether the component custom_id starts with the given string.
* `?regex: bool = False`: Whether the component custom_id matches the given regex.

### *func* extension_modal


A modified decorator that allows you to add more information to the `custom_id` and use
`startswith` or `regex` to invoke the callback inside of `Extension`s.

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

The startswith callback is called if the `custom_id` starts with the given string.

The regex callback is called if the `custom_id` matches the given regex.

Parameters:

* `modal: str | Modal`: The modal custom_id or regex to listen to.
* `?startswith: bool = False`: Whether the modal custom_id starts with the given string.
* `?regex: bool` = False: Whether the modal custom_id matches the given regex.

## commands

### *func* setup_options


Sets up the options of the command.

Usage:
```py
@bot.command()
@setup_options
async def test(ctx, option: EnhancedOption(...)):
    ...
```

Parameters:

* `(X)coro: Callable[..., Awaitable]`: The coroutine to setup the options of.

## command_models

### *class* EnhancedOption


An alternative way of providing options by typehinting.

Basic example:

```py
@bot.command(...)
async def command(ctx, name: EnhancedOption(int, "description") = 5):
    ...
```

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

Parameters:

* `?option_type: type | int | OptionType`: The type of the option.
* `?description: str = "No description"`: The description of the option.
* `?name: str`: The name of the option. Defaults to the argument name.
* `?**kwargs`: Any additional keyword arguments, same as `ipy.Option`.

## components

### *func* ActionRow


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

### *func* Button


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
* `(?)custom_id: str`: The custom id of the button. *Required if the button is not a link.*
* `(?)url: str`: The URL of the button. *Required if the button is a link.*
* `?emoji: Emoji`: The emoji of the button.
* `?disabled: bool = False`: Whether the button is disabled.
* `**kwargs: dict`: Any additional arguments of the button.

Returns:

`Button`

### *func* SelectOption


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
* `?disabled: bool = False`: Whether the option is disabled.
* `**kwargs: dict`: Any additional arguments of the option.

Returns:

`SelectOption`

### *func* SelectMenu


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
* `**kwargs: dict`: Any additional arguments of the select menu.

Returns:

`SelectMenu`

### *func* TextInput


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
* `?required: bool = True`: Whether the text input is required.
* `?placeholder: str`: The placeholder of the text input.
* `?min_length: int`: The minimum length of the text input.
* `?max_length: int`: The maximum length of the text input.

Returns:

`TextInput`

### *func* Modal


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
* `**kwargs: dict`: Any additional arguments of the modal.

Returns:

`Modal`

## cooldowns

### *class* cooldown


A decorator for handling cooldowns.

Parameters for `datetime.timedelta` are `days=0, seconds=0, microseconds=0,
milliseconds=0, minutes=0, hours=0, weeks=0`.

```py
from interactions.ext.better_interactions import cooldown

async def cooldown_error(ctx, delta):
    ...

@client.command(...)
@cooldown(..., error=cooldown_error, type=..., seconds=..., ...)
async def cooldown_command(ctx, ...):
    ...
```

Parameters:

* `*delta_args: tuple[datetime.timedelta arguments]`: The arguments to pass to `datetime.timedelta`.
* `?error: Coroutine`: The function to call if the user is on cooldown.
* `?type: str | User | Channel | Guild = "user"`: The type of cooldown.
* `?count: int = 1`: The number of times the user can use the command before they are on cooldown.
* `**delta_kwargs: dict[datetime.timedelta arguments]`: The keyword arguments to pass to `datetime.timedelta`.

Methods:

#### *func* get_id


Returns the appropriate ID for the type provided.

Parameters:

* `?type: str | User | Member | Channel | Guild`: The type of cooldown.
* `ctx: CommandContext`: The context to get the id from.

#### *func* reset


Resets the cooldown.

```py
@client.command(...)
@cooldown(..., type=..., seconds=..., ...)
async def cooldown_command(ctx, ...):
    cooldown_command.cooldown.reset(cooldown.get_id("user", ctx))
```

Parameters:

* `?id: str`: The id of the cooldown to reset. If not provided, all cooldowns are reset.

## extension

### *class* Enhanced


This is the core of this library, initialized when loading the extension.

It applies hooks to the client for additional and modified features.

```py
# main.py
client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
```

Parameters:

* `(?)bot: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
* `?ignore_warning: bool`: Whether to ignore the warning. Defaults to `False`.
* `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.

### *func* setup


This function initializes the core of the library, `Enhanced`.

It applies hooks to the client for additional and modified features.

```py
# main.py
client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
```

Parameters:

* `(?)client: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
* `?ignore_warning: bool`: Whether to ignore the warning. Defaults to `False`.
* `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.
