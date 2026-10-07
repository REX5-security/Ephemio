from pathlib import Path
p=Path('/lsiopy/lib/python3.14/site-packages/selkies/input_handler.py');s=p.read_text()
helper='''def _ephemio_gnome_send(message):
    path = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/config/.XDG"), "ephemio-input.sock")
    if not os.path.exists(path):
        return False
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as channel:
        channel.sendto(message.encode("ascii"), path)
    return True


'''
a='class _XTestKeyboard:';assert s.count(a)==1;s=s.replace(a,helper+a)
a='        msg_type = toks[0]\n';assert s.count(a)==1;s=s.replace(a,a+'        if msg_type in ("kd", "ku", "kr") and _ephemio_gnome_send(msg):\n            return\n')
a='        held_level_mods = frozenset(self.active_modifiers & self.LEVEL_MODIFIER_KEYSYMS)';assert s.count(a)==1;s=s.replace(a,'        if _ephemio_gnome_send(("kd," if down else "ku,") + str(keysym)):\n            return\n'+a)
a='        if self.is_wayland:\n            worker = self.keyboard_worker_task';assert s.count(a)==1;s=s.replace(a,'        if _ephemio_gnome_send("kr"):\n            return\n'+a)
p.write_text(s)
print('Enabled direct GNOME keyboard forwarding.')
