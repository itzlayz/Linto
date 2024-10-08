# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

import logging
import subprocess
import sys

from .modules import evaluator, presence, terminal, info
from ..patch import Bot

try:
    import flet as ft
except ImportError:
    logging.warning("Flet is not found, installing flet")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "--disable-pip-version-check", "flet"],
        check=True,
    )
    import flet as ft

async def init_flet(bot):
    logger = logging.getLogger(__name__)
    logger.info(f"{bot.user} - flet app initialization..")

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
                tabs=[ft.Tab(name) for name in self.tabs],
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
        text_style = ft.TextStyle(color=ft.colors.ORANGE, weight=ft.FontWeight.BOLD, size=18)
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

    try:
        import flet_fastapi
        from uvicorn import Server, Config

        fastapi = flet_fastapi.FastAPI()
        fastapi.mount("/", flet_fastapi.app(app))

        config = Config(fastapi, "localhost", 6606, log_level=60)
        server = Server(config)
        
        await server.serve()

        logger.info("Flet-app started on http://localhost:6606")
    except ImportError:
        logger.error("Install `web_requirements.txt` to use flet-app in web browser")

    await ft.app_async(app)
