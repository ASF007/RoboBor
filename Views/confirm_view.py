# imports
import random
from typing import Optional

from discord import ButtonStyle, Interaction
from discord.ui import View, Button, button
from discord.ext.commands import Context

class ConfirmView(View):
    def __init__(self, ctx: Context, confirm_label: str = "Confirm!", success_msg: str = "done..", timeout_msg = "timed out..", timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.confirm_callback.label = confirm_label
        self.ctx = ctx
        self.success_msg = success_msg
        self.timeout_msg = timeout_msg
        self.value = None
        self.bot = self.ctx.bot
        self._response = self.bot.config.get("button_responses")


    @button(style=ButtonStyle.green)
    async def confirm_callback(self, interaction: Interaction, button: Button) -> None:
        """Sets the value to true, meaning the user has confirmed the action."""
        self.value = True 
        self.stop()
        button.disabled = True
        self.remove_item(self.cancel_callback)
        await interaction.response.edit_message(
            content=f"{self.bot.emoji.get('confirm')} **{self.success_msg}**", 
            view=self
        )


    @button(label = "Cancel", style=ButtonStyle.red)
    async def cancel_callback(self, interaction: Interaction, button: Button) -> None:
        """Vice versa of the confirm button."""
        self.value = False
        self.stop()
        button.disabled = True
        self.remove_item(self.confirm_callback)
        await interaction.response.edit_message(content=f"{self.bot.emoji.get('cancel')} **alright we stopped...**", view=self)

    async def on_timeout(self) -> Optional[float]:
        for child in self.children:
            if isinstance(child, Button):
                child.disabled = True
        if self.message:
            await self.message.edit(content = f"{self.bot.emoji.get('cancel')} **{self.timeout_msg}**", view = self)


    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.response.send_message(random.choice(self._response), ephemeral=True)
            return False

        

