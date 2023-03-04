import argparse
import getpass
import logging
import sys
import time
from importlib.metadata import version

from cyberpower.cyberpower import CyberPower

DEFAULT_USER = getpass.getuser()
VERSION = version(__package__)

logger = logging.getLogger(__name__)


def do_shell(args: argparse.Namespace) -> int:
    c = CyberPower(args.host, args.user)
    print(c.connect(), end="")
    try:
        while c.is_open():
            cmd = input()
            cmdargs = cmd.split() or [""]
            try:
                fn = getattr(c, cmdargs[0])
            except AttributeError:
                print(c.run(cmd), end="")
                if cmd == "exit":
                    time.sleep(0.5)
            else:
                fn(*cmdargs[1:])
    finally:
        c.close()
    return 0


def do_status(args: argparse.Namespace) -> int:
    with CyberPower(args.host, args.user) as c:
        status = c.get_status()
        if args.outlet:
            print(status[args.outlet])
        else:
            print(status)
    return 0


def do_power_control(args: argparse.Namespace) -> int:
    with CyberPower(args.host, args.user) as c:
        if args.action == "on":
            c.power_on(args.outlet)
        elif args.action == "off":
            c.power_off(args.outlet)
        elif args.action == "cycle":
            c.reboot(args.outlet)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("host", help="the hostname of the PDU")
    parser.add_argument(
        "action",
        choices=("on", "off", "cycle", "status", "shell"),
        help="the action to run",
    )
    parser.add_argument(
        "outlet",
        nargs="?",
        choices=list(map(str, range(1, 9))),
        help="the outlet to control",
    )
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--version", "-V", action="version", version=VERSION)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    if args.action == "shell":
        return do_shell(args)
    if args.action == "status":
        return do_status(args)
    if not args.outlet:
        parser.error(f"outlet is required for action '{args.action}'")
    return do_power_control(args)


if __name__ == "__main__":
    sys.exit(main())
