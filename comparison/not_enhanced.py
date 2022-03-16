from random import randint

from interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    Client,
    CommandContext,
    ComponentContext,
    Option,
    OptionType,
)

client = Client("...")


@client.event
async def on_ready():
    print("Ready!")


@client.command(name="send_buttons", description="Sends buttons!", scope=None)
async def send_buttons(ctx: CommandContext):
    example_id: int = randint(0, 999_999_999)
    await ctx.send(
        "Pong!",
        components=ActionRow(
            components=[
                Button(
                    style=ButtonStyle.PRIMARY,
                    custom_id=f"primary{example_id}",
                    label="Primary",
                ),
                Button(
                    style=ButtonStyle.SECONDARY,
                    custom_id=f"secondary{example_id}",
                    label="Secondary",
                ),
            ]
        ),
    )


@client.event
async def on_component(ctx: ComponentContext):
    custom_id: str = ctx.data.custom_id
    if custom_id.startswith("primary"):
        await ctx.send(f"You clicked on a primary button! ID is {custom_id.replace('primary', '')}")
    elif custom_id.startswith("secondary"):
        await ctx.send(
            f"You clicked on a secondary button! ID is {custom_id.replace('secondary', '')}"
        )


@client.command(
    name="command_with_options",
    description="Command with options!",
    options=[
        Option(
            type=OptionType.STRING,
            name="string",
            description="String",
            required=True,
        ),
        Option(
            type=OptionType.INTEGER,
            name="integer",
            description="Integer",
            required=False,
        ),
    ],
    scope=123456789,
)
async def command_with_options(ctx: CommandContext, string: str, integer: int = 5):
    await ctx.send(f"Command with options: {string=}, {integer=}.")


@client.command(
    name="base",
    description="Base",
    options=[
        Option(
            type=OptionType.SUB_COMMAND_GROUP,
            name="subcommand_group",
            description="Subcommand group",
            options=[
                Option(
                    type=OptionType.SUB_COMMAND,
                    name="subcommand",
                    description="Subcommand",
                ),
                Option(
                    type=OptionType.SUB_COMMAND,
                    name="subcommand_options",
                    description="Subcommand with options",
                    options=[
                        Option(
                            type=OptionType.STRING,
                            name="string",
                            description="String",
                            required=True,
                        ),
                        Option(
                            type=OptionType.INTEGER,
                            name="integer",
                            description="Integer",
                            required=False,
                        ),
                    ],
                ),
            ],
        ),
        Option(
            type=OptionType.SUB_COMMAND,
            name="subcommand_no_group",
            description="Subcommand without group",
        ),
    ],
    scope=123456789,
)
async def a_subcommand(
    ctx: CommandContext,
    sub_command_group: str = None,
    sub_command: str = None,
    string: str = None,
    integer: int = 5,
):
    if sub_command_group:
        if sub_command == "subcommand":
            await ctx.send("Subcommand")
        elif sub_command == "subcommand_options":
            await ctx.send(f"Subcommand with options: {string=}, {integer=}.")
    elif sub_command == "subcommand_no_group":
        await ctx.send("Subcommand without group")


client.load("not_enhanced_extension")
client.start()
