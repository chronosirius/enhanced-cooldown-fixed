from interactions import (
    MISSING,
    ApplicationCommandType,
    Option,
    Guild,
    get_logger,
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
from functools import wraps

from loguru import logger


log: Logger = get_logger("client")


@logger.catch
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
        _name = name is not MISSING or coro.__name__
        _description = description is not MISSING or getdoc(coro) or "No description"

        print(f"Registering command: {_name}, {_description}")

        if not options and len(coro.__code__.co_varnames) > 1:
            print("STARTING")

        return self.old_command(
            type=type,
            name=_name,
            description=_description,
            scope=scope,
            options=options,
            default_permission=default_permission,
        )(coro)

    return decorator


@wraps(command)
def extension_command(**kwargs):
    def decorator(coro):
        kwargs["name"] = kwargs.get("name", coro.__name__)
        kwargs["description"] = kwargs.get(
            "description", (getdoc(coro) or "No description")
        )
        coro.__command_data__ = ((), kwargs)
        return coro

    return decorator
