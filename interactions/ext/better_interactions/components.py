from typing import List, Optional, Union

from interactions import ActionRow as AR
from interactions import Button as B
from interactions import ButtonStyle, Component, Emoji
from interactions import Modal as M
from interactions import SelectMenu as SM
from interactions import SelectOption
from interactions import TextInput as TI
from interactions import TextStyleType as TST

from ._logging import get_logger

log = get_logger("components")


def ActionRow(*args: Union[B, SM]) -> AR:
    """
    A helper function that passes arguments to `ActionRow`

    :param *args: The components to add to the ActionRow
    :type *args: Union[Button, SelectMenu]
    :return: The ActionRow
    :rtype: ActionRow
    """
    log.debug(f"Creating ActionRow with {list(args)}")
    return AR(components=list(args))


def Button(
    style: Union[ButtonStyle, int],
    label: str,
    *,
    custom_id: Optional[str] = None,
    url: Optional[str] = None,
    emoji: Optional[Emoji] = None,
    disabled: Optional[bool] = False,
) -> B:
    """
    A helper function that passes arguments to `Button`

    :param style: The style of the button
    :type style: Union[ButtonStyle, int]
    :param label: The label of the button
    :type label: str
    :param custom_id: The custom id of the Button
    :type custom_id: Optional[str]
    :param url: The url of the Button
    :type url: Optional[str]
    :param emoji: The emoji of the Button
    :type emoji: Optional[Emoji]
    :param disabled: Whether the Button is disabled
    :type disabled: Optional[bool]
    :return: The Button
    :rtype: Button
    """
    log.debug(
        f"Creating Button with {style=}, {label=}, {custom_id=}, {url=}, {emoji=}, {disabled=}"
    )
    if custom_id and url:
        raise ValueError("`custom_id` and `url` cannot be used together!")

    if not (custom_id or url):
        raise ValueError("`custom_id` or `url` must be specified!")

    if style == ButtonStyle.LINK and not url:
        raise ValueError("`url` must be specified if `style` is `ButtonStyle.LINK`!")
    elif url and style != ButtonStyle.LINK:
        raise ValueError("`url` can only be specified if `style` is `ButtonStyle.LINK`!")

    if style != ButtonStyle.LINK and not custom_id:
        raise ValueError("`custom_id` must be specified if `style` is not `ButtonStyle.LINK`!")
    elif custom_id and style == ButtonStyle.LINK:
        raise ValueError("`custom_id` can only be specified if `style` is not `ButtonStyle.LINK`!")

    return B(
        style=style,
        label=label,
        custom_id=custom_id,
        url=url,
        emoji=emoji,
        disabled=disabled,
    )


def SelectMenu(
    options: List[SelectOption],
    custom_id: str,
    *,
    placeholder: Optional[str] = None,
    min_values: Optional[int] = None,
    max_values: Optional[int] = None,
    disabled: Optional[bool] = False,
) -> SM:
    """
    A helper function that passes arguments to `SelectMenu`

    :param options: The options to display
    :type options: List[SelectOption]
    :param custom_id: The custom id of the SelectMenu
    :type custom_id: str
    :param placeholder: The placeholder of the SelectMenu
    :type placeholder: Optional[str]
    :param min_values: The minimum number of values that can be selected
    :type min_values: Optional[int]
    :param max_values: The maximum number of values that can be selected
    :type max_values: Optional[int]
    :param disabled: Whether the SelectMenu is disabled
    :type disabled: Optional[bool]
    :return: The SelectMenu
    :rtype: SelectMenu
    """
    log.debug(
        f"Creating SelectMenu with {options=}, {custom_id=}, {placeholder=}, {min_values=}, {max_values=}, {disabled=}"
    )
    return SM(
        options=options,
        custom_id=custom_id,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
    )


def spread_to_rows(*components: Union[AR, B, SM], max_in_row: int = 5) -> List[AR]:
    """
    A helper function that spreads your components into `ActionRow`s of a set size

    :param *components: The components to spread, use `None` to explicit start a new row
    :type *components: Union[AR, Button, SelectMenu]
    :param max_in_row: The maximum number of components in each row
    :type max_in_row: int
    :return: The components spread to rows
    :rtype: List[ActionRow]
    :raises: ValueError: Too many or few components or rows
    """
    log.debug(f"spread_to_rows with {components=}, {max_in_row=}")
    # todo: incorrect format errors
    if not components or len(components) > 25:
        raise ValueError("Number of components should be between 1 and 25.")
    if not 1 <= max_in_row <= 5:
        raise ValueError("max_in_row should be between 1 and 5.")

    rows = []
    action_row = []
    for component in list(components):
        if component is not None and isinstance(component, B):
            action_row.append(component)

            if len(action_row) == max_in_row:
                rows.append(ActionRow(*action_row))
                action_row = []

            continue

        if action_row:
            rows.append(ActionRow(*action_row))
            action_row = []

        if component is not None:
            if isinstance(component, AR):
                rows.append(component)
            elif isinstance(component, SM):
                rows.append(ActionRow(component))
    if action_row:
        rows.append(ActionRow(*action_row))

    if len(rows) > 5:
        raise ValueError("Number of rows exceeds 5.")

    return rows


def TextInput(
    custom_id: str,
    label: str,
    style: Optional[TST] = TST.SHORT,
    value: Optional[str] = None,
    required: Optional[bool] = True,
    placeholder: Optional[str] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> TI:
    return TI(
        custom_id=custom_id,
        label=label,
        style=style,
        value=value,
        required=required,
        placeholder=placeholder,
        min_length=min_length,
        max_length=max_length,
    )


def Modal(custom_id: str, title: str, components: List[Component]) -> M:
    return M(custom_id=custom_id, title=title, components=components)
