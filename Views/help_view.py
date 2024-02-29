from typing import Union

import discord
from discord.ext import commands


class CogSelector(discord.ui.Select):
    def __init__(self, pages: dict[commands.Cog, list[discord.Embed]]):
        self.pages = pages
        super().__init__(
            placeholder="Select a category...",
            options=[
                discord.SelectOption(
                    label=cog.qualified_name, emoji=getattr(cog, "EMOJI", None)
                )
                for cog in pages.keys()
            ],
            row=0,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        for cog, embeds in self.pages.items():
            if cog.qualified_name == self.values[0]:
                view = self.view
                view.go_to_first_page.disabled = True
                view.go_to_previous_page.disabled = True
                view.go_to_next_page.disabled = True if len(embeds) == 1 else False
                view.go_to_last_page.disabled = True if len(embeds) == 1 else False

                e = embeds[0]
                e.set_footer(text=f"Page 1 / {len(embeds)}")
                self.view.current_pages = embeds
                self.view.current_page = 0
                self.view.message = await interaction.original_message()
                await self.view.message.edit(embed=e, view=view)


class HelpView(discord.ui.View):
    def __init__(
        self,
        pages: dict[commands.Cog, list[discord.Embed]],
        *,
        interaction: discord.Interaction,
        message: Union[discord.Message, None] = None,
    ):
        super().__init__(timeout=90)

        self.current_pages: Union[list[discord.Embed], None] = None
        self.current_page: Union[int, None] = None
        self.interaction = interaction
        self.message: Union[discord.Message, None] = message
        self.add_item(CogSelector(pages=pages))

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id in (
            self.interaction.client.owner_ids,
        ) + (self.interaction.user.id,):
            return True

        await interaction.response.send_message(
            "This pagination menu cannot be controlled by you, sorry!", ephemeral=True
        )
        return False

    async def show_checked_page(
        self, interaction: discord.Interaction, page_number: int
    ) -> None:
        max_pages = len(self.current_pages)
        if max_pages > page_number >= 0:
            await self.show_page(interaction, page_number)

    async def show_page(
        self, interaction: discord.Interaction, page_number: int
    ) -> None:
        if 0 > page_number >= len(self.current_pages):
            return

        page = self.current_pages[page_number]
        await self._update_labels(page_number)
        self.current_page = page_number
        page.set_footer(text=f"Page {self.current_page + 1}")
        await interaction.response.edit_message(embed=page, view=self)

    async def _update_labels(self, page_number: int) -> None:
        self.go_to_first_page.disabled = page_number == 0
        self.go_to_previous_page.disabled = False if page_number > 0 else True
        self.go_to_next_page.disabled = (
            True if page_number + 1 >= len(self.current_pages) else False
        )
        self.go_to_last_page.disabled = page_number == len(self.current_pages) - 1

    @discord.ui.button(label="≪", style=discord.ButtonStyle.grey, row=1)
    async def go_to_first_page(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ):
        await self.show_page(interaction, 0)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple, row=1)
    async def go_to_previous_page(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ):
        await self.show_checked_page(interaction, self.current_page - 1)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, row=1)
    async def go_to_next_page(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ):
        await self.show_checked_page(interaction, self.current_page + 1)

    @discord.ui.button(label="≫", style=discord.ButtonStyle.grey, row=1)
    async def go_to_last_page(
        self, interaction: discord.Interaction, _: discord.ui.Button
    ):
        await self.show_page(interaction, len(self.current_pages) - 1)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red, row=1)
    async def quit(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.defer()
        await interaction.message.delete()
