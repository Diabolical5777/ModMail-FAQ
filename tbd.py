# for simplicity, these commands are all global. You can add `guild=` or `guilds=` to `Bot.add_cog` in `setup` to add them to a guild.

from typing import Optional

import discord
import yaml
from discord import ButtonStyle, Embed, Interaction, Member, Message, app_commands
from discord.app_commands import Group
from discord.ext import commands
from discord.ui import Button, View
from discord.utils import format_dt

from dropdown import AlphaDropdownView


class FAQ_Group(Group, name="faq"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()  # this is now required in this context.

    @app_commands.command(name="sub-1")
    async def my_sub_command_1(self, interaction: discord.Interaction) -> None:
        """/parent sub-1"""
        await interaction.response.send_message(
            "Hello from sub command 1", ephemeral=True
        )

    @app_commands.command(name="sub-2")
    async def my_sub_command_2(self, interaction: discord.Interaction) -> None:
        """/parent sub-2"""
        await interaction.response.send_message(
            "Hello from sub command 2", ephemeral=True
        )

        @app_commands.command()
        async def hello(interaction: Interaction):
            """Says hello!"""
            await interaction.response.send_message(f"Hi, {interaction.user.mention}")

        @app_commands.command()
        @app_commands.describe(
            first_value="The first value you want to add something to",
            second_value="The value you want to add to the first value",
        )
        async def add(interaction: Interaction, first_value: int, second_value: int):
            """Adds two numbers together."""
            await interaction.response.send_message(
                f"{first_value} + {second_value} = {first_value + second_value}"
            )

        # The rename decorator allows us to change the display of the parameter on Discord.
        # In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
        # Note that other decorators will still refer to it as `text_to_send` in the code.
        @app_commands.command()
        @app_commands.rename(text_to_send="text")
        @app_commands.describe(text_to_send="Text to send in the current channel")
        async def send(interaction: Interaction, text_to_send: str):
            """Sends the text into the current channel."""
            await interaction.response.send_message(text_to_send)

        # To make an argument optional, you can either give it a supported default argument
        # or you can mark it as Optional from the typing standard library. This example does both.
        @app_commands.command()
        @app_commands.describe(
            member="The member you want to get the joined date from; defaults to the user who uses the command"
        )
        async def joined(interaction: Interaction, member: Optional[Member] = None):
            """Says when a member joined."""
            # If no member is explicitly provided then we use the command user here
            member = member or interaction.user

            # The format_dt function formats the date time into a human readable representation in the official client
            await interaction.response.send_message(
                f"{member} joined {format_dt(member.joined_at)}"
            )

        # A Context Menu command is an app command that can be run on a member or on a message by
        # accessing a menu within the client, usually via right clicking.
        # It always takes an interaction as its first parameter and a Member or Message as its second parameter.

        # This context menu command only works on members
        @app_commands.context_menu(name="Show Join Date")
        async def show_join_date(interaction: Interaction, member: Member):
            # The format_dt function formats the date time into a human readable representation in the official client
            await interaction.response.send_message(
                f"{member} joined at {format_dt(member.joined_at)}"
            )

        # This context menu command only works on messages
        @app_commands.context_menu(name="Report to Moderators")
        async def report_message(interaction: Interaction, message: Message):
            # We're sending this response message with ephemeral=True, so only the command executor can see it
            await interaction.response.send_message(
                f"Thanks for reporting this message by {message.author.mention} to our moderators.",
                ephemeral=True,
            )

            # Handle report by sending it into a log channel
            log_channel = interaction.guild.get_channel(
                0
            )  # replace with your channel id

            embed = Embed(title="Reported Message")
            if message.content:
                embed.description = message.content

            embed.set_author(
                name=message.author.display_name,
                icon_url=message.author.display_avatar.url,
            )
            embed.timestamp = message.created_at

            url_view = View()
            url_view.add_item(
                Button(
                    label="Go to Message", style=ButtonStyle.url, url=message.jump_url
                )
            )

            await log_channel.send(embed=embed, view=url_view)


async def setup(bot):
    await bot.add_cog(User_Cog(bot), guild=Object(id=default_guild))
    menus = [info_menu, joined_menu, avatar_menu, roles_menu, status_menu]
    for menu in menus:
        bot.tree.add_command(menu, guild=Object(id=default_guild))
    bot.tree.add_command(permissions_menu)
