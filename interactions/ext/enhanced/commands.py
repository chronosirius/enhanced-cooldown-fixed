from asyncio import Task, get_running_loop, sleep
from functools import wraps
from inspect import getdoc, signature
from logging import Logger
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

from typing_extensions import _AnnotatedAlias

from interactions import (
    MISSING,
    ApplicationCommandType,
    CommandContext,
    ComponentContext,
    Guild,
    Option,
    get_logger,
)

from .command_models import EnhancedOption, parameters_to_options

log: Logger = get_logger("command")


def command(
    self,
    _coro: Optional[Coroutine] = MISSING,
    *,
    type: Optional[Union[int, ApplicationCommandType]] = ApplicationCommandType.CHAT_INPUT,
    name: Optional[str] = MISSING,
    description: Optional[str] = MISSING,
    scope: Optional[Union[int, Guild, List[int], List[Guild]]] = MISSING,
    options: Optional[Union[Dict[str, Any], List[Dict[str, Any]], Option, List[Option]]] = MISSING,
    default_permission: Optional[bool] = MISSING,
    debug_scope: Optional[bool] = True,
) -> Callable[..., Any]:
    """
    A modified decorator for creating slash commands.

    Makes `name` and `description` optional, and adds ability to use `EnhancedOption`s.

    Full-blown example:

    ```py
    from interactions import OptionType, Channel
    from interactions.ext.enhanced import EnhancedOption
    from typing_extensions import Annotated

    @bot.command()
    async def options(
        ctx,
        option1: Annotated[str, EnhancedOption(description="...")],
        option2: Annotated[OptionType.MENTIONABLE, EnhancedOption(description="...")],
        option3: Annotated[Channel, EnhancedOption(description="...")],
    ):
        \"""Says something!\"""
        await ctx.send("something")
    ```

    Parameters:

    * `?type: int | ApplicationCommandType`: The type of application command. Defaults to `ApplicationCommandType.CHAT_INPUT`.
    * `?name: str`: The name of the command. Defaults to function name.
    * `?description: str`: The description of the command. Defaults to function docstring or `"No description"`.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the command.
    * `?options: list[Option]`: The options of the command.
    * `?default_permission: bool`: The default permission of the command.
    * `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.
    """

    def decorator(coro: Coroutine) -> Callable[..., Any]:
        # TODO: fix this code once it breaks
        _name = coro.__name__ if name is MISSING else name
        _description = (
            MISSING
            if type != ApplicationCommandType.CHAT_INPUT
            else getdoc(coro) or "No description"
            if description is MISSING
            else description
        )
        if isinstance(_description, str):
            _description = _description.split("\n")[0]
            if len(_description) > 100:
                raise ValueError("Description must be less than 100 characters.")
        _scope = (
            self.__debug_scope
            if scope is MISSING and hasattr(self, "__debug_scope") and debug_scope
            else scope
        )

        params = signature(coro).parameters
        _options = (
            coro.__decor_options
            if hasattr(coro, "__decor_options")
            else parameters_to_options(params)
            if options is MISSING
            and len(params) > 1
            and any(
                isinstance(param.annotation, (EnhancedOption, _AnnotatedAlias))
                for _, param in params.items()
            )
            else options
        )
        log.debug(f"command: {_name=} {_description=} {_options=}")

        return self.old_command(
            type=type,
            name=_name,
            description=_description,
            scope=_scope,
            options=_options,
            default_permission=default_permission,
        )(coro)

    if _coro is not MISSING:
        return decorator(_coro)
    return decorator


def extension_command(_coro: Optional[Coroutine] = MISSING, **kwargs):
    """
    A modified decorator for creating slash commands inside `Extension`s.

    Makes `name` and `description` optional, and adds ability to use `EnhancedOption`s.

    Same parameters as `interactions.ext.enhanced.command`.

    Parameters:

    * `?type: int | ApplicationCommandType`: The type of application command. Defaults to `ApplicationCommandType.CHAT_INPUT`.
    * `?name: str`: The name of the command. Defaults to function name.
    * `?description: str`: The description of the command. Defaults to function docstring or `"No description"`.
    * `?scope: int | Guild | list[int] | list[Guild]`: The scope of the command.
    * `?options: list[Option]`: The options of the command.
    * `?default_permission: bool`: The default permission of the command.
    * `?debug_scope: bool`: Whether to use debug_scope for this command. Defaults to `True`.
    """

    def decorator(coro):
        name = kwargs.get("name", MISSING)
        description = kwargs.get("description", MISSING)
        kwargs["name"] = coro.__name__ if name is MISSING else name
        kwargs["description"] = (
            MISSING
            if type != ApplicationCommandType.CHAT_INPUT
            else getdoc(coro) or "No description"
            if description is MISSING
            else description
        )
        if isinstance(kwargs["description"], str):
            kwargs["description"] = kwargs["description"].split("\n")[0]
            if len(kwargs["description"]) > 100:
                raise ValueError("Description must be less than 100 characters.")
        coro.__command_data__ = ((), kwargs)
        log.debug(f"extension_command: {coro.__command_data__=}")
        return coro

    if _coro is not MISSING:
        return decorator(_coro)
    return decorator


def autodefer(
    delay: Optional[Union[float, int]] = 2,
    ephemeral: Optional[bool] = False,
    edit_origin: Optional[bool] = False,
):
    """
    Set up a command to be automatically deferred after some time.

    Note: This will not work if blocking code is used (such as the requests module).

    Usage:

    ```py
    @bot.command(...)
    @autodefer(...)
    async def foo(ctx, ...):
        ...
    ```

    Parameters:

    * `?delay: float | int`: How long to wait before deferring in seconds. Defaults to `2`.
    * `?ephemeral: bool`: If the command should be deferred hidden. Defaults to `False`.
    * `?edit_origin: bool`: If the command should be deferred with the origin message. Defaults to `False`.
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
