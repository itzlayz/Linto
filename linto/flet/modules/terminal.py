import flet as ft
from ... import utils

import traceback


class Terminal(ft.UserControl):
    def __init__(self):
        super().__init__()

        self.terminal_input = ft.TextField(hint_text="Enter code to bash", width=250)
        self.terminal_submit = ft.FloatingActionButton(
            "Bash", on_click=self.bash, width=200
        )
        self.terminal_output = ft.Text()

        self.terminal = ft.Container(
            ft.Column(
                controls=[
                    ft.Text("Terminal"),
                    self.terminal_input,
                    self.terminal_submit,
                    self.terminal_output,
                ]
            )
        )

    async def bash(self, event):
        code = self.terminal_input.value

        try:
            output = await utils.create_process_async(code)

            out = await output.stdout.read()
            if not out:
                try:
                    output = (await output.stderr.read()).decode()
                except UnicodeDecodeError:
                    output = await output.stderr.read()
            else:
                try:
                    out = out.decode()
                except UnicodeDecodeError:
                    pass
        except OSError:
            output = "Bash is not available on windows"
        except Exception as error:
            traceback.print_exc()
            output = f"Got error during bash: {error}"

        self.terminal_output.value = str(output)
        await super().update_async()
