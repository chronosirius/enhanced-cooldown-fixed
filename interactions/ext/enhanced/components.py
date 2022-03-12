from typing import List, Optional, Union

from interactions import ActionRow as AR
from interactions import Button as B
from interactions import ButtonStyle, Emoji
from interactions import Modal as M
from interactions import SelectMenu as SM
from interactions import SelectOption as SO
from interactions import TextInput as TI
from interactions import TextStyleType as TST

from ._logging import get_logger

log = get_logger("components")


def ActionRow(*args: Union[B, SM, TI]) -> AR:
    """
    A helper function that passes arguments to `ActionRow`.

    Previous:

    ```py
    row = ActionRow(components=[...])
    ```

    Now:

    ```py
    row = ActionRow(...)
    ```

    Parameters:

    * `*args: tuple[Button | SelectMenu | TextInput]`: The components to add to the `ActionRow`.

    Returns:

    `ActionRow`
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
    A helper function that passes arguments to `Button`.

    Previous:

    ```py
    button = Button(style=1, label="1", custom_id="1", ...)
    ```

    Now:

    ```py
    button = Button(1, "1", custom_id="1", ...)
    ```

    Parameters:

    * `style: ButtonStyle | int`: The style of the button.
    * `label: str`: The label of the button.
    * `(?)custom_id: str`: The custom id of the button. *Required if the button is not a `ButtonStyle.LINK`.*
    * `(?)url: str`: The URL of the button. *Required if the button is a `ButtonStyle.LINK`.*
    * `?emoji: Emoji`: The emoji of the button.
    * `?disabled: bool`: Whether the button is disabled. Defaults to `False`.

    Returns:

    `Button`
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
    if url and style != ButtonStyle.LINK:
        raise ValueError("`url` can only be specified if `style` is `ButtonStyle.LINK`!")

    if style != ButtonStyle.LINK and not custom_id:
        raise ValueError("`custom_id` must be specified if `style` is not `ButtonStyle.LINK`!")
    if custom_id and style == ButtonStyle.LINK:
        raise ValueError("`custom_id` can only be specified if `style` is not `ButtonStyle.LINK`!")

    return B(
        style=style,
        label=label,
        custom_id=custom_id,
        url=url,
        emoji=emoji,
        disabled=disabled,
    )


def SelectOption(
    label: str,
    value: str,
    description: Optional[str] = None,
    emoji: Optional[Emoji] = None,
    disabled: Optional[bool] = False,
) -> SO:
    """
    A helper function that passes arguments to `SelectOption`.

    Before:

    ```py
    option = SelectOption(label="1", value="1", ...)
    ```

    Now:

    ```py
    option = SelectOption("1", "1", ...)
    ```

    Parameters:

    * `label: str`: The label of the option.
    * `value: str`: The value of the option.
    * `?description: str`: The description of the option.
    * `?emoji: Emoji`: The emoji of the option.
    * `?disabled: bool`: Whether the option is disabled. Defaults to `False`.

    Returns:

    `SelectOption`
    """
    log.debug(
        f"Creating SelectOption with {label=}, {value=}, {description=}, {emoji=}, {disabled=}"
    )
    return SO(
        label=label,
        value=value,
        description=description,
        emoji=emoji,
        disabled=disabled,
    )


def SelectMenu(
    custom_id: str,
    options: List[SO],
    *,
    placeholder: Optional[str] = None,
    min_values: Optional[int] = None,
    max_values: Optional[int] = None,
    disabled: Optional[bool] = False,
) -> SM:
    """
    A helper function that passes arguments to `SelectMenu`.

    Previous:

    ```py
    select = SelectMenu(custom_id="s", options=[...], ...)
    ```

    Now:

    ```py
    select = SelectMenu("s", [...], ...)
    ```

    Parameters:

    * `custom_id: str`: The custom id of the select menu.
    * `options: list[SelectOption]`: The options of the select menu.
    * `?placeholder: str`: The placeholder of the select menu.
    * `?min_values: int`: The minimum number of values that can be selected.
    * `?max_values: int`: The maximum number of values that can be selected.
    * `?disabled: bool`: Whether the select menu is disabled. Defaults to `False`.

    Returns:

    `SelectMenu`
    """
    log.debug(
        f"Creating SelectMenu with {custom_id=}, {options=}, {placeholder=}, {min_values=}, {max_values=}, {disabled=}"
    )
    return SM(
        custom_id=custom_id,
        options=options,
        placeholder=placeholder,
        min_values=min_values,
        max_values=max_values,
        disabled=disabled,
    )


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
    """
    A helper function that passes arguments to `TextInput`.

    Before:

    ```py
    ti = TextInput(custom_id="ti", label="ti", style=1, ...)
    ```

    Now:

    ```py
    ti = TextInput("ti", "ti", 1, ...)
    ```

    Parameters:

    * `custom_id: str`: The custom id of the text input.
    * `label: str`: The label of the text input.
    * `?style: TextInputStyle | int`: The style of the text input.
    * `?value: str`: The value of the text input.
    * `?required: bool`: Whether the text input is required. Defaults to `True`.
    * `?placeholder: str`: The placeholder of the text input.
    * `?min_length: int`: The minimum length of the text input.
    * `?max_length: int`: The maximum length of the text input.

    Returns:

    `TextInput`
    """
    log.debug(
        f"Creating TextInput with {custom_id=}, {label=}, {style=}, {value=}, {required=}, {placeholder=}, {min_length=}, {max_length=}"
    )
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


def Modal(custom_id: str, title: str, components: List[TI]) -> M:
    """
    A helper function that passes arguments to `Modal`.

    Before:

    ```py
    modal = Modal(custom_id="modal", title="Modal", components=[...])
    ```

    Now:

    ```py
    modal = Modal("modal", "Modal", [...])
    ```

    Parameters:

    * `custom_id: str`: The custom id of the modal.
    * `title: str`: The title of the modal.
    * `components: list[TextInput]`: The components of the modal.

    Returns:

    `Modal`
    """
    log.debug(f"Creating Modal with {custom_id=}, {title=}, {components=}")
    return M(custom_id=custom_id, title=title, components=components)


def spread_to_rows(*components: Union[AR, B, SM], max_in_row: int = 5) -> List[AR]:
    """
    A helper function that spreads your components into `ActionRow`s of a set size.

    ```py
    rows = spread_to_rows(..., max_in_row=...)
    ```

    Parameters:

    * `*components: tuple[ActionRow | Button | SelectMenu]`: The components to spread, use `None` to explicit start a new row.
    * `?max_in_row: int`: The maximum number of components in a row. Defaults to `5`.

    Returns:

    `list[ActionRow]`
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
