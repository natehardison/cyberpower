import argparse
import getpass
import logging
import sys
from importlib.metadata import version

from cyberpower.cyberpower import CyberPower

DEFAULT_USER = getpass.getuser()
VERSION = version(__package__)

logger = logging.getLogger(__name__)


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
    c = CyberPower(args.host, args.user)
    if args.action == "shell":
        print(c.connect(), end="")
        try:
            c.shell()
        finally:
            c.close()
    else:
        with c:
            if args.action == "on":
                c.power_on(args.outlet)
            elif args.action == "off":
                c.power_off(args.outlet)
            elif args.action == "cycle":
                c.reboot(args.outlet)
            else:
                status = c.get_status()
                if args.outlet:
                    print(status[args.outlet])
                else:
                    print(status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
