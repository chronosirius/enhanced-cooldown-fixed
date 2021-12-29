from interactions import (
    ApplicationCommandType,
    Guild,
    Option,
    InteractionException,
    ApplicationCommand,
)
from typing import Coroutine, Optional, Union, List, Dict, Any, Callable


def command(
    *,
    type: Optional[
        Union[int, ApplicationCommandType]
    ] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = None,
    description: Optional[str] = None,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    options: Optional[
        Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]
    ] = None,
    default_permission: Optional[bool] = None,
) -> List[ApplicationCommand]:
    """
    A wrapper designed to interpret the client-facing API for
    how a command is to be created and used.
    :return: A list of command paylods.
    :rtype: List[ApplicationCommand]
    """
    _type: int = 0
    if isinstance(type, ApplicationCommandType):
        _type: int = type.value
    else:
        _type: int = ApplicationCommandType(type).value

    _description: str = "" if description is None else description
    _options: list = []

    if options:
        if all(isinstance(option, Option) for option in options):
            _options = [option._json for option in options]
        elif all(
            isinstance(option, dict) and all(isinstance(value, str) for value in option)
            for option in options
        ):
            _options = [option for option in options]
        elif isinstance(options, Option):
            _options = [options._json]
        else:
            _options = [options]

    _default_permission: bool = (
        True if default_permission is None else default_permission
    )

    # TODO: Implement permission building and syncing.
    # _permissions: list = []

    # if permissions:
    #     if all(isinstance(permission, Permission) for permission in permissions):
    #         _permissions = [permission._json for permission in permissions]
    #     elif all(
    #         isinstance(permission, dict)
    #         and all(isinstance(value, str) for value in permission)
    #         for permission in permissions
    #     ):
    #         _permissions = [permission for permission in permissions]
    #     elif isinstance(permissions, Permission):
    #         _permissions = [permissions._json]
    #     else:
    #         _permissions = [permissions]

    _scope: list = []

    payloads: list = []

    if scope:
        if isinstance(scope, list):
            if all(isinstance(guild, Guild) for guild in scope):
                [_scope.append(guild.id) for guild in scope]
            elif all(isinstance(guild, int) for guild in scope):
                [_scope.append(guild) for guild in scope]
        else:
            _scope.append(scope)

    if _scope:
        for guild in _scope:
            payload: ApplicationCommand = ApplicationCommand(
                type=_type,
                guild_id=guild,
                name=name,
                description=_description,
                options=_options,
                default_permission=_default_permission,
            )
            payloads.append(payload)
    else:
        payload: ApplicationCommand = ApplicationCommand(
            type=_type,
            name=name,
            description=_description,
            options=_options,
            default_permission=_default_permission,
        )
        payloads.append(payload)

    return payloads


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
