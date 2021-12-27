import interactions
from interactions.ext import wait_for
import types
from typing import Any, Callable, Coroutine, Optional, Union


class ExtendedWebSocket(interactions.api.gateway.WebSocket):
    def handle_dispatch(self, event: str, data: dict) -> None:
        super().handle_dispatch(event, data)

        if event == "INTERACTION_CREATE":
            if "type" not in data:
                return

            context: interactions.ComponentContext = self.contextualize(data)

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
                        return


interactions.api.gateway.WebSocket = ExtendedWebSocket


def component(
    bot: interactions.Client,
    component: Union[str, interactions.Button, interactions.SelectMenu],
    startswith: Optional[bool] = False,
) -> Callable[..., Any]:
    """
    A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
    events involving components.
    The structure for a component callback:
    .. code-block:: python
        # Method 1
        @component(interactions.Button(
            style=interactions.ButtonStyle.PRIMARY,
            label="click me!",
            custom_id="click_me_button",
        ))
        async def button_response(ctx):
            ...
        # Method 2
        @component("custom_id")
        async def button_response(ctx):
            ...
    The context of the component callback decorator inherits the same
    as of the command decorator.
    :param component: The component you wish to callback for.
    :type component: Union[str, Button, SelectMenu]
    :param startswith: Whether the component should be matched by the start of the custom_id.
    :type startswith: bool
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Any:
        payload: str = (
            interactions.Component(**component._json).custom_id
            if isinstance(component, (interactions.Button, interactions.SelectMenu))
            else component
        )
        if not startswith:
            coro.startswith = False
            return bot.event(coro, name=f"component_{payload}")
        coro.startswith = True
        return bot.event(coro, name=f"component_startswith_{payload}")

    return decorator


def setup(
    bot: interactions.Client,
    modify_component_callbacks: bool = True,
    use_wait_for: bool = False,
) -> None:
    """
    Apply hooks to a bot to add additional features

    This function is required, as importing alone won't extend the classes

    :param Client bot: The bot instance or class to apply hooks to
    :param bool modify_component_callbacks: Whether to modify the component callbacks
    :param bool use_wait_for: Whether to use `interactions-wait-for`
    """

    if not isinstance(bot, interactions.Client):
        raise TypeError(f"{bot.__class__.__name__} is not interactions.Client!")

    if modify_component_callbacks:
        bot.component = types.MethodType(component, bot)
    if use_wait_for:
        wait_for.setup(bot, add_method=True)
