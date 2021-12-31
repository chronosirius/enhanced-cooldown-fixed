import types
import interactions
from interactions.ext import wait_for

from .callback import component
from .context_menu import message_menu, user_menu
from .subcomand import subcommand


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


def setup(
    bot: interactions.Client,
    modify_component_callbacks: bool = True,
    add_context_menu: bool = True,
    add_subcommand: bool = True,
    add_method: bool = False,
    add_interaction_events: bool = False,
) -> None:
    """
    Apply hooks to a bot to add additional features

    This function is required, as importing alone won't extend the classes

    :param Client bot: The bot instance or class to apply hooks to
    :param bool modify_component_callbacks: Whether to modify the component callbacks
    :param bool add_method: If ``wait_for`` should be attached to the bot
    :param bool add_interaction_events: Whether to add ``on_message_component``, ``on_application_command``, and other interaction event
    """

    if not isinstance(bot, interactions.Client):
        raise TypeError(f"{bot.__class__.__name__} is not interactions.Client!")

    if modify_component_callbacks:
        bot.component = types.MethodType(component, bot)

        old_websocket = bot.websocket
        new_websocket = ExtendedWebSocket(
            old_websocket.intents, old_websocket.session_id, old_websocket.sequence
        )

        _replace_values(old_websocket, new_websocket)

        bot.websocket = new_websocket

    if add_context_menu:
        bot.message_menu = types.MethodType(message_menu, bot)
        bot.user_menu = types.MethodType(user_menu, bot)

    if add_subcommand:
        bot.subcommand = types.MethodType(subcommand, bot)

    if add_method or add_interaction_events:
        wait_for.setup(
            bot, add_method=add_method, add_interaction_events=add_interaction_events
        )
