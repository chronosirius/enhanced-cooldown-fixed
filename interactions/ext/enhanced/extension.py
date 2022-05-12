"""
extension

Content:

* EnhancedExtension: extension class.
* base: base class for extension.
* version: version of the extension.

GitHub: https://github.com/interactions-py/enhanced/blob/main/interactions/ext/enhanced/extension.py

(c) 2022 interactions-py.
"""
import types
from inspect import getmembers, iscoroutinefunction
from logging import Logger
from re import fullmatch
from typing import List, Optional, Union

from interactions import MISSING, Client, CommandContext, ComponentContext, Extension, Guild
from interactions.ext import Base, Version, VersionAuthor

from ._logging import get_logger
from .subcommands import ExternalSubcommandSetup

log: Logger = get_logger("extension")


version: Version = Version(
    version="3.3.0",  # could not release candidate
    author=VersionAuthor(
        name="Toricane",
        email="prjwl028@gmail.com",
    ),
)

base = Base(
    name="enhanced",
    version=version,
    description="Enhanced interactions for interactions.py",
    link="https://github.com/interactions-py/enhanced",
    packages=["interactions.ext.enhanced"],
    requirements=[
        "discord-py-interactions>=4.1.1rc.1",
        "typing_extensions",
    ],
)


def sync_subcommands(self: Extension, client: Client) -> Optional[dict]:
    """Syncs the subcommands in the extension."""
    if not any(
        hasattr(func, "__subcommand__")
        for _, func in getmembers(self, predicate=iscoroutinefunction)
    ):
        return
    bases = {
        func.__base__: func.__data__
        for _, func in getmembers(self, predicate=iscoroutinefunction)
        if hasattr(func, "__subcommand__")
    }

    if not bases:
        return

    # commands = []

    for base, subcommand in bases.items():
        base: str
        subcommand: ExternalSubcommandSetup
        subcommand.inner._command_data = subcommand.raw_commands
        client._Client__command_coroutines.append(subcommand.inner)
        client.event(subcommand.inner, name=f"command_{base}")
        # commands.extend(subcommand.raw_commands)

    # if client._automate_sync:
    #     if client._loop.is_running():
    #         [client._loop.create_task(client._synchronize(command)) for command in commands]
    #     else:
    #         [client._loop.run_until_complete(client._synchronize(command)) for command in commands]
    for subcommand in bases.values():
        scope = subcommand.scope
        if scope is not MISSING:
            if isinstance(scope, list):
                [client._scopes.add(_ if isinstance(_, int) else _.id) for _ in scope]
            else:
                client._scopes.add(scope if isinstance(scope, int) else scope.id)

    for base, subcommand in bases.items():
        base: str
        subcommand: ExternalSubcommandSetup
        subcommand._super_autocomplete(client)

    return bases


def sync_new_subcommands(cls: Extension, client: Client):
    subcmds = []
    new_bases: set = set()
    for _, func in getmembers(cls, predicate=iscoroutinefunction):
        if hasattr(func, "manager") and func.manager.full_data:
            subcmds.append(func.manager)
            if (
                hasattr(client, "__debug_scope")
                and getattr(client, "__debug_scope")
                and func.manager.debug_scope
            ):
                func.manager.scope = getattr(client, "__debug_scope")
            if func.manager.base not in new_bases:
                func.manager.subcommand_caller = func.manager.full_data
                client._Client__command_coroutines.append(func.manager.subcommand_caller)
                client.event(func.manager.subcommand_caller, name=f"command_{func.manager.base}")
                # OLD:
                # if client._automate_sync:
                #     if client._loop.is_running() and isinstance(func.manager.full_data, list):
                #         for data in func.manager.full_data:
                #             client._loop.create_task(client._synchronize(data))
                #     elif (
                #         client._loop.is_running()
                #         and not isinstance(func.manager.full_data, list)
                #         or not client._loop.is_running()
                #         and not isinstance(func.manager.full_data, list)
                #     ):
                #         client._loop.create_task(client._synchronize(func.manager.full_data))
                #     else:
                #         for data in func.manager.full_data:
                #             client._loop.run_until_complete(client._synchronize(data))
                # client.event(func.manager.subcommand_caller, name=f"command_{func.manager.base}")
                # new_bases.add(func.manager.base)
                # END OLD
            del func.__command_data__
    return subcmds


class EnhancedExtension(Extension):
    """
    Enables modified external commands, subcommands, callbacks, and more.

    Use this class instead of `Extension` when using extensions.

    ```py
    # extension.py
    from interactions.ext.enhanced import EnhancedExtension

    class Example(EnhancedExtension):
        ...

    def setup(client):
        Example(client)
    ```
    """

    def __new__(cls, client: Client, *args, **kwargs):
        subcmds = sync_new_subcommands(cls, client)

        log.debug("Syncing subcommands...")
        bases = sync_subcommands(cls, client)
        log.debug("Synced subcommands")

        self = super().__new__(cls, client, *args, **kwargs)

        if bases:
            for base, subcommand in bases.items():
                base: str
                subcommand: ExternalSubcommandSetup
                subcommand.set_self(self)
                commands = self._commands.get(f"command_{base}", [])
                commands.append(subcommand.inner)
                self._commands[f"command_{base}"] = commands

        if subcmds:
            for sub in subcmds:
                sub.set_self(self)

        return self


def start(self: Client) -> None:
    """Starts the client session."""
    if hasattr(self, "_command_data") and self._command_data:
        if self._automate_sync:
            if self._loop.is_running():
                for command in self._command_data:
                    self._loop.create_task(self._synchronize(command))
            else:
                for command in self._command_data:
                    self._loop.run_until_complete(self._synchronize(command))
        for name, coro in self._command_coros.items():
            self.event(coro, name=f"command_{name}")
    self._loop.run_until_complete(self._ready())


class Enhanced(Extension):
    """
    This is the core of this library, initialized when loading the extension.

    It applies hooks to the client for additional and modified features.

    ```py
    # main.py
    client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
    ```

    Parameters:

    * `(?)bot: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
    * `?ignore_warning: bool`: Whether to ignore the warning. Defaults to `False`.
    * `?debug_scope: int | Guild | list[int] | list[Guild]`: The debug scope to apply to global commands.
    * `?add_get: bool`: Whether to add the `get()` helper function. Defaults to `True`.
    * `?add_subcommand: bool`: Whether to add subcommand hooks to the client. Defaults to `True`.
    * `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.
    * `?modify_command: bool`: Whether to modify the command decorator. Defaults to `True`.
    """

    def __init__(
        self,
        bot: Client,
        *,
        ignore_warning: bool = False,
        debug_scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
        add_get: bool = True,
        add_subcommand: bool = True,
        modify_callbacks: bool = True,
        modify_command: bool = True,
    ):
        if not isinstance(bot, Client):
            log.critical("The bot is not an instance of Client")
            if not ignore_warning:
                raise TypeError(f"{bot.__class__.__name__} is not interactions.Client!")
        log.debug("The bot is an instance of Client")

        from .file_sending import create_interaction_response

        bot._http.create_interaction_response = types.MethodType(
            create_interaction_response, bot._http
        )

        # bot.start = types.MethodType(start, bot)

        if debug_scope is not None:
            log.debug("Setting debug_scope (debug_scope)")
            setattr(bot, "__debug_scope", debug_scope)

        if add_get:
            from .get_helpers import get, get_emoji, get_role

            log.debug("Adding bot.get (add_get)")
            bot._http.get_emoji = types.MethodType(get_emoji, bot._http)
            bot._http.get_role = types.MethodType(get_role, bot._http)
            bot.get = types.MethodType(get, bot)

        if add_subcommand:
            from .subcommands import subcommand_base

            log.debug("Adding bot.subcommand_base (add_subcommand)")
            bot.subcommand_base = types.MethodType(subcommand_base, bot)

        if modify_callbacks:
            from .callbacks import component, modal

            log.debug("Modifying component callbacks (modify_callbacks)")
            bot.component = types.MethodType(component, bot)

            bot.event(self._on_component, name="on_component")
            log.debug("Registered on_component")

            log.debug("Modifying modal callbacks (modify_callbacks)")
            bot.modal = types.MethodType(modal, bot)

            bot.event(self._on_modal, name="on_modal")
            log.debug("Registered on_modal")

        if modify_command:
            from .commands import command

            log.debug("Modifying bot.command (modify_command)")
            bot.old_command = bot.command
            bot.command = types.MethodType(command, bot)

        log.info("Hooks applied")

    async def _on_component(self, ctx: ComponentContext):
        """on_component callback for modified callbacks."""
        websocket = self.client._websocket
        if any(
            any(hasattr(func, "startswith") or hasattr(func, "regex") for func in funcs)
            for _, funcs in websocket._dispatch.events.items()
        ):
            for decorator_custom_id, funcs in websocket._dispatch.events.items():
                for func in funcs:
                    if hasattr(func, "startswith"):
                        if ctx.data.custom_id.startswith(
                            decorator_custom_id.replace("component_startswith_", "")
                        ):
                            log.info(f"{func} startswith {func.startswith} matched")
                            return websocket._dispatch.dispatch(decorator_custom_id, ctx)
                    elif hasattr(func, "regex") and fullmatch(
                        func.regex,
                        ctx.data.custom_id.replace("component_regex_", ""),
                    ):
                        log.info(f"{func} regex {func.regex} matched")
                        return websocket._dispatch.dispatch(decorator_custom_id, ctx)

    async def _on_modal(self, ctx: CommandContext):
        """on_modal callback for modified callbacks."""
        websocket = self.client._websocket
        if any(
            any(hasattr(func, "startswith") or hasattr(func, "regex") for func in funcs)
            for _, funcs in websocket._dispatch.events.items()
        ):
            for decorator_custom_id, funcs in websocket._dispatch.events.items():
                for func in funcs:
                    if hasattr(func, "startswith"):
                        if ctx.data.custom_id.startswith(
                            decorator_custom_id.replace("modal_startswith_", "")
                        ):
                            log.info(f"{func} startswith {func.startswith} matched")
                            return websocket._dispatch.dispatch(decorator_custom_id, ctx)
                    elif hasattr(func, "regex") and fullmatch(
                        func.regex,
                        ctx.data.custom_id.replace("modal_regex_", ""),
                    ):
                        log.info(f"{func} regex {func.regex} matched")
                        return websocket._dispatch.dispatch(decorator_custom_id, ctx)


def setup(
    bot: Client,
    *,
    ignore_warning: bool = False,
    debug_scope: Optional[Union[int, Guild, List[int], List[Guild]]] = None,
    add_get: bool = True,
    add_subcommand: bool = True,
    modify_callbacks: bool = True,
    modify_command: bool = True,
) -> Enhanced:
    """
    This function initializes the core of the library, `Enhanced`.

    It applies hooks to the client for additional and modified features.

    ```py
    # main.py
    client.load("interactions.ext.enhanced", ...)  # optional args/kwargs
    ```

    Parameters:

    * `(?)client: Client`: The client instance. Not required if using `client.load("interactions.ext.enhanced", ...)`.
    * `?ignore_warning: bool`: Whether to ignore the warning. Defaults to `False`.
    * `?debug_scope: int | Guild | list[int] | list[Guild]`: The debug scope to apply to global commands.
    * `?add_get: bool`: Whether to add the `get()` helper function. Defaults to `True`.
    * `?add_subcommand: bool`: Whether to add subcommand hooks to the client. Defaults to `True`.
    * `?modify_callbacks: bool`: Whether to modify callback decorators. Defaults to `True`.
    * `?modify_command: bool`: Whether to modify the command decorator. Defaults to `True`.
    """
    log.info("Setting up Enhanced")
    return Enhanced(
        bot,
        ignore_warning=ignore_warning,
        debug_scope=debug_scope,
        add_get=add_get,
        add_subcommand=add_subcommand,
        modify_callbacks=modify_callbacks,
        modify_command=modify_command,
    )
