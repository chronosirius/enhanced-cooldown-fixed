# enhanced

![enhanced banner](https://github.com/interactions-py/enhanced/blob/main/src/enhanced_banner.png?raw=true)

[![Discord](https://img.shields.io/discord/924871439776108544?color=blue&label=discord&style=for-the-badge)](https://discord.gg/Y78bpT5aNv) [![PyPI - Downloads](https://img.shields.io/pypi/dm/enhanced?color=blue&style=for-the-badge)](https://pypi.org/project/enhanced/)

Enhanced interactions for interactions.py

Join the [Discord server](https://discord.gg/Y78bpT5aNv) to ask questions, get help, or to discuss the project!

## Installation

```bash
pip install -U enhanced
```

## Table of Contents

- [Installation](#installation)
- [Table of Contents](#table-of-contents)
- [What is this library?](#what-is-this-library)
- [What does this have?](#what-does-this-have)
  - [Subcommands](#subcommands)
  - [Enhanced commands](#enhanced-commands)
  - [Enhanced components](#enhanced-components)
  - [Enhanced callbacks](#enhanced-callbacks)
  - [Cooldown](#cooldown)

## What is this library?

This is `enhanced`, a library for `interactions.py` which modifies interactions, and adds useful helper functions and models.

It simplifies the process of creating commands, and provides an easy and organized way to make subcommands. Enhanced callbacks are also implemented, which allow for more advanced functionality. Enhanced components are also implemented, which allow for better looking code. A cooldown system is also implemented, which allows for commands to have a cooldown.

## What does this have?

Listed below are all the features this library currently has:

- [Subcommands](#subcommands)
- [Enhanced commands](#enhanced-commands)
- [Enhanced components](#enhanced-components)
- [Enhanced callbacks](#enhanced-callbacks)
- [Cooldown](#cooldown)

---------------------

## [API Reference](./API-Reference)

[![API Reference](https://img.shields.io/badge/API-Reference-blue.svg)](./API-Reference)

## Subcommands

Subcommands are technically options for commands, meaning to make subcommands, you may need long chains of options and if/elif/else conditionals.

This library provides a way to make subcommands, similar to subcommands in `discord-py-interactions<=3.0.2`.

Click [here](./Subcommands) to see more information and examples on subcommands!

## Enhanced commands

Enhanced commands are commands that have a default name and description, and the ability to typehint options.

Click [here](./Enhanced-commands) to see more information and examples on enhanced commands!

## Enhanced components

Improved `Button`, `SelectMenu`, `ActionRow`, `TextInput`, and `Modal` components, with error correction, `spread_to_rows` functionality, and more.

Click [here](./Enhanced-components) to see more information and examples on enhanced components!

## Enhanced callbacks

The new component and modal callbacks are modified so you can enable checking if the `custom_id` of the component or model starts with the one provided in the decorator, or use regex.

Click [here](./Enhanced-callbacks) to see more information and examples on enhanced callbacks!

## Cooldown

The `cooldown` decorator is a simple and easy way to add a cooldown or slowmode to a command, with customization.

Credit to [@dontbanmeplz](https://github.com/dontbanmeplz) for the original code.

Click [here](./Cooldown) to see more information and examples on cooldown!
