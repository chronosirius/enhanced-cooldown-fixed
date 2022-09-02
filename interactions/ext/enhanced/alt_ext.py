"""
alt_ext

Content:

* AltExt: An alternate extension with enhanced syntax.

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/alt_ext.py

(c) 2022 interactions-py.
"""

from functools import wraps
from importlib import import_module
from inspect import getmembers
from typing import Any, Awaitable, Callable, Coroutine, Dict, Optional, Union

from interactions import Button, Client, Command, Extension, Modal, SelectMenu
from interactions import extension_autocomplete as ext_auto
from interactions import extension_command as ext_cmd
from interactions import extension_component as ext_comp
from interactions import extension_listener as ext_listener
from interactions import extension_message_command as ext_msg_cmd
from interactions import extension_modal as ext_modal
from interactions import extension_user_command as ext_user_cmd

from .callbacks import extension_component, extension_modal

__all__ = ("AltExt",)
Coroutine = Callable[..., Union[Awaitable[Any], Coroutine]]


def remove_self(coro: Coroutine) -> Coroutine:
    @wraps(coro)
    async def wrapper(*args, **kwargs):
        return await coro(*args[1:], **kwargs)

    return wrapper


class AltExt:
    """
    An alternate extension class that uses simpler and improved syntax.

    You don't need a setup function, there is no unnecessary indentation, and you can use the
    extension variable instead of self.

    A simple extension:
    ```py
    from ext import AltExt

    ext = AltExt("ExtName")

    @ext.command()
    async def hello(ctx):
        await ctx.send("Hello!")
    ```

    Parameters:

    * `name: str`: The name of the extension.
    * `**kwargs`: Any attributes to set.
    """

    def __init__(self, name: str, **kwargs) -> None:
        self.name: str = name
        self.__data: Dict[str, Union[Coroutine, Any]] = {}
        self.__setup: bool = True

        for key, value in kwargs.items():
            setattr(self, key, value)

    def add(
        self, coro: Union[Command, Coroutine], raw: Optional[Union[Command, Coroutine]] = None
    ) -> Union[Command, Coroutine]:
        """
        A decorator to add a method to the extension.

        Usage:
        ```py
        ext = AltExt("ExtName")

        @ext.add
        async def method(ctx):
            ...
        ```
        """
        if raw and self.__setup:
            self.__setup = False
            setattr(import_module(raw.__module__), "setup", self.setup)
        self.__data[coro.name if isinstance(coro, Command) else coro.__name__] = coro
        return coro

    def command(self, **kwargs) -> Callable[[Coroutine], Command]:
        """
        A decorator to add a command to the extension.

        Same usage as `interactions.extension_command`.
        """

        def decorator(coro: Coroutine) -> Command:
            return self.add(ext_cmd(**kwargs)(coro), coro)

        return decorator

    def event(self, coro: Optional[Coroutine] = None, name: Optional[str] = None):
        """
        A decorator to add a listener to the extension.

        Same usage as `interactions.extension_listener`.
        """
        coro = remove_self(coro)

        def decorator(_coro: Coroutine):
            return self.add(ext_listener(_coro, name=name), coro)

        return decorator(coro) if coro else decorator

    def component(self, *args, **kwargs) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add a component callback to the extension.

        Same usage as `interactions.extension_component`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(ext_comp(*args, **kwargs)(remove_self(coro)), coro)

        return decorator

    def enhanced_component(
        self,
        component: Union[str, Button, SelectMenu],
        startswith: Optional[bool] = False,
        regex: Optional[bool] = False,
    ) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add an enhanced component callback to the extension.

        Same usage as `interactions.ext.enhanced.extension_component`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(
                extension_component(component, startswith, regex)(remove_self(coro)), coro
            )

        return decorator

    def autocomplete(self, *args, **kwargs) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add an autocomplete callback to the extension.

        Same usage as `interactions.extension_autocomplete`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(ext_auto(*args, **kwargs)(remove_self(coro)), coro)

        return decorator

    def modal(self, *args, **kwargs) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add a modal callback to the extension.

        Same usage as `interactions.extension_modal`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(ext_modal(*args, **kwargs)(remove_self(coro)), coro)

        return decorator

    def enhanced_modal(
        self,
        modal: Union[str, Modal],
        startswith: Optional[bool] = False,
        regex: Optional[bool] = False,
    ) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add an enhanced modal callback to the extension.

        Same usage as `interactions.ext.enhanced.extension_modal`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(extension_modal(modal, startswith, regex)(remove_self(coro)), coro)

        return decorator

    def message_command(self, *args, **kwargs) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add a message command to the extension.

        Same usage as `interactions.extension_message_command`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(ext_msg_cmd(*args, **kwargs)(remove_self(coro)), coro)

        return decorator

    def user_command(self, *args, **kwargs) -> Callable[[Coroutine], Coroutine]:
        """
        A decorator to add a user command to the extension.

        Same usage as `interactions.extension_user_command`.
        """

        def decorator(coro: Coroutine) -> Coroutine:
            return self.add(ext_user_cmd(*args, **kwargs)(remove_self(coro)), coro)

        return decorator

    def setup(self, client: Client, *args, **kwargs) -> Extension:
        """The default setup function for the extension."""
        return self(client, *args, **kwargs)

    def __call__(self, client: Client, *args, **kwargs) -> Extension:
        """Returns the extension in its `Extension` form."""
        ext = type(self.name, (Extension,), self.__data)(client, *args, **kwargs)
        for m in (m for _, m in getmembers(ext) if isinstance(m, Command)):
            m.extension = None
        return ext
