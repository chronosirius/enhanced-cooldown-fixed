from inspect import _empty
from typing import TYPE_CHECKING, List, Optional, Union, get_args

from interactions import (
    MISSING,
    Channel,
    ChannelType,
    Choice,
    Option,
    OptionType,
    Role,
    User,
)

from ._logging import get_logger

if TYPE_CHECKING:
    from collections import OrderedDict

from typing_extensions import _AnnotatedAlias

log = get_logger("command_models")
_type: type = type


def get_type(param):
    """Gets the type of the parameter."""
    return get_args(param.annotation)[0] or get_args(param.annotation)[1].type


def get_option(param):
    """Gets the `BetterOption` of the parameter."""
    return get_args(param.annotation)[1]


def type_to_int(param):
    """Converts the type to an integer."""
    type: Union[_type, int, OptionType] = get_type(param)
    if isinstance(type, int):
        return type
    if type in (str, int, float, bool):
        if type is str:
            return OptionType.STRING
        if type is int:
            return OptionType.INTEGER
        if type is float:
            return OptionType.NUMBER
        if type is bool:
            return OptionType.BOOLEAN
    elif isinstance(type, OptionType):
        return type
    elif type is User:
        return OptionType.USER
    elif type is Channel:
        return OptionType.CHANNEL
    elif type is Role:
        return OptionType.ROLE
    else:
        raise TypeError(f"Invalid type: {type}")


class BetterOption:
    """
    An alternative way of providing options by typehinting.

    Basic example:

    ```py
    @bot.command(...)
    async def command(ctx, name: BetterOption(int, "description") = 5):
        ...
    ```

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
        \"""Says something!\"""
        await ctx.send("something")
    ```

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
    """

    def __init__(
        self,
        type: Union[_type, int, OptionType] = None,
        description: Optional[str] = None,
        name: Optional[str] = None,
        choices: Optional[List[Choice]] = None,
        channel_types: Optional[List[ChannelType]] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        autocomplete: Optional[bool] = None,
        focused: Optional[bool] = None,
        value: Optional[str] = None,
    ):
        log.debug("BetterOption.__init__")
        if isinstance(type, (int, _type(None))):
            self.type = type
        elif type in (str, int, float):
            if type is str:
                self.type = OptionType.STRING
            elif type is int:
                self.type = OptionType.INTEGER
            elif type is float:
                self.type = OptionType.NUMBER
            elif type is bool:
                self.type = OptionType.BOOLEAN
        elif isinstance(type, OptionType):
            self.type = type
        elif type is User:
            self.type = OptionType.USER
        elif type is Channel:
            self.type = OptionType.CHANNEL
        elif type is Role:
            self.type = OptionType.ROLE
        else:
            raise TypeError(f"Invalid type: {type}")

        self.description = description or "No description"
        self.name = name
        self.choices = choices
        self.channel_types = channel_types
        self.min_value = min_value
        self.max_value = max_value
        self.autocomplete = autocomplete
        self.focused = focused
        self.value = value


def parameters_to_options(params: "OrderedDict") -> List[Option]:
    """Converts `BetterOption`s to `Option`s."""
    log.debug("parameters_to_options:")
    _options = [
        (
            Option(
                type=param.annotation.type,
                name=__name if not param.annotation.name else param.annotation.name,
                description=param.annotation.description,
                required=param.default is _empty,
                choices=param.annotation.choices,
                channel_types=param.annotation.channel_types,
                min_value=param.annotation.min_value,
                max_value=param.annotation.max_value,
                autocomplete=param.annotation.autocomplete,
                focused=param.annotation.focused,
                value=param.annotation.value,
            )
            if isinstance(param.annotation, BetterOption)
            else Option(
                type=type_to_int(param),
                name=__name if not get_option(param).name else get_option(param).name,
                description=get_option(param).description,
                required=param.default is _empty,
                choices=get_option(param).choices,
                channel_types=get_option(param).channel_types,
                min_value=get_option(param).min_value,
                max_value=get_option(param).max_value,
                autocomplete=get_option(param).autocomplete,
                focused=get_option(param).focused,
                value=get_option(param).value,
            )
            if isinstance(param.annotation, _AnnotatedAlias)
            else MISSING
        )
        for __name, param in params.items()
    ][1:]

    if any(opt is MISSING for opt in _options):
        raise TypeError(
            "You must typehint with `BetterOption` or specify `options=[]` in the decorator!"
        )
    log.debug(f"  _options: {_options}\n")

    return _options
