import discord
from discord.ext import commands
from discord import app_commands

from .config import db
from .utils import (
    apply_replacements,
    split_message,
    validate_word,
)

from .webhook import (
    get_or_create_webhook,
    clear_webhook_cache,
    send_as_user,
    MissingWebhookPermissions
)


MAX_WORD = 100


class Replace(app_commands.Group):
    pass


class Replacer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.replace = Replace(
            name="replace",
            description="Manage word replacements"
        )


    async def cog_load(self):

        if "replace" not in self.bot.tree.get_commands():

            self.bot.tree.add_command(self.replace)


    async def permission_fail(self, target):

        text = (
            "❌ Missing permissions:\n"
            "- Manage Webhooks\n"
            "- Manage Messages\n"
            "- Send Messages\n"
            "- Read Message History"
        )

        try:

            if isinstance(target, discord.Interaction):

                if target.response.is_done():
                    await target.followup.send(text, ephemeral=True)
                else:
                    await target.response.send_message(text, ephemeral=True)

            else:

                await target.channel.send(
                    f"{target.author.mention}\n{text}"
                )

        except Exception:
            pass


    @app_commands.command(name="add", description="Add a replacement")
    async def add(
        self,
        interaction: discord.Interaction,
        word: str,
        replacement: str
    ):

        try:
            validate_word(word, MAX_WORD)
            validate_word(replacement, MAX_WORD)

        except Exception as e:
            return await interaction.response.send_message(
                str(e),
                ephemeral=True
            )

        db.add_replacement(
            interaction.guild.id,
            word,
            replacement
        )

        await interaction.response.send_message(
            f"✅ {word} → {replacement}",
            ephemeral=True
        )


    @app_commands.command(name="remove", description="Remove a replacement")
    async def remove(
        self,
        interaction: discord.Interaction,
        word: str
    ):

        removed = db.remove_replacement(
            interaction.guild.id,
            word
        )

        await interaction.response.send_message(
            "✅ Removed" if removed else "❌ Not found",
            ephemeral=True
        )


    @app_commands.command(name="list", description="List replacements")
    async def list(
        self,
        interaction: discord.Interaction
    ):

        data = db.get_replacements(interaction.guild.id)
        enabled = db.enabled(interaction.guild.id)
        channels = db.get_channels(interaction.guild.id)
        role = db.get_bypass_role(interaction.guild.id)

        header = [
            "🟢 Enabled" if enabled else "🔴 Disabled",
            "📍 " + (", ".join(f"<#{c}>" for c in channels) if channels else "all channels"),
            f"🛡️ <@&{role}>" if role else "🛡️ none"
        ]

        body = [
            f"• {k} → {v}"
            for k, v in data.items()
        ]

        text = "\n".join(header) + "\n\n" + (
            "\n".join(body) if body else "No replacements."
        )

        chunks = split_message(text)

        await interaction.response.send_message(
            chunks[0],
            ephemeral=True
        )

        for chunk in chunks[1:]:
            await interaction.followup.send(chunk, ephemeral=True)


    @app_commands.command(name="clearlist", description="Clear replacements")
    async def clearlist(self, interaction: discord.Interaction):

        count = db.clear_replacements(interaction.guild.id)

        await interaction.response.send_message(
            f"Removed {count}",
            ephemeral=True
        )


    @app_commands.command(name="toggle", description="Enable/disable system")
    async def toggle(self, interaction: discord.Interaction):

        state = db.toggle(interaction.guild.id)

        await interaction.response.send_message(
            "Enabled" if state else "Disabled",
            ephemeral=True
        )


    @commands.Cog.listener()
    async def on_message(self, message):

        if (
            message.author.bot
            or message.webhook_id
            or not message.guild
        ):
            return

        guild = message.guild

        if not db.enabled(guild.id):
            return

        channels = db.get_channels(guild.id)

        if channels and str(message.channel.id) not in channels:
            return

        replacements = db.get_replacements(guild.id)

        if not replacements:
            return

        role_id = db.get_bypass_role(guild.id)

        if role_id:

            role = guild.get_role(int(role_id))

            if role and message.author.top_role >= role:
                return

        modified = apply_replacements(message.content, replacements)

        if modified == message.content:
            return

        try:
            webhook, _ = await get_or_create_webhook(message.channel)

        except MissingWebhookPermissions:
            return await self.permission_fail(message)

        name = getattr(message.author, "display_name", message.author.name)
        avatar = message.author.display_avatar.url

        try:
            await message.delete()

        except Exception:
            return

        try:
            await send_as_user(
                webhook,
                message,
                modified,
                name,
                avatar
            )

        except Exception:
            clear_webhook_cache(message.channel.id)


async def setup(bot):
    await bot.add_cog(Replacer(bot))
