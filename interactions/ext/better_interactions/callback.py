from typing import Any, Callable, Coroutine, Optional, Union

import interactions

from ._logging import get_logger

log = get_logger("callback")


def component(
    bot: interactions.Client,
    component: Union[str, interactions.Button, interactions.SelectMenu],
    startswith: Optional[bool] = False,
    regex: Optional[bool] = False,
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
    :param regex: Whether to use regex matching for the component using value of custom_id.
    :type regex: bool
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Any:
        payload: str = (
            interactions.Component(**component._json).custom_id
            if isinstance(component, (interactions.Button, interactions.SelectMenu))
            else component
        )
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        if startswith:
            coro.startswith = True
            bot.event(coro, name=f"component_startswith_{payload}")
        elif regex:
            coro.regex = payload
            bot.event(coro, name=f"component_regex_{payload}")
        else:
            bot.event(coro, name=f"component_{payload}")

        log.debug(f"Component callback, {coro.startswith=}, {regex=}")
        return coro

    return decorator
