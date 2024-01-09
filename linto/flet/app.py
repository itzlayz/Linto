# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#                           
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

async def init_flet(bot):
    import logging
    import discord
    import traceback
    
    from .. import utils
    from ..patch import Bot
    from discord.ext import commands

    logger = logging.getLogger(__name__)
    logger.info(f"{bot.user} - flet app initialization..")
    try:
        import flet as ft
    except ImportError:
        import subprocess
        import sys
        
        logger.warning("Flet is not found, installing flet")
        subprocess.run(
            [
                sys.executable,
                "-m", "pip",
                "install", "--upgrade",
                "--disable-pip-version-check",
                "flet"
            ], check=True
        )

        import flet as ft

    class FletApp(ft.UserControl):
        def __init__(self, bot: Bot, *args, **kwargs):
            self.bot = bot
            super().__init__(*args, **kwargs)

        def build(self):
            self.eval_input = ft.TextField(hint_text="Enter code to eval")
            self.eval_submit = ft.FloatingActionButton(
                "Evaluate", on_click=self.eval)
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

            self.terminal_input = ft.TextField(hint_text="Enter code to bash")
            self.terminal_submit = ft.FloatingActionButton(
                "Bash", on_click=self.bash)
            self.terminal_output = ft.Text()

            self.terminal = ft.Container(
                ft.Column(
                    controls=[
                        ft.Text("Terminal"),
                        self.terminal_input,
                        self.terminal_submit,
                        self.terminal_output
                    ]
                )
            )

            self.presence_status = ft.Dropdown(
                width=300,
                label="Presence status",
                autofocus=True,
                options=[
                    ft.dropdown.Option("Online"),
                    ft.dropdown.Option("Offline"),
                    ft.dropdown.Option("Do not disturb"),
                    ft.dropdown.Option("Idle")
                ], on_change=self.change_status
            )
            self.presence = ft.Container(
                ft.Row(
                    controls=[
                        self.presence_status
                    ]
                )
            )
            
            self.tabs = {
                "Evaluator": self.evaluator,
                "Terminal": self.terminal,
                "Presence": self.presence
            }
            self.linto_tabs = ft.Tabs(
                tabs=[
                    ft.Tab("Evaluator"),
                    ft.Tab("Terminal"),
                    ft.Tab("Presence"),
                ], on_change=self.change_tab
            )

            self.current_tab = ft.Container()
            return ft.Column(
                controls=[
                    self.linto_tabs,
                    self.current_tab
                ]
            )
        
        async def change_tab(self, event):
            next_tab = self.linto_tabs.tabs[self.linto_tabs.selected_index]
            tab_content = self.tabs[next_tab.text].content

            self.current_tab.content = tab_content
            await super().update_async()

        async def change_status(self, event):
            statuses = {
                "Online": discord.Status.online,
                "Offline": discord.Status.offline,
                "Do not disturb": discord.Status.dnd,
                "Idle": discord.Status.idle
            }
            status = statuses[self.presence_status.value]
            await self.bot.change_presence(status=status)

        async def bash(self, event):
            code = self.terminal_input.value

            try:
                output = await utils.check_output(code)
                
                out = await output.stdout.read()
                if not out:
                    try:
                        output = (await output.stderr.read()).decode()
                    except UnicodeDecodeError:
                        output = await output.stderr.read()
                else:
                    try:
                        out = out.decode()
                    except:
                        pass
            except OSError:
                output = "Bash is not available on windows"
            except Exception as error:
                traceback.print_exc()
                output = f"Got error during bash: {error}"

            self.terminal_output.value = str(output)
            await super().update_async()

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
    
    flet_app = FletApp(bot)
    async def app(page: ft.Page):
        page.title = bot.user
        
        await page.add_async(flet_app)

    await ft.app_async(app)
    return flet_app