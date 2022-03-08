from functools import wraps
from re import compile
from typing import Any, Callable, Coroutine, Optional, Union

from interactions import Client, Button, SelectMenu, Modal, Component

from ._logging import get_logger

log = get_logger("callback")


def component(
    bot: Client,
    component: Union[str, Button, SelectMenu],
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

    def decorator(coro: Coroutine) -> Callable[..., Any]:
        if hasattr(coro, "__extension"):
            return coro

        payload: str = (
            Component(**component._json).custom_id
            if isinstance(component, (Button, SelectMenu))
            else component
        )
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        if startswith:
            coro.startswith = True
            bot.event(coro, name=f"component_startswith_{payload}")
        elif regex:
            coro.regex = compile(payload)
            bot.event(coro, name=f"component_regex_{payload}")
        else:
            bot.event(coro, name=f"component_{payload}")

        log.debug(f"Component callback, {startswith=}, {regex=}")
        return coro

    return decorator


def modal(
    bot: Client,
    modal: Union[Modal, str],
    startswith: Optional[bool] = False,
    regex: Optional[bool] = False,
) -> Callable[..., Any]:
    """
    A decorator for listening to ``INTERACTION_CREATE`` dispatched gateway
    events involving modals.

    The structure for a modal callback:
    .. code-block:: python
        @modal(interactions.Modal(
            interactions.TextInput(
                style=interactions.TextStyleType.PARAGRAPH,
                custom_id="how_was_your_day_field",
                label="How has your day been?",
                placeholder="Well, so far...",
            ),
        ))
        async def modal_response(ctx):
            ...

    The context of the modal callback decorator inherits the same
    as of the component decorator.

    :param modal: The modal or custom_id of modal you wish to callback for.
    :type modal: Union[Modal, str]
    :param startswith: Whether the modal should be matched by the start of the custom_id.
    :type startswith: bool
    :param regex: Whether to use regex matching for the modal using value of custom_id.
    :type regex: bool
    :return: A callable response.
    :rtype: Callable[..., Any]
    """

    def decorator(coro: Coroutine) -> Any:
        if hasattr(coro, "__extension"):
            return coro

        payload: str = modal.custom_id if isinstance(modal, Modal) else modal
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        if startswith:
            coro.startswith = True
            bot.event(coro, name=f"modal_startswith_{payload}")
        elif regex:
            coro.regex = compile(payload)
            bot.event(coro, name=f"modal_regex_{payload}")
        else:
            bot.event(coro, name=f"modal_{payload}")

        log.debug(f"Modal callback, {startswith=}, {regex=}")
        return coro

    return decorator


@wraps(Client.component)
def extension_component(
    component: Union[str, Button, SelectMenu],
    startswith: Optional[bool] = False,
    regex: Optional[bool] = False,
):
    def decorator(func):
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        func.__extension = True
        payload: str = (
            Component(**component._json).custom_id
            if isinstance(component, (Button, SelectMenu))
            else component
        )

        if startswith:
            func.startswith = True
            payload = f"startswith_{payload}"
        elif regex:
            func.regex = compile(payload)
            payload = f"regex_{payload}"

        log.debug(f"Extension component callback, {startswith=}, {regex=}")

        func.__component_data__ = (
            (),
            {"component": payload, "startswith": startswith, "regex": regex},
        )
        return func

    return decorator


@wraps(Client.modal)
def extension_modal(
    modal: Union[Modal, str],
    startswith: Optional[bool] = False,
    regex: Optional[bool] = False,
):
    def decorator(func):
        if startswith and regex:
            log.error("Cannot use both startswith and regex.")
            raise ValueError("Cannot use both startswith and regex!")

        func.__extension = True
        payload: str = modal.custom_id if isinstance(modal, Modal) else modal

        if startswith:
            func.startswith = True
            payload = f"startswith_{payload}"
        elif regex:
            func.regex = compile(payload)
            payload = f"regex_{payload}"

        log.debug(f"Extension modal callback, {startswith=}, {regex=}")

        func.__modal_data__ = (
            (),
            {"modal": payload, "startswith": startswith, "regex": regex},
        )
        return func

    return decorator
