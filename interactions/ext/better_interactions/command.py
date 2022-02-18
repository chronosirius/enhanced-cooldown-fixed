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
from inspect import signature, _empty

from .command_models import BetterOption

log: Logger = get_logger("client")


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

        params = signature(coro).parameters

        if options is MISSING and len(params) > 1:
            context = True
            for __name, param in params.items():
                if context:
                    context = False
                    continue
                typehint: BetterOption = param.annotation
                if typehint is _empty or not isinstance(typehint, BetterOption):
                    raise TypeError(
                        "You must typehint with `BetterOption` or specify `options=[]` in the decorator!"
                    )
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
