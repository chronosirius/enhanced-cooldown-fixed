from interactions import (
    OptionType,
    User,
    Channel,
    Role,
    Choice,
    ChannelType,
)
from typing import (
    List,
    Optional,
    Union,
)


class BetterOption:
    """
    An alternative way of providing options.
    ```py
    async def command(ctx, name: BetterOption(int, "description") = 5):
        ...
    ```

    :param Union[type, int, OptionType] type: The type of the option.
    :param Optional[str] description?: The description of the option.
    :param Optional[str] name?: The name of the option.
    :param Optional[List[Choice]] choices?: The choices of the option.
    :param Optional[List[ChannelType]] channel_types?: The channel types of the option.
    :param Optional[int] min_value?: The minimum value of the option.
    :param Optional[int] max_value?: The maximum value of the option.
    :param Optional[bool] autocomplete?: Whether the option should autocomplete.
    :param Optional[bool] focused?: Whether the option should be focused.
    :param Optional[str] value?: The value of the option.
    """

    def __init__(
        self,
        type: Union[type, int, OptionType],
        description: Optional[str] = None,
        name: Optional[str] = None,
        choices: Optional[List[Choice]] = None,
        channel_types: Optional[List[ChannelType]] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        autocomplete: Optional[bool] = None,
        focused: Optional[bool] = None,
        value: Optional[str] = None,
    ):
        if isinstance(type, int):
            self.type = type
        elif type in (str, int, float):
            if type is str:
                self.type = OptionType.STRING
            elif type is int:
                self.type = OptionType.INTEGER
            elif type is float:
                self.type = OptionType.NUMBER
            elif type is bool:
                self.type = OptionType.BOOLEAN
        elif isinstance(type, OptionType):
            self.type = type
        elif type is User:
            self.type = OptionType.USER
        elif type is Channel:
            self.type = OptionType.CHANNEL
        elif type is Role:
            self.type = OptionType.ROLE
        else:
            raise TypeError(f"Invalid type: {type}")

        self.description = description or "No description"
        self.name = name
        self.choices = choices
        self.channel_types = channel_types
        self.min_value = min_value
        self.max_value = max_value
        self.autocomplete = autocomplete
        self.focused = focused
        self.value = value
