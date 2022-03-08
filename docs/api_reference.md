# API Reference

## Subcommands

### *class* `SubcommandSetup`

<ul>

A class you get when using `base_var = client.base("base_name", ...)`

Use this class to create subcommands by using the `@base_name.subcommand(...)` decorator.

Parameters:

* `client: Client`: The client that the subcommand belongs to. Not needed if you load the extension.
* `base: str`: The base name of the subcommand.
* `description: str`: The description of the subcommand.
* `scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
* `default_permission: bool`: The default permission of the subcommand.

Methods:

<ul>

#### *func* `subcommand`

<ul>

Decorator that creates a subcommand for the corresponding base.

All arguments are optional.

```py
@base_var.subcommand(
    group="group_name",
    name="subcommand_name",
    description="subcommand_description",
    options=[...]
)
```

Parameters:

* `group: str`: The group of the subcommand.
* `name: str`: The name of the subcommand.
* `description: str`: The description of the subcommand.
* `options: list[Option]`: The options of the subcommand.

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
* `description: str`: The description of the subcommand.
* `scope: int | Guild | list[int] | list[Guild]`: The scope of the subcommand.
* `default_permission: bool`: The default permission of the subcommand.

Methods:

<ul>

#### *func* `subcommand` (same as `SubcommandSetup`)

<ul>

Decorator that creates a subcommand for the corresponding base.

All arguments are optional.

```py
@base_var.subcommand(
    group="group_name",
    name="subcommand_name",
    description="subcommand_description",
    options=[...]
)
```

Parameters:

* `group: str`: The group of the subcommand.
* `name: str`: The name of the subcommand.
* `description: str`: The description of the subcommand.
* `options: list[Option]`: The options of the subcommand.

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

* `self: Client`: The client that the base belongs to. Not needed if you load the extension and use `client.base(...)`.
* `base: str`: The base name of the base.
* `description: str`: The description of the base.
* `scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
* `default_permission: bool`: The default permission of the base.

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
* `description: str`: The description of the base.
* `scope: int | Guild | list[int] | list[Guild]`: The scope of the base.
* `default_permission: bool`: The default permission of the base.

</ul>
