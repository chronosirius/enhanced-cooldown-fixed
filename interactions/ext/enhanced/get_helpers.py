"""
get_helpers

Content:

* get: get object(s) from the Discord API.

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/get_helpers.py

(c) 2022 interactions-py.
"""
from asyncio import gather
from typing import Coroutine, List, Optional, Union, _GenericAlias, get_args

from interactions.api.http.route import Route

from interactions import Client, HTTPClient, Item, Role

from ._logging import get_logger

log = get_logger("get_helpers")


async def get_role(self: HTTPClient, guild_id: int, role_id: int) -> dict:
    """
    Gets a role from a guild.

    Parameters:

    * `guild_id: int`: The guild ID.
    * `role_id: int`: The role ID.

    Returns:

    `dict`
    """
    request = await self._req.request(Route("GET", "/guilds/{guild_id}/roles", guild_id=guild_id))

    for role in request:
        if role.get("id"):
            self.cache.roles.add(Item(id=role["id"], value=Role(**role)))
            if role["id"] == str(role_id):
                return role


async def get_emoji(self: HTTPClient, guild_id: int, emoji_id: int) -> dict:
    """
    Gets an emoji from a guild.

    Parameters:

    * `guild_id: int`: The guild ID.
    * `emoji_id: int`: The role ID.

    Returns:

    `dict`
    """
    return await self.get_guild_emoji(guild_id, emoji_id)


async def _get_http(self: Client, class_name: str, http_method: Optional[str] = None) -> Coroutine:
    """Gets the HTTPClient method to use in `get()`."""
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
        log.debug(f"Getting 1 {class_name} with {args} and {kwargs}")
        _http_method: Coroutine = await _get_http(self, class_name, http_method)
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
        __obj: object = get_args(__obj)[0]
        class_name: str = __obj.__name__
        log.debug(f"Getting {len(args or kwargs)} {class_name}s with {args} and {kwargs}")
        _http_method: Coroutine = await _get_http(self, class_name, http_method)
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

        arguments: List[List[int]] = arguments[0] if len(arguments) == 1 else list(zip(*arguments))

        async def _main() -> List[dict]:
            return await gather(
                *[
                    _http_method(*arg) if isinstance(arg, (list, tuple)) else _http_method(arg)
                    for arg in arguments
                ]
            )

        res = await _main()

        if isinstance(res, list):
            return [__obj(**r, _client=self._http) for r in res]
        elif isinstance(res, dict):
            return __obj(**res, _client=self._http)
        else:
            return res
