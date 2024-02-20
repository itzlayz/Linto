import flet as ft
import asyncio

from ... import __version__
from discord.ext import commands


class Info(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.bot: commands.Bot

        self.avatar = ft.Image(
            "https://cdn.discordapp.com/embed/avatars/0.png",
            width=200,
            height=200,
            fit=ft.ImageFit.NONE,
            repeat=ft.ImageRepeat.NO_REPEAT,
            border_radius=ft.border_radius.all(50),
        )

        def loading():
            return ft.Text(
                "Loading..", weight=ft.FontWeight.BOLD, size=24, color=ft.colors.BLACK
            )

        self.username = loading()
        self.status = loading()

        self.guild_count = loading()
        self.friends_count = loading()

        self.linto_modules = loading()
        self.linto_version = loading()

        self.user_info = ft.Container(
            ft.Row(
                controls=[
                    self.avatar,
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    self.username,
                                    self.status,
                                    self.guild_count,
                                    self.friends_count,
                                ]
                            ),
                            ft.Column(
                                controls=[self.linto_modules, self.linto_version]
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            ),
            bgcolor=ft.colors.LIGHT_BLUE_ACCENT_700,
            border_radius=10,
            padding=10,
        )
        self.info = ft.Container(
            ft.Row(
                controls=[self.user_info],
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        )

        loop = asyncio.get_running_loop()
        loop.create_task(self.loading())

    async def loading(self):
        while True:
            await self.load_all()
            await asyncio.sleep(5)

    async def load_all(self):
        avatar = (
            self.bot.user.avatar.url
            if self.bot.user.avatar
            else self.bot.user.default_avatar.url
        )
        guild_count = len((await self.bot.fetch_guilds(with_counts=False)))

        self.avatar.src = avatar
        self.username.value = f"Username: {self.bot.user}"
        self.status.value = f"Status: {self.bot.status.name.title()}"

        self.guild_count.value = f"Guilds: {guild_count}"
        self.friends_count.value = f"Friends: {len(self.bot.friends)}"

        self.linto_modules.value = f"Linto modules: {len(self.bot.cogs)}"
        self.linto_version.value = f"Linto version: {'.'.join(map(str, __version__))}"

        try:
            await super().update_async()
        except AssertionError:
            pass
