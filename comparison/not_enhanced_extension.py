from random import randint

from interactions import (
    Client,
    CommandContext,
    Extension,
    Modal,
    Option,
    OptionType,
    TextInput,
    TextStyleType,
    extension_command,
    extension_listener,
)


class NotEnhanced(Extension):
    @extension_command(name="send_modal", description="Modal!")
    async def send_modal(self, ctx: CommandContext):
        example_id: int = randint(0, 999_999_999)
        modal = Modal(
            custom_id=f"modal{example_id}",
            title=f"Modal #{example_id}",
            components=[
                TextInput(
                    style=TextStyleType.SHORT,
                    custom_id=f"text_input{example_id}",
                    label="hi",
                )
            ],
        )
        await ctx.popup(modal)

    @extension_command(
        name="base2",
        description="Base 2",
        options=[
            Option(
                type=OptionType.SUB_COMMAND_GROUP,
                name="subcommand_group2",
                description="Subcommand group 2",
                options=[
                    Option(
                        type=OptionType.SUB_COMMAND,
                        name="subcommand2",
                        description="Subcommand 2",
                    ),
                    Option(
                        type=OptionType.SUB_COMMAND,
                        name="subcommand_options3",
                        description="Subcommand with options 3",
                        options=[
                            Option(
                                type=OptionType.STRING,
                                name="string3",
                                description="String 3",
                                required=True,
                            ),
                            Option(
                                type=OptionType.INTEGER,
                                name="integer3",
                                description="Integer 3",
                                required=False,
                            ),
                        ],
                    ),
                    Option(
                        type=OptionType.SUB_COMMAND,
                        name="subcommand_options4",
                        description="Subcommand with options 4",
                        options=[
                            Option(
                                type=OptionType.STRING,
                                name="string4",
                                description="String 4",
                                required=True,
                            ),
                            Option(
                                type=OptionType.INTEGER,
                                name="integer4",
                                description="Integer 4",
                                required=False,
                            ),
                        ],
                    ),
                ],
            ),
            Option(
                type=OptionType.SUB_COMMAND,
                name="subcommand_no_group2",
                description="Subcommand without group 2",
            ),
        ],
        scope=123456789,
    )
    async def an_extension_subcommand(
        ctx: CommandContext,
        sub_command_group: str = None,
        sub_command: str = None,
        string3: str = None,
        integer3: int = 5,
        string4: str = None,
        integer4: int = 5,
    ):
        if sub_command_group:
            if sub_command == "subcommand2":
                await ctx.send("Subcommand 2")
            elif sub_command == "subcommand_options3":
                await ctx.send(f"Subcommand with options 3: {string3=}, {integer3=}.")
            elif sub_command == "subcommand_options4":
                await ctx.send(f"Subcommand with options 4: {string4=}, {integer4=}.")
        elif sub_command == "subcommand_no_group2":
            await ctx.send("Subcommand without group 2")

    @extension_listener(name="on_modal")
    async def on_modal(self, ctx: CommandContext, *args, **kwargs):
        if int(ctx.data.custom_id.replace("modal", "")) >= 500_000_000:
            await ctx.send("Big modal")
        else:
            await ctx.send("Small modal")


def setup(client: Client) -> Extension:
    return NotEnhanced(client)
