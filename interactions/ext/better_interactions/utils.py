from interactions import Button, SelectMenu
from interactions import ActionRow as AR
from typing import Union, List


def ActionRow(*args: Union[Button, SelectMenu]) -> AR:
    """
    A helper function that passes arguments to `ActionRow`

    :param *args: The components to add to the ActionRow
    :type *args: Union[Button, SelectMenu]
    :return: The ActionRow
    :rtype: ActionRow
    """
    return AR(components=list(args))


def spread_to_rows(
    *components: Union[AR, Button, SelectMenu], max_in_row: int = 5
) -> List[AR]:
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
    # todo: incorrect format errors
    if not components or len(components) > 25:
        raise ValueError("Number of components should be between 1 and 25.")
    if not 1 <= max_in_row <= 5:
        raise ValueError("max_in_row should be between 1 and 5.")

    rows = []
    action_row = []
    for component in list(components):
        if component is not None and isinstance(component, Button):
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
            elif isinstance(component, SelectMenu):
                rows.append(ActionRow(component))
    if action_row:
        rows.append(ActionRow(*action_row))

    if len(rows) > 5:
        raise ValueError("Number of rows exceeds 5.")

    return rows
