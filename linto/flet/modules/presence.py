import flet as ft

import asyncio
import discord

class Presence(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.bio_input = ft.TextField(hint_text="Enter custom bio")
        self.bio_submit = ft.FloatingActionButton(
            "Change custom bio", 
            on_click=self.change_bio,
            width=300
        )
        self.bio = ft.Column(
            controls=[
                self.bio_input,
                self.bio_submit
            ]
        )
        
        self.presence_text = ft.Text("Choose presence status to change", size=24)
        self.presence_status = ft.Dropdown(
            width=300,
            hint_text="Presence status",
            autofocus=True,
            options=[
                ft.dropdown.Option("Online"),
                ft.dropdown.Option("Offline"),
                ft.dropdown.Option("Do not disturb"),
                ft.dropdown.Option("Idle")
            ], on_change=self.change_status
        )
        self.current_status = ft.Text(weight=ft.FontWeight.BOLD, size=24)

        self.presence = ft.Container(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        controls=[
                            self.presence_status,
                            self.current_status,
                        ]
                    ),
                    self.bio
                ]
            )
        )
        
        loop = asyncio.get_running_loop()
        loop.create_task(self.change_curstatus())

    async def change_curstatus(self):
        self.current_status.value = f"Current status: {self.bot.status.name}"

        try:
            await super().update_async()
        except AssertionError:
            pass

    async def change_status(self, event):
        statuses = {
            "Online": discord.Status.online,
            "Offline": discord.Status.offline,
            "Do not disturb": discord.Status.dnd,
            "Idle": discord.Status.idle
        }
        status = statuses[self.presence_status.value]
        await self.bot.change_presence(status=status)
        await self.change_curstatus()

    async def change_bio(self, event):
        bio = discord.CustomActivity(
            self.bio_input.value,
            expires_at=self.bio_delete.current_date
        )

        await self.bot.change_presence(activity=bio)