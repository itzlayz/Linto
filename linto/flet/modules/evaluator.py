import flet as ft
from ... import utils

import discord
from discord.ext import commands

class Evaluator(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.eval_input = ft.TextField(hint_text="Enter code to eval", width=250)
        self.eval_submit = ft.FloatingActionButton(
            "Evaluate", on_click=self.eval, width=200)
        self.eval_output = ft.Text()

        self.evaluator = ft.Container(
            ft.Column(
                controls=[
                    ft.Text("Evaluator"),
                    self.eval_input,
                    self.eval_submit,
                    self.eval_output
                ]
            )
        )

    async def eval(self, event):
        code = self.eval_input.value
        env = {
            "bot": self.bot,
            "web": self.bot.webmanager,
            "db": self.bot.db,
            "discord": discord,
            "commands": commands
        }
        output = await utils.epc(code, env)

        self.eval_output.value = str(output)
        await super().update_async()