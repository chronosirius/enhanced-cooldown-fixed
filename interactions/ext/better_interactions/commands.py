from asyncio import Task, get_running_loop, sleep
from functools import wraps
from inspect import getdoc, signature
from logging import Logger
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from interactions import (
    MISSING,
    ApplicationCommandType,
    CommandContext,
    ComponentContext,
    Guild,
    Option,
    get_logger,
)

from .command_models import parameters_to_options

log: Logger = get_logger("command")


def command(
    self,
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = MISSING,
    description: Optional[str] = MISSING,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = MISSING,
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
        ).split("\n")[0]
        if len(_description) > 100:
            raise ValueError("Description must be less than 100 characters.")

        params = signature(coro).parameters
        _options = (
            parameters_to_options(params) if options is MISSING and len(params) > 1 else options
        )
        log.debug(f"command: {_name=} {_description=} {_options=}")

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
        ).split("\n")[0]
        if len(kwargs["description"]) > 100:
            raise ValueError("Description must be less than 100 characters.")
        coro.__command_data__ = ((), kwargs)
        log.debug(f"extension_command: {coro.__command_data__=}")
        return coro

    return decorator


def autodefer(
    delay: Optional[Union[float, int]] = 2,
    ephemeral: Optional[bool] = False,
    edit_origin: Optional[bool] = False,
):
    """
    Set up a command to be automatically deferred after some time
    Note: This will not work if blocking code is used (such as the requests module)

    Usage:
    ```py
    @bot.command(...)
    @autodefer(...)
    async def foo(ctx, ...):
        ...
    ```

    :param delay: How long to wait before deferring
    :type delay: Optional[Union[float, int]]
    :param ephemeral: If the command should be deferred hidden
    :type ephemeral: Optional[bool]
    :param edit_origin: If the command should be deferred with the origin message
    :type edit_origin: Optional[bool]
    """

    def inner(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def deferring_func(ctx: Union[CommandContext, ComponentContext], *args, **kwargs):
            try:
                loop = get_running_loop()
            except RuntimeError as e:
                raise RuntimeError("No running event loop detected!") from e
            task: Task = loop.create_task(func(ctx, *args, **kwargs))

            await sleep(delay)

            if task.done():
                return task.result()

            if not (ctx.deferred or ctx.responded):
                if isinstance(ctx, ComponentContext):
                    await ctx.defer(ephemeral=ephemeral, edit_origin=edit_origin)
                else:
                    await ctx.defer(ephemeral=ephemeral)

            return await task

        return deferring_func

    return inner
