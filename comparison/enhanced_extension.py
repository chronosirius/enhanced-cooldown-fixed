from random import randint

from typing_extensions import Annotated

from enhanced.interactions.ext.enhanced.subcommands import ext_subcommand_base
from interactions import Client, CommandContext, Modal, TextInput, TextStyleType
from interactions.ext.enhanced import (
    EnhancedExtension,
    EnhancedOption,
    ExternalSubcommandSetup,
    Modal,
    TextInput,
    ext_subcommand_base,
    extension_command,
    extension_modal,
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

    @base2.subcommand(group="subcommand_group2")
    async def subcommand2(self, ctx: CommandContext):
        """Subcommand 2"""
        await ctx.send("Subcommand 2")

    @base2.subcommand(group="subcommand_group2")
    async def subcommand_options2(
        self,
        ctx: CommandContext,
        string: Annotated[str, EnhancedOption(description="String")],
        integer: Annotated[int, EnhancedOption(description="Integer")] = 5,
    ):
        """Subcommand with options 2"""
        await ctx.send(f"Subcommand with options 2: {string=}, {integer=}.")

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
