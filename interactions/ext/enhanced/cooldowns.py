"""
Credit to @dontbanmeplz for the original code regarding cooldowns, and merging into better-interactions.
"""
from datetime import datetime, timedelta
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Coroutine, Optional, Type, Union

from interactions import Channel, CommandContext, Guild, Member, User

NoneType: Type[None] = type(None)


def get_id(type: Optional[Union[str, User, Channel, Guild]], ctx: CommandContext) -> str:
    """Returns the appropriate ID for the type provided."""
    type = type.lower() if isinstance(type, str) else type

    if type == "user" or type is User or type == "member" or type is Member:
        return str(ctx.author.user.id)
    if type == "channel" or type is Channel:
        return str(ctx.channel_id)
    if type == "guild" or type is Guild:
        return str(ctx.guild_id)
    raise TypeError("Invalid type provided for `type`!")


def cooldown(
    *delta_args,
    error: Optional[Coroutine] = None,
    type: Optional[Union[str, User, Channel, Guild]] = "user",
    **delta_kwargs,
):
    """
    A decorator for handling cooldowns.

    Parameters for `datetime.timedelta` are `days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0`.

    ```py
    from interactions.ext.better_interactions import cooldown

    async def cooldown_error(ctx, delta):
        ...

    @client.command(...)
    @cooldown(seconds=..., ..., error=cooldown_error, type=...)
    async def cooldown_command(ctx, ...):
        ...
    ```

    Parameters:

    * `*delta_args: tuple[datetime.timedelta arguments]`: The arguments to pass to `datetime.timedelta`.
    * `?error: Coroutine`: The function to call if the user is on cooldown. Defaults to `None`.
    * `?type: str | User | Channel | Guild`: The type of cooldown. Defaults to `None`.
    * `**delta_kwargs: dict[datetime.timedelta arguments]`: The keyword arguments to pass to `datetime.timedelta`.
    """
    if not (delta_args or delta_kwargs):
        raise ValueError(
            "Cooldown amount must be provided! Valid arguments and keyword arguments are listed in https://docs.python.org/3/library/datetime.html#datetime.timedelta"
        )

    delta = timedelta(*delta_args, **delta_kwargs)

    def decorator(coro: Coroutine):
        coro.__last_called = {}

        if not isinstance(error, (Callable, NoneType)):
            raise TypeError(
                "Invalid type provided for `error`! Must be a `Callable`, specifically a `Coroutine`!"
            )
        if type not in {"user", User, "guild", Guild, "channel", Channel}:
            raise TypeError("Invalid type provided for `type`!")

        @wraps(coro)
        async def wrapper(ctx: CommandContext, *args, **kwargs):
            last_called: dict = coro.__last_called
            now = datetime.now()
            id = get_id(type, ctx)
            unique_last_called = last_called.get(id)

            if unique_last_called and (now - unique_last_called < delta):
                if not error:
                    return await ctx.send(
                        f"This command is on cooldown for {delta - (now - unique_last_called)}!"
                    )
                return (
                    await error(ctx, delta - (now - unique_last_called))
                    if iscoroutinefunction(error)
                    else error(ctx, delta - (now - unique_last_called))
                )

            last_called[id] = now
            coro.__last_called = last_called
            return await coro(ctx, *args, **kwargs)

        return wrapper

    return decorator
