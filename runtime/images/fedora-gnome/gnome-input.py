#!/usr/bin/python3
"""Forward Selkies keysyms to GNOME's private remote-desktop session."""
import ctypes
import os
import socket
import time
from pathlib import Path

from gi.repository import Gio, GLib

runtime = Path(os.environ['XDG_RUNTIME_DIR'])
path = runtime / 'ephemio-input.sock'
libc = ctypes.CDLL(None)

while True:
    bus = server = session = None
    try:
        bus = Gio.DBusConnection.new_for_address_sync(
            os.environ['DBUS_SESSION_BUS_ADDRESS'],
            Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT | Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION,
            None, None)

        def call(where, interface, method, args=None):
            return bus.call_sync('org.gnome.Mutter.RemoteDesktop', where, interface,
                                 method, args, None, Gio.DBusCallFlags.NONE, 5000, None)

        # Devkit initializes the compositor's virtual monitor and keyboard.
        # Create our keyboard after that initialization, rather than racing it.
        while True:
            state = bus.call_sync('org.gnome.Mutter.DisplayConfig', '/org/gnome/Mutter/DisplayConfig',
                                  'org.gnome.Mutter.DisplayConfig', 'GetCurrentState', None, None,
                                  Gio.DBusCallFlags.NONE, 5000, None).unpack()
            if state[2]:
                break
            time.sleep(0.2)

        interface = 'org.gnome.Mutter.RemoteDesktop.Session'
        session = call('/org/gnome/Mutter/RemoteDesktop', 'org.gnome.Mutter.RemoteDesktop',
                       'CreateSession').unpack()[0]
        call(session, interface, 'Start')
        path.unlink(missing_ok=True)
        server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        server.bind(str(path))
        os.chmod(path, 0o600)
        # The worker's readiness check waits for the initialized input session.
        libc.prctl(15, b'ephemio-input', 0, 0, 0)
        pressed = set()

        def key(value, down):
            call(session, interface, 'NotifyKeyboardKeysym', GLib.Variant('(ub)', (value, down)))

        while True:
            try:
                parts = server.recv(256).decode('ascii').split(',')
                if parts == ['kr']:
                    for value in list(pressed):
                        key(value, False)
                    pressed.clear()
                elif len(parts) == 2 and parts[0] in ('kd', 'ku'):
                    value = int(parts[1])
                    if not 0 <= value <= 0xffffffff:
                        continue
                    down = parts[0] == 'kd'
                    key(value, down)
                    if down:
                        pressed.add(value)
                    else:
                        pressed.discard(value)
            except (ValueError, UnicodeError):
                continue
    except (OSError, GLib.Error):
        pass
    finally:
        libc.prctl(15, b'ephemio-init', 0, 0, 0)
        path.unlink(missing_ok=True)
        if server is not None:
            server.close()
        if bus is not None:
            # Closing this connection also releases GNOME's virtual keyboard.
            try:
                bus.close_sync(None)
            except GLib.Error:
                pass
    time.sleep(0.5)
