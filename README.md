cyberpower
==========
A library and tool to control a CyberPower PDU41001 via SSH.

Why?
* Logging into the web GUI is a pain
* SSH oneliners don't appear to work (it's a janky SSH implementation)
* SNMP and NUT feel too complex for just on/off/cycle/status

Features:
* Will load your password out of your system keyring if you have it stored
    there (`keyring set <host> <user>`)
* `cyberpower <host> shell` command gives you shell access just like an
    SSH client

CLI usage
---------
```
usage: cyberpower [-h] [--user USER] [--verbose] [--version]
                  host {on,off,cycle,status,shell} [{1,2,3,4,5,6,7,8}]

Control a CyberPower PDU41001

positional arguments:
  host                  the hostname of the PDU
  {on,off,cycle,status,shell}
                        the action to run
  {1,2,3,4,5,6,7,8}     the outlet to control (required for on/off/cycle)
                        (default: None)

options:
  -h, --help            show this help message and exit
  --user USER           the user to log in as (default: nate)
  --verbose, -v         set logging to DEBUG (default: False)
  --version, -V         show program's version number and exit
```
