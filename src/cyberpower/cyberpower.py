import getpass
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

import keyring
from paramiko import Channel, Transport
from typing_extensions import Self

logger = logging.getLogger(__name__)


class CyberPower:
    KEX_ALGORITHM = "diffie-hellman-group-exchange-sha256"
    KEY_TYPE = "ssh-rsa"
    PROMPT = "CyberPower > "
    DEFAULT_RECV_BUFSIZE = 1024
    LINE_SEPARATOR = "\r\n"
    # CyberPower will disconnect if it receives a keepalive
    KEEPALIVE_INTERVAL = 0
    NUM_OUTLETS = 8

    def __init__(self, host: str, user: str, password: Optional[str] = None):
        self.host = host
        self.user = user
        self.password = (
            password or keyring.get_password(self.host, self.user) or getpass.getpass()
        )

        self.transport: Optional[Transport] = None
        self.channel: Optional[Channel] = None

    def _auth_handler(
        self, title: str, instructions: str, fields: List[Tuple[str, bool]]
    ) -> List[str]:
        return [self.password]

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def connect(self) -> str:
        if self.is_open():
            return ""
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
        return self._recv_until(self.PROMPT)

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

    def get_status(self) -> List[Dict[str, str]]:
        response = self.run("oltsta show")
        status = []
        for line in response.splitlines():
            if m := re.match(
                r"(?P<index>\d)\s+(?P<name>\S+)\s+(?P<status>(Off|On))$", line.strip()
            ):
                status.append(m.groupdict())
        return status

    def power_on(self, index: Optional[int] = None) -> str:
        return self._oltctrl_action("on", index)

    def power_off(self, index: Optional[int] = None) -> str:
        return self._oltctrl_action("off", index)

    def reboot(self, index: Optional[int] = None) -> str:
        return self._oltctrl_action("reboot", index)

    def _oltctrl_action(self, action: str, index: Optional[int] = None) -> str:
        cmd = "oltctrl index {} act {}"
        if index:
            return self.run(cmd.format(index, action))
        results = ""
        for i in range(1, self.NUM_OUTLETS + 1):
            results += self.run(cmd.format(i, action))
        return results
