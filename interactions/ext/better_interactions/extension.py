import types
import interactions
from interactions import Client
from interactions.ext import wait_for

# from asyncio import iscoroutinefunction
from inspect import getmembers, iscoroutinefunction

from .callback import component
from .subcomand import base


class ExtendedWebSocket(interactions.api.gateway.WebSocket):
    def handle_dispatch(self, event: str, data: dict) -> None:
        super().handle_dispatch(event, data)

        if event == "INTERACTION_CREATE":
            if "type" not in data:
                return

            context: interactions.ComponentContext = self.contextualize(data)

            # startswith component callbacks
            if context.data.custom_id:
                for event in self.dispatch.events:
                    try:
                        startswith = self.dispatch.events[event][0].startswith
                    except AttributeError:
                        continue
                    if startswith and context.data.custom_id.startswith(
                        event.replace("component_startswith_", "")
                    ):
                        self.dispatch.dispatch(event, context)


interactions.api.gateway.WebSocket = ExtendedWebSocket


def sync_subcommands(self):
    print("original init")
    client = self.client
    print("E", getmembers(self, predicate=iscoroutinefunction))
    # get the methods
    if any(
        hasattr(func, "__subcommand__")
        for _, func in getmembers(self, predicate=iscoroutinefunction)
    ):
        bases = {
            func.__base__: func.__data__
            for _, func in getmembers(self, predicate=iscoroutinefunction)
            if hasattr(func, "__subcommand__")
        }
        print(bases)
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


class Extension(interactions.client.Extension):
    def __init__(self, client: Client, *args, **kwargs):
        self.sync_subcommands()
    
    def sync_subcommands(self):
        print("original init")
        client = self.client
        print("E", getmembers(self, predicate=iscoroutinefunction))
        # get the methods
        if any(
            hasattr(func, "__subcommand__")
            for _, func in getmembers(self, predicate=iscoroutinefunction)
        ):
            bases = {
                func.__base__: func.__data__
                for _, func in getmembers(self, predicate=iscoroutinefunction)
                if hasattr(func, "__subcommand__")
            }
            print(bases)
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




interactions.client.Extension = Extension


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
            raise TypeError(f"{bot.__class__.__name__} is not interactions.Client!")

        if modify_component_callbacks:
            bot.component = types.MethodType(component, bot)

            old_websocket = bot._websocket
            new_websocket = ExtendedWebSocket(
                old_websocket.intents, old_websocket.session_id, old_websocket.sequence
            )

            _replace_values(old_websocket, new_websocket)

            bot._websocket = new_websocket

        if add_subcommand:
            bot.base = types.MethodType(base, bot)

        if add_method or add_interaction_events:
            wait_for.setup(
                bot,
                add_method=add_method,
                add_interaction_events=add_interaction_events,
            )


def setup(
    bot: Client,
    modify_component_callbacks: bool = True,
    add_subcommand: bool = True,
    add_method: bool = False,
    add_interaction_events: bool = False,
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
    return BetterInteractions(
        bot,
        modify_component_callbacks,
        add_subcommand,
        add_method,
        add_interaction_events,
    )
