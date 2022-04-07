from asyncio import gather
from inspect import isawaitable
from typing import Coroutine, List, Optional, Union, _GenericAlias, get_args

from interactions.api.http.route import Route

from interactions import Client, HTTPClient


async def get_role(self: HTTPClient, guild_id: int, role_id: int) -> dict:
    """
    Gets a role from a guild.

    Parameters:

    * `guild_id: int`: The guild ID.
    * `role_id: int`: The role ID.

    Returns:

    `Role`: The role we're trying to get.
    """
    request = await self._req.request(Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id))

    for role in request:
        if role.get("id") == str(role_id):
            return role


async def get_emoji(self: HTTPClient, guild_id: int, emoji_id: int) -> dict:
    return await self.get_guild_emoji(guild_id, emoji_id)


async def maybe_coroutine(f, *args, **kwargs):
    value = f(*args, **kwargs)
    return await value if isawaitable(value) else value


async def _get_http(self: Client, class_name: str, http_method: Optional[str] = None) -> Coroutine:
    try:
        return getattr(self._http, http_method or f"get_{class_name.lower()}")
    except AttributeError:
        raise ValueError(f"Client.get() does not support the model {class_name}.")


async def get(
    self: Client, __obj: object, *args, http_method: Optional[str] = None, **kwargs
) -> object:
    r"""
    A helper method for retrieving data from the Discord API in its object representation.

    Parameters:

    * `(?)self: Client`: The client instance. Do not input if using the `Client.get` method.
    * `__obj: object`: The object to get.
    * `*args: list`: The parameters to send with the request.
    * `?http_method: str`: The HTTP method to use. Defaults to `None`.
    * `**kwargs: dict`: The parameters to send with the request.

    Returns:

    `object`: The object we're trying to get.
    """
    if not isinstance(__obj, _GenericAlias):
        class_name: str = __obj.__name__
        _http_method = await _get_http(self, class_name, http_method)
        try:
            res: Union[dict, List[dict]] = await _http_method(*args, **kwargs)
        except TypeError:
            raise ValueError(f"Client.get() could not find a {class_name} with the given IDs.")
        if isinstance(res, dict):
            return __obj(**res, _client=self._http)
        elif isinstance(res, list):
            return [__obj(**r, _client=self._http) for r in res]
        else:
            return res
    else:
        __obj = get_args(__obj)[0]
        class_name = __obj.__name__
        _http_method = await _get_http(self, class_name, http_method)
        arguments: List[List[int]] = list(
            args
            or [(list(kwarg) if isinstance(kwarg, tuple) else kwarg) for kwarg in kwargs.values()]
        )

        for arg in arguments:
            if arguments[0] != arg and not isinstance(arguments[0], list):
                arguments[0] = [arguments[0]]
            if (
                isinstance(arguments[0], list)
                and len(arg) > len(arguments[0])
                and len(arguments[0]) == 1
            ):
                arguments[0] *= len(arg)
                break

        arguments = arguments[0] if len(arguments) == 1 else list(zip(*arguments))

        async def _main():
            return await gather(
                *[
                    _http_method(*arg) if isinstance(arg, (list, tuple)) else _http_method(arg)
                    for arg in arguments
                ]
            )

        res = await _main()

        if isinstance(res, dict):
            return __obj(**res, _client=self._http)
        elif isinstance(res, list):
            return [__obj(**r, _client=self._http) for r in res]
        else:
            return res
