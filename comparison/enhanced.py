from random import randint

from typing_extensions import Annotated

from interactions import ActionRow, Button, ButtonStyle, Client, CommandContext, ComponentContext
from interactions.ext.enhanced import EnhancedOption, GroupSetup, SubcommandSetup, option

client = Client("...")
client.load("interactions.ext.enhanced", debug_scope=123456789)


@client.event
async def on_ready():
    print("Ready!")


@client.command(debug_scope=False)
async def send_buttons(ctx: CommandContext):
    """Sends buttons!"""
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


@client.component("primary", startswith=True)
async def primary_callback(ctx: ComponentContext):
    custom_id: str = ctx.data.custom_id
    await ctx.send(f"You clicked on a primary button! ID is {custom_id.replace('primary', '')}")


@client.component("secondary", startswith=True)
async def secondary_callback(ctx: ComponentContext):
    custom_id: str = ctx.data.custom_id
    await ctx.send(f"You clicked on a secondary button! ID is {custom_id.replace('secondary', '')}")


@client.command()
async def command_with_options(
    ctx: CommandContext,
    string: Annotated[str, EnhancedOption(description="String")],
    integer: Annotated[int, EnhancedOption(description="Integer")] = 5,
):
    """Command with options!"""
    await ctx.send(f"String: {string}, Integer: {integer}")


@client.command()
@option(str, "string2", "String 2")
@option(int, "integer2", "Integer 2", required=False)
async def command_with_options2(ctx: CommandContext, string2: str, integer2: int = 5):
    """Command with options 2!"""
    await ctx.send(f"Command with options 2: {string2=}, {integer2=}.")


base: SubcommandSetup = client.subcommand_base("base", description="Base")
subcommand_group: GroupSetup = base.group("subcommand_group")


@subcommand_group.subcommand()
async def subcommand(ctx: CommandContext):
    """Subcommand"""
    await ctx.send("Subcommand")


@subcommand_group.subcommand()
async def subcommand_options(
    ctx: CommandContext,
    string: Annotated[str, EnhancedOption(description="String")],
    integer: Annotated[int, EnhancedOption(description="Integer")] = 5,
):
    """Subcommand with options"""
    await ctx.send(f"Subcommand with options: {string=}, {integer=}.")


@subcommand_group.subcommand()
@option(str, "string2", "String 2")
@option(int, "integer2", "Integer 2", required=False)
async def subcommand_options2(ctx: CommandContext, string2: str, integer2: int = 5):
    """Subcommand with options 2!"""
    await ctx.send(f"Subcommand with options 2: {string2=}, {integer2=}.")


@base.subcommand()
async def subcommand_no_group(ctx: CommandContext):
    """Subcommand without group"""
    await ctx.send("Subcommand without group")


base.finish()


client.load("enhanced_extension")
client.start()
