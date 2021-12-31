from interactions import (
    ApplicationCommandType,
    Guild,
    Option,
    InteractionException,
    ApplicationCommand,
)
from typing import Coroutine, Optional, Union, List, Dict, Any, Callable
from interactions.decor import command


def message_menu(
    self,
    *,
    name: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> Callable[..., Any]:
    """
    A decorator for registering a message context menu to the Discord API,
    as well as being able to listen for ``INTERACTION_CREATE`` dispatched
    gateway events.
    The structure of a user context menu:
    .. code-block:: python
        @user_menu(name="Context menu name", description="this is a message context menu.")
        async def context_menu_name(ctx):
            ...
    The ``scope`` kwarg field may also be used to designate the command in question
    applicable to a guild or set of guilds.
    :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
    :type name: Optional[str]
    :param scope?: The "scope"/applicable guilds the application command applies to.
    :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
    :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
    :type default_permission: Optional[bool]
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Callable[..., Any]:
        if not name:
            raise InteractionException(11, message="Your command must have a name.")

        if not len(coro.__code__.co_varnames):
            raise InteractionException(
                11,
                message="Your command needs at least one argument to return context.",
            )

        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.MESSAGE,
            name=name,
            description=None,
            scope=scope,
            options=None,
            default_permission=default_permission,
        )

        if self.automate_sync:
            [
                self.loop.run_until_complete(self.synchronize(command))
                for command in commands
            ]

        return self.event(coro, name=f"command_{name}")

    return decorator


def user_menu(
    self,
    *,
    name: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    default_permission: Optional[bool] = None,
) -> Callable[..., Any]:
    """
    A decorator for registering a user context menu to the Discord API,
    as well as being able to listen for ``INTERACTION_CREATE`` dispatched
    gateway events.
    The structure of a user context menu:
    .. code-block:: python
        @user_menu(name="Context menu name", description="this is a user context menu.")
        async def context_menu_name(ctx):
            ...
    The ``scope`` kwarg field may also be used to designate the command in question
    applicable to a guild or set of guilds.
    :param name: The name of the application command. This *is* required but kept optional to follow kwarg rules.
    :type name: Optional[str]
    :param scope?: The "scope"/applicable guilds the application command applies to.
    :type scope: Optional[Union[int, Guild, List[int], List[Guild]]]
    :param default_permission?: The default permission of accessibility for the application command. Defaults to ``True``.
    :type default_permission: Optional[bool]
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Callable[..., Any]:
        if not name:
            raise InteractionException(11, message="Your command must have a name.")

        if not len(coro.__code__.co_varnames):
            raise InteractionException(
                11,
                message="Your command needs at least one argument to return context.",
            )

        commands: List[ApplicationCommand] = command(
            type=ApplicationCommandType.USER,
            name=name,
            description=None,
            scope=scope,
            options=None,
            default_permission=default_permission,
        )

        if self.automate_sync:
            [
                self.loop.run_until_complete(self.synchronize(command))
                for command in commands
            ]

        return self.event(coro, name=f"command_{name}")

    return decorator
