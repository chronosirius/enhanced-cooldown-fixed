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


def sync_subcommands(self: Extension, client: Client):
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
    commands = []

    for base, subcommand in bases.items():
        base: str
        subcommand: ExternalSubcommandSetup
        client.event(subcommand.inner, name=f"command_{base}")
        commands.extend(subcommand.raw_commands)

    if client._automate_sync:
        if client._loop.is_running():
            [client._loop.create_task(client._synchronize(command)) for command in commands]
        else:
            [client._loop.run_until_complete(client._synchronize(command)) for command in commands]
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
        for func in getmembers(cls, predicate=iscoroutinefunction):
            if hasattr(func, "__command_data__"):
                scope = func.__command_data__[1].get("scope", MISSING)
                debug_scope = func.__command_data__[1].get("debug_scope", True)
                del func.__command_data__[1]["debug_scope"]
                if scope is MISSING and debug_scope and hasattr(client, "__debug_scope"):
                    func.__command_data__[1]["scope"] = client.__debug_scope

        log.debug("Syncing subcommands...")
        bases = sync_subcommands(cls, client)
        log.debug("Synced subcommands")

        self = super().__new__(cls, client, *args, **kwargs)
        for base, subcommand in bases.items():
            subcommand.set_self(self)
            commands = self._commands.get(f"command_{base}", [])
            commands.append(subcommand.inner)
            self._commands[f"command_{base}"] = commands
        return self


class Enhanced(Extension):
    """
    This is the core of this library, initialized when loading the extension.

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

        if debug_scope is not None:
            log.debug("Setting debug_scope (debug_scope)")
            setattr(bot, "__debug_scope", debug_scope)

        if add_get:
            from .command_models import get, get_role

            log.debug("Adding bot.get (add_get)")
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

            bot.event(self._on_component, "on_component")
            log.debug("Registered on_component")

            log.debug("Modifying modal callbacks (modify_callbacks)")
            bot.modal = types.MethodType(modal, bot)

            bot.event(self._on_modal, "on_modal")
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
) -> None:
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
