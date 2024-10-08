# █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
# █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
# https://t.me/itzlayz
#
# 🔒 Licensed under the GNU AGPLv3
# https://www.gnu.org/licenses/agpl-3.0.html

from . import main
from contextlib import suppress

from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--flet", dest="flet_app", action="store_true")
parser.add_argument("--no-web", dest="no_web", action="store_true")
parser.add_argument("--no-qr", dest="no_qr", action="store_true")

args = parser.parse_args()

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        main.main(args)

    if getattr(args, "flet_app", False):
        exit(0)
