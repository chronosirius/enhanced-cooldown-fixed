# better-interactions

[![Discord](https://img.shields.io/discord/924871439776108544?color=blue&label=discord&style=for-the-badge)](https://discord.gg/Y78bpT5aNv) [![PyPI - Downloads](https://img.shields.io/pypi/dm/interactions-better-components?color=blue&style=for-the-badge)](https://pypi.org/project/better-interactions/)

Better interactions for interactions.py

Join the [Discord server](https://discord.gg/Y78bpT5aNv) to ask questions, get help, or to discuss the project!

## Installation

```bash
pip install -U better-interactions
```

## Table of Contents

- [Installation](#installation)
- [Table of Contents](#table-of-contents)
- [What is this library?](#what-is-this-library)
- [What does this have?](#what-does-this-have)
  - [Subcommands](#subcommands)
  - [Better commands](#better-commands)
  - [Better components](#better-components)
  - [Better component callback](#better-component-callback)
  - [Cooldown](#cooldown)

## What is this library?

This is `better-interactions`, a library for `interactions.py` which modifies interactions, and adds useful helper functions.

## What does this have?

Listed below are all the features this library currently has:

- [Subcommands](#subcommands)
- [Better commands](#better-commands)
- [Better components](#better-components)
- [Better component callback](#better-component-callback)
- [Cooldown](#cooldown)

---------------------

## [API Reference](./docs/api_reference.md)

[![API Reference](https://img.shields.io/badge/API-Reference-blue.svg)](./docs/api_reference.md)

## Subcommands

Subcommands are technically options for commands, meaning to make subcommands, you may need long chains of options and if/elif/else conditionals.

This library provides a way to make subcommands, similar to subcommands in `discord-py-interactions<=3.0.2`.

Click [here](./docs/subcommands.md) to see more information and examples on subcommands!

## Better commands

Better commands are commands that have a default name and description.

Click [here](./docs/better_commands.md) to see more information and examples on better commands!

## Better components

Improved `Button`, `SelectMenu`, and `ActionRow` components, with error correction, `spread_to_rows`, and more.

Click [here](./docs/better_components.md) to see more information and examples on better components!

## Better component callback

The new component callbacks are modified so you can enable checking if the `custom_id` of the component starts with the one provided in the decorator, or use regex.

Click [here](./docs/better_component_callback.md) to see more information and examples on better component callbacks!

## Cooldown

The `cooldown` decorator is a simple and easy way to add a cooldown or slowmode to a command, with customization.

Credit to [@dontbanmeplz](https://github.com/dontbanmeplz) for the original code.

Click [here](./docs/cooldown.md) to see more information and examples on cooldown!
