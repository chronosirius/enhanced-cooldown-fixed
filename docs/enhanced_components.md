# Enhanced components

This library has a few improvements to the `Button` and `SelectMenu` components, and `ActionRow` has been improved. There is also the `spread_to_rows` function.

The `Button` component has `style` and `label` as positional arguments, and the rest as keyword arguments. Also, there are a few checks to make sure the arguments are valid. In the end, it returns a normal `Button` component from `interactions.py`.

The `SelectMenu` component has `style` and `options` as positional arguments, and the rest as keyword arguments. In the end, it returns a normal `SelectMenu` component from `interactions.py`.

The `ActionRow` component uses `*args`, which lets you do `ActionRow(Button(...), Button(...))` instead of `ActionRow(components=[Button(...), Button(...)])`.

The `TextInput` component has positional arguments, and shows which are optional and which are not.

The `Modal` just has positional arguments.

These can be imported directly from `interactions.ext.enhanced`. They are mostly useful for style and cleanliness of code.

## Status

100% all is well!

## [API Reference](./API-Reference#enhanced-components)
