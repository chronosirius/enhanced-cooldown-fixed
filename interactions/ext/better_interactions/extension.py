import types
from inspect import getmembers, iscoroutinefunction
from logging import Logger

import interactions
from interactions import Client

from ._logging import get_logger

log: Logger = get_logger("extension")


# class ExtendedWebSocket(interactions.api.gateway.WebSocket):
#     def handle_dispatch(self, event: str, data: dict) -> None:
#         super().handle_dispatch(event, data)
#         if event == "INTERACTION_CREATE":
#             if "type" not in data:
#                 return
#             context: interactions.ComponentContext = self.contextualize(data)
#             # startswith component callbacks
#             if context.data.custom_id and any(
#                 hasattr(func, "startswith") for _, func in self.dispatch.events
#             ):
#                 for event in self.dispatch.events:
#                     if hasattr(self.dispatch.events[event], "startswith"):
#                         startswith = self.dispatch.events[event].startswith
#                         if startswith and context.data.custom_id.startswith(
#                             event.replace("component_startswith_", "")
#                         ):
#                             return self.dispatch.dispatch(event, context)


# interactions.api.gateway.WebSocket = ExtendedWebSocket


# async def on_component(self, context: interactions.ComponentContext):
#     # startswith component callbacks
#     if context.data.custom_id:
#         for event in self.dispatch.events:
#             try:
#                 startswith = self.dispatch.events[event][0].startswith
#             except AttributeError:
#                 continue
#             if startswith and context.data.custom_id.startswith(
#                 event.replace("component_startswith_", "")
#             ):
#                 self.dispatch.dispatch(event, context)


class WebSocketExtension(interactions.WebSocketClient):
    def _dispatch_event(self, event: str, data: dict):
        super()._dispatch_event(event, data)

        if event != "TYPING_START" and event == "INTERACTION_CREATE":
            _context: object = super().__contextualize(data)

            if (
                data["type"] == interactions.InteractionType.MESSAGE_COMPONENT
                and _context.data._json.get("custom_id")
                and any(
                    hasattr(func, "startswith") for _, func in self._dispatch.events
                )
            ):
                for event, func in self._dispatch.events.items():
                    if hasattr(func, "startswith") and func.startswith:
                        event.replace("components_startswith_", "")
                        self._dispatch.dispatch(event, _context)


interactions.api.gateway.WebSocketClient = WebSocketExtension


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
        # if (
        #     hasattr(client, "__modify_component_callbacks__")
        #     and "ON_COMPONENT" not in client._websocket._dispatch.events
        # ):
        #     client.__modify_component_callbacks__ = False
        #     client.event(self.on_component, "on_component")
        #     log.debug("Registered on_component")
        return self


# async def on_component(self, ctx: interactions.ComponentContext):
#     print("somethingg")
#     bot = self.client
#     websocket = bot._websocket
#     # startswith component callbacks
#     if any(
#         hasattr(func, "startswith")
#         for custom_id, func in websocket._dispatch.events.items()
#     ):
#         for custom_id, func in websocket._dispatch.events.items():
#             if hasattr(func, "startswith"):
#                 startswith = func.startswith
#                 if startswith and ctx.data.custom_id.startswith(
#                     custom_id.replace("component_startswith_", "")
#                 ):
#                     return websocket._dispatch.dispatch(custom_id, ctx)


_old_dispatch_event = None


def _new_dispatch_event(self: interactions.WebSocketClient, event: str, data: dict):
    _old_dispatch_event(self, event, data)

    if event == "INTERACTION_CREATE":
        context: interactions.ComponentContext = self.__contextualize(data)
        # startswith component callbacks
        if context.data.custom_id and any(
            hasattr(func, "startswith") for _, func in self._dispatch.events.items()
        ):
            for event in self._dispatch.events:
                if hasattr(self._dispatch.events[event], "startswith"):
                    startswith = self._dispatch.events[event].startswith
                    if startswith and context.data.custom_id.startswith(
                        event.replace("component_startswith_", "")
                    ):
                        return self._dispatch.dispatch(event, context)


def _replace_values(old, new):
    """Change all values on new to the values on old. Useful if neither object has __dict__"""
    for item in dir(old):  # can't use __dict__, this should take everything
        value = getattr(old, item)

        if hasattr(value, "__call__") or isinstance(value, property):
            # Don't need to get callables or properties, that would un-overwrite things
            continue

        try:
            new.__setattr__(item, value)
        except AttributeError:
            pass


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

            # global _old_dispatch_event
            # _old_dispatch_event = bot._websocket._dispatch_event
            # bot._websocket._dispatch_event = types.MethodType(
            #     _new_dispatch_event, bot._websocket
            # )

            # old_websocket = bot._websocket
            # new_websocket = WebSocketExtension(
            #     old_websocket._http.token,
            #     old_websocket._intents,
            #     old_websocket.session_id,
            #     old_websocket.sequence,
            # )

            # _replace_values(old_websocket, new_websocket)

            # bot._websocket = new_websocket

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
        print("somethingg")
        bot = self.client
        websocket = bot._websocket
        # startswith component callbacks
        if any(
            hasattr(func, "startswith")
            for custom_id, func in websocket._dispatch.events.items()
        ):
            for custom_id, func in websocket._dispatch.events.items():
                if hasattr(func, "startswith"):
                    startswith = func.startswith
                    if startswith and ctx.data.custom_id.startswith(
                        custom_id.replace("component_startswith_", "")
                    ):
                        return websocket._dispatch.dispatch(custom_id, ctx)


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
