import types
from inspect import getmembers, iscoroutinefunction
from logging import Logger
from re import compile, match

import interactions
from interactions import Client

from ._logging import get_logger

log: Logger = get_logger("extension")


def sync_subcommands(self):
    client = self.client
    if any(
        hasattr(func, "__subcommand__")
        for _, func in getmembers(self, predicate=iscoroutinefunction)
    ):
        bases = {
            func.__base__: func.__data__
            for _, func in getmembers(self, predicate=iscoroutinefunction)
            if hasattr(func, "__subcommand__")
        }
        commands = []

        for subcommand in bases.values():
            client.event(subcommand.inner, name=f"command_{subcommand.base}")
            commands.extend(subcommand.raw_commands)

        if client._automate_sync:
            if client._loop.is_running():
                [
                    client._loop.create_task(client._synchronize(command))
                    for command in commands
                ]
            else:
                [
                    client._loop.run_until_complete(client._synchronize(command))
                    for command in commands
                ]
        for subcommand in bases.values():
            scope = subcommand.scope
            if scope is not None:
                if isinstance(scope, list):
                    [
                        client._scopes.add(_ if isinstance(_, int) else _.id)
                        for _ in scope
                    ]
                else:
                    client._scopes.add(scope if isinstance(scope, int) else scope.id)


class BetterExtension(interactions.client.Extension):
    def __new__(cls, client: interactions.Client, *args, **kwargs):
        self = super().__new__(cls, client, *args, **kwargs)
        log.debug("Syncing subcommands...")
        sync_subcommands(self)
        log.debug("Synced subcommands")
        return self


class BetterInteractions(interactions.client.Extension):
    def __init__(
        self,
        bot: Client,
        modify_component_callbacks: bool = True,
        add_subcommand: bool = True,
        add_method: bool = False,
        add_interaction_events: bool = False,
        modify_command: bool = True,
    ):
        """
        Apply hooks to a bot to add additional features

        This function is required, as importing alone won't extend the classes

        :param Client bot: The bot instance or class to apply hooks to
        :param bool modify_component_callbacks: Whether to modify the component callbacks
        :param bool add_subcommand: Whether to add the subcommand
        :param bool add_method: If ``wait_for`` should be attached to the bot
        :param bool add_interaction_events: Whether to add ``on_message_component``, ``on_application_command``, and other interaction event
        """
        if not isinstance(bot, interactions.Client):
            log.critical("The bot must be an instance of Client")
            raise TypeError(f"{bot.__class__.__name__} is not interactions.Client!")
        else:
            log.debug("The bot is an instance of Client")

        if modify_component_callbacks:
            from .callback import component

            log.debug("Modifying component callbacks (modify_component_callbacks)")
            bot.component = types.MethodType(component, bot)

            bot.event(self.on_component, "on_component")
            log.debug("Registered on_component")

        if add_subcommand:
            from .subcommands import base

            log.debug("Adding bot.base (add_subcommand)")
            bot.base = types.MethodType(base, bot)

        if add_method or add_interaction_events:
            log.debug("Adding bot.wait_for (add_method or add_interaction_events)")
            from interactions.ext import wait_for

            wait_for.setup(
                bot,
                add_method=add_method,
                add_interaction_events=add_interaction_events,
            )

        if modify_command:
            from .commands import command

            log.debug("Modifying bot.command (modify_command)")
            bot.old_command = bot.command
            bot.command = types.MethodType(command, bot)

        log.info("Hooks applied")

    async def on_component(self, ctx: interactions.ComponentContext):
        bot = self.client
        websocket = bot._websocket
        # startswith component callbacks
        if any(
            any(hasattr(func, "startswith") or hasattr(func, "regex") for func in funcs)
            for custom_id, funcs in websocket._dispatch.events.items()
        ):
            for custom_id, funcs in websocket._dispatch.events.items():
                for func in funcs:
                    if hasattr(func, "startswith"):
                        if ctx.data.custom_id.startswith(
                            custom_id.replace("component_startswith_", "")
                        ):
                            if ctx.responded:
                                ctx.responded = False
                            log.info(f"{func} startswith {func.startswith} matched")
                            websocket._dispatch.dispatch(custom_id, ctx)
                    elif hasattr(func, "regex"):
                        regex = compile(func.regex)
                        print("regex", regex)
                        custom_id.replace("component_regex_", "")
                        print("fullmatch", match(regex, custom_id))
                        if match(regex, custom_id):
                            if ctx.responded:
                                ctx.responded = False
                            log.info(f"{func} regex {func.regex} matched")
                            websocket._dispatch.dispatch(custom_id, ctx)


def setup(
    bot: Client,
    modify_component_callbacks: bool = True,
    add_subcommand: bool = True,
    add_method: bool = False,
    add_interaction_events: bool = False,
    modify_command: bool = True,
) -> None:
    """
    Setup the extension

    This function is required, as importing alone won't extend the classes

    :param Client bot: The bot instance or class to apply hooks to
    :param bool modify_component_callbacks: Whether to modify the component callbacks
    :param bool add_subcommand: Whether to add the subcommand
    :param bool add_method: If ``wait_for`` should be attached to the bot
    :param bool add_interaction_events: Whether to add ``on_message_component``, ``on_application_command``, and other interaction event
    """
    log.info("Setting up BetterInteractions")
    return BetterInteractions(
        bot,
        modify_component_callbacks,
        add_subcommand,
        add_method,
        add_interaction_events,
        modify_command,
    )
