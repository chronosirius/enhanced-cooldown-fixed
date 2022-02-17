from collections import UserList
from interactions import (
    MISSING,
    ApplicationCommandType,
    Option,
    Guild,
    get_logger,
    OptionType,
    User,
    Channel,
    Role,
    Choice,
    ChannelType,
)
from typing import (
    List,
    Dict,
    Any,
    Optional,
    Union,
    Callable,
    Coroutine,
)
from logging import Logger
from inspect import getdoc
from functools import wraps, partial
from inspect import signature, _empty


log: Logger = get_logger("client")


class BetterOption:
    def __init__(
        self,
        type: Union[type, int, OptionType],
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
        if isinstance(type, int):
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

        self.description = description
        self.name = name
        self.choices = choices
        self.channel_types = channel_types
        self.min_value = min_value
        self.max_value = max_value
        self.autocomplete = autocomplete
        self.focused = focused
        self.value = value


def command(
    self,
    *,
    type: Optional[
        Union[int, ApplicationCommandType]
    ] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = MISSING,
    description: Optional[str] = MISSING,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
    options: Optional[
        Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]
    ] = MISSING,
    default_permission: Optional[bool] = MISSING,
) -> Callable[..., Any]:
    """
    A decorator for registering an application command to the Discord API,
    as well as being able to listen for ``INTERACTION_CREATE`` dispatched
    gateway events.
    The structure of a chat-input command:
    .. code-block:: python
        @command(name="command-name", description="this is a command.")
        async def command_name(ctx):
            ...
    You are also able to establish it as a message or user command by simply passing
    the ``type`` kwarg field into the decorator:
    .. code-block:: python
        @command(type=interactions.ApplicationCommandType.MESSAGE, name="Message Command")
        async def message_command(ctx):
            ...
    The ``scope`` kwarg field may also be used to designate the command in question
    applicable to a guild or set of guilds.
    :param type?: The type of application command. Defaults to :meth:`interactions.enums.ApplicationCommandType.CHAT_INPUT` or ``1``.
    :type type: Optional[Union[str, int, ApplicationCommandType]]
    :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
    :type name: Optional[str]
    :param description?: The description of the application command. This should be left blank if you are not using ``CHAT_INPUT``.
    :type description: Optional[str]
    :param scope?: The "scope"/applicable guilds the application command applies to.
    :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
    :param options?: The "arguments"/options of an application command. This should be left blank if you are not using ``CHAT_INPUT``.
    :type options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]]
    :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
    :type default_permission: Optional[bool]
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Callable[..., Any]:
        # TODO: fix this code once it breaks
        _name = coro.__name__ if name is MISSING else name
        _description = (
            getdoc(coro) or "No description" if description is MISSING else description
        )
        _description = _description[:100]
        _options = []

        print(f"Registering command: {_name}, {_description[:100]}")

        if options is MISSING and len(coro.__code__.co_varnames) > 1:
            print(f"STARTING {_name}")
            params = signature(coro).parameters
            for __name, param in params.items():
                typehint = param.annotation
                _options.append(
                    Option(
                        type=typehint.type,
                        name=__name if not typehint.name else typehint.name,
                        description=typehint.description,
                        required=param.default is _empty,
                        choices=typehint.choices,
                        channel_types=typehint.channel_types,
                        min_value=typehint.min_value,
                        max_value=typehint.max_value,
                        autocomplete=typehint.autocomplete,
                        focused=typehint.focused,
                        value=typehint.value,
                    )
                )

        return self.old_command(
            type=type,
            name=_name,
            description=_description,
            scope=scope,
            options=_options,
            default_permission=default_permission,
        )(coro)

    return decorator


def extension_command(**kwargs):
    def decorator(coro):
        name = kwargs.get("name", MISSING)
        description = kwargs.get("description", MISSING)
        kwargs["name"] = coro.__name__ if name is MISSING else name
        kwargs["description"] = (
            getdoc(coro) or "No description" if description is MISSING else description
        )
        kwargs["description"] = kwargs["description"][:100]
        coro.__command_data__ = ((), kwargs)
        return coro

    return decorator
