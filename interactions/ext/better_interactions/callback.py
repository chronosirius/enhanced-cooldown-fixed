from typing import Union, Callable, Optional, Any, Coroutine
import interactions

from .context_menu import message_menu, user_menu
from .subcomand import subcommand


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
