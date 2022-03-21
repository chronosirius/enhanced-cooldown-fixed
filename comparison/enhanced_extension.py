from random import randint

from typing_extensions import Annotated

from interactions import Client, CommandContext, TextStyleType
from interactions.ext.enhanced import (
    EnhancedExtension,
    EnhancedOption,
    GroupSetup,
    ExternalSubcommandSetup,
    Modal,
    TextInput,
    ext_subcommand_base,
    extension_command,
    extension_modal,
    option,
)


class VeryEnhanced(EnhancedExtension):
    @extension_command()
    async def send_modal(self, ctx: CommandContext):
        """Modal!"""
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

    base2: ExternalSubcommandSetup = ext_subcommand_base("base2", description="Base 2")
    subcommand_group2: GroupSetup = base2.group("subcommand_group2")

    @subcommand_group2.subcommand()
    async def subcommand2(self, ctx: CommandContext):
        """Subcommand 2"""
        await ctx.send("Subcommand 2")

    @subcommand_group2.subcommand()
    async def subcommand_options3(
        self,
        ctx: CommandContext,
        string3: Annotated[str, EnhancedOption(description="String")],
        integer3: Annotated[int, EnhancedOption(description="Integer")] = 5,
    ):
        """Subcommand with options 3"""
        await ctx.send(f"Subcommand with options 3: {string3=}, {integer3=}.")

    @subcommand_group2.subcommand()
    @option(str, "string4", "String 4")
    @option(int, "integer4", "Integer 4", required=False)
    async def subcommand_options4(
        self, ctx: CommandContext, string4: str, integer4: int = 5
    ):
        """Subcommand with options 4"""
        await ctx.send(f"Subcommand with options 4: {string4=}, {integer4=}.")

    @base2.subcommand()
    async def subcommand_no_group2(self, ctx: CommandContext):
        """Subcommand without group 2"""
        await ctx.send("Subcommand without group 2")

    base2.finish()

    @extension_modal("modal", startswith=True)
    async def modal_callback(self, ctx: CommandContext):
        if int(ctx.data.custom_id.replace("modal", "")) >= 500_000_000:
            await ctx.send("Big modal")
        else:
            await ctx.send("Small modal")


def setup(client: Client):
    VeryEnhanced(client)
