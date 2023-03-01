import getpass
import logging
import re
import sys
import time
from typing import Optional

from paramiko import Channel, Transport


logger = logging.getLogger(__name__)


class CyberPower:
    KEX_ALGORITHM = "diffie-hellman-group-exchange-sha256"
    KEY_TYPE = "ssh-rsa"
    PROMPT = "CyberPower > "
    DEFAULT_RECV_BUFSIZE = 1024
    LINE_SEPARATOR = "\r\n"
    KEEPALIVE_INTERVAL = 60

    def __init__(self, host: str, user: str, password: Optional[str] = None):
        self.host = host
        self.user = user
        self.password = password

        self.transport: Optional[Transport] = None
        self.channel: Optional[Channel] = None

    def _auth_handler(self, *_) -> list[str]:
        return [self.password or getpass.getpass()]

    def connect(self) -> None:
        if self.is_open():
            return
        t = Transport(self.host)
        o = t.get_security_options()
        o.kex = (self.KEX_ALGORITHM,)
        o.key_types = (self.KEY_TYPE,)
        t.set_keepalive(self.KEEPALIVE_INTERVAL)

        t.start_client()
        t.auth_interactive(self.user, self._auth_handler)
        self.transport = t
        self.channel = t.open_session()
        self.channel.get_pty()
        self.channel.invoke_shell()
        self._recv_until(self.PROMPT)

    def is_open(self) -> bool:
        return bool(self.transport and self.transport.active)

    def close(self) -> None:
        if self.is_open():
            assert self.transport
            self.transport.close()
        self.transport = None
        self.channel = None

    def _recv_until(self, delim: str, bufsize: int = DEFAULT_RECV_BUFSIZE) -> str:
        assert self.channel
        while True:
            data = self.channel.recv(bufsize).decode()
            if data.endswith(delim):
                return data

    def run(self, cmd: str) -> str:
        assert self.channel
        if cmd != "?" and not cmd.endswith(self.LINE_SEPARATOR):
            cmd += self.LINE_SEPARATOR
        self.channel.sendall(cmd.encode())
        return self._recv_until(self.PROMPT)

    def get_status(self) -> list:
        response = self.run("oltsta show")
        status = []
        for line in response.splitlines():
            if m := re.match(
                r"(?P<index>\d)\s+(?P<name>\S+)\s+(?P<status>(Off|On))$", line.strip()
            ):
                status.append({k: m.group(k)} for k in ("index", "name", "status"))
        return status

    def power_on(self, index: int) -> None:
        self.run(f"oltctrl index {index} act on")

    def power_off(self, index: int) -> None:
        self.run(f"oltctrl index {index} act off")

    def reboot(self, index: int) -> None:
        self.run(f"oltctrl index {index} act reboot")

    def shell(self) -> None:
        while self.is_open():
            cmd = input()
            args = cmd.split() or [""]
            try:
                fn = getattr(self, args[0])
            except AttributeError:
                print(self.run(cmd), end="")
                if cmd == "exit":
                    time.sleep(0.5)
            else:
                fn(*args[1:])


def main() -> int:
    host = "192.168.1.62"
    user = "nate"
    logging.basicConfig(level=logging.DEBUG)
    c = CyberPower(host, user)
    c.connect()
    try:
        c.shell()
    finally:
        c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
