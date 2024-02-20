# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html


async def init_flet(bot):
    import logging

    from .modules import evaluator, presence, terminal, info
    from ..patch import Bot

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
                "-m",
                "pip",
                "install",
                "--upgrade",
                "--disable-pip-version-check",
                "flet",
            ],
            check=True,
        )

        import flet as ft

    class FletApp(evaluator.Evaluator, presence.Presence, terminal.Terminal, info.Info):
        def __init__(self, bot: Bot):
            super().__init__()
            self.bot = bot

        def build(self):
            self.tabs = {
                "Info": self.info,
                "Evaluator": self.evaluator,
                "Terminal": self.terminal,
                "Presence": self.presence,
            }
            self.linto_tabs = ft.Tabs(
                tabs=[
                    ft.Tab("Info"),
                    ft.Tab("Evaluator"),
                    ft.Tab("Terminal"),
                    ft.Tab("Presence"),
                ],
                on_change=self.change_tab,
            )

            self.current_tab = ft.Container()
            return ft.Column(controls=[self.linto_tabs, self.current_tab])

        async def change_tab(self, event):
            next_tab = self.linto_tabs.tabs[self.linto_tabs.selected_index]
            tab_content = self.tabs[next_tab.text].content

            self.current_tab.content = tab_content
            await super().update_async()

    flet_app = FletApp(bot)

    async def app(page: ft.Page):
        text_style = ft.TextStyle(
            color=ft.colors.ORANGE, weight=ft.FontWeight.BOLD, size=18
        )
        page.title = bot.user
        page.theme = ft.Theme(
            text_theme=ft.TextTheme(
                label_large=text_style,
                label_medium=text_style,
                label_small=text_style,
                title_large=text_style,
                title_medium=text_style,
                title_small=text_style,
            )
        )

        await page.add_async(flet_app)

    await ft.app_async(app, host="localhost", port=8080)
    logger.info("Flet app started (also on http://localhost:8080)")

    return flet_app
