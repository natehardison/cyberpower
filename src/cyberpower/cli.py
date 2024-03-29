import argparse
import atexit
import getpass
import logging
import os
import readline
import sys
from importlib.metadata import version

from cyberpower.cyberpower import CyberPower

DEFAULT_USER = getpass.getuser()
VERSION = version(__package__)

HISTFILE = os.path.join(os.path.expanduser("~"), ".cyberpower")
HISTLEN = 1000

logger = logging.getLogger(__name__)


def do_shell(args: argparse.Namespace) -> int:  # noqa: C901
    try:
        readline.read_history_file(HISTFILE)
        # default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(HISTLEN)
    except FileNotFoundError:
        pass

    atexit.register(readline.write_history_file, HISTFILE)

    c = CyberPower(args.host, args.user)
    banner = c.connect()
    try:
        print(banner)
        while c.is_open():
            try:
                cmd = input(c.PROMPT)
                cmdargs = cmd.split() or [""]
                try:
                    fn = getattr(c, cmdargs[0])
                except AttributeError:
                    if cmd == "exit":
                        break
                    print(c.run(cmd))
                else:
                    print(fn(*cmdargs[1:]))
            except KeyboardInterrupt:
                if c.channel:
                    c.channel.send(b"\x03")
                else:
                    break
    finally:
        c.close()
    return 0


def do_status(args: argparse.Namespace) -> int:
    with CyberPower(args.host, args.user) as c:
        status = c.get_status(args.outlet)
        if args.outlet:
            print(status[0])
        else:
            print(status)
    return 0


def do_power_control(args: argparse.Namespace) -> int:
    with CyberPower(args.host, args.user) as c:
        if args.action == "on":
            fn = c.power_on
        elif args.action == "off":
            fn = c.power_off
        elif args.action == "cycle":
            fn = c.reboot
        else:
            raise ValueError(f"unknown action: '{args.action}'")
        fn(args.outlet)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Control a CyberPower PDU41001",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("host", help="the hostname of the PDU")
    parser.add_argument(
        "action",
        choices=("on", "off", "cycle", "status", "shell"),
        help="the action to run",
    )
    parser.add_argument(
        "outlet",
        nargs="?",
        help="the name or index of the outlet to control (if None will operate on all outlets)",
    )
    parser.add_argument("--user", default=DEFAULT_USER, help="the user to log in as")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="set logging to DEBUG"
    )
    parser.add_argument("--version", "-V", action="version", version=VERSION)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    if args.action == "shell":
        return do_shell(args)
    if args.action == "status":
        return do_status(args)
    return do_power_control(args)


if __name__ == "__main__":
    sys.exit(main())
