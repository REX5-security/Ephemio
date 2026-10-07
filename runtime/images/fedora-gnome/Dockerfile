FROM ghcr.io/linuxserver/baseimage-selkies@sha256:e0026fcf7f1899013ba6310611d2a17125c094e401f78950968ca29bd04bbac3
ENV TITLE="Fedora Workstation" PIXELFLUX_WAYLAND=false
RUN dnf install -y --setopt=install_weak_deps=False \
    gnome-shell gnome-session gnome-control-center gnome-settings-daemon \
    nautilus gnome-terminal gnome-text-editor file-roller loupe \
    firefox adwaita-icon-theme dbus-daemon xorg-x11-server-Xwayland \
    && dnf clean all
RUN dnf install -y --allowerasing --setopt=install_weak_deps=False \
    mutter-devkit pipewire wireplumber fedora-release-workstation f44-backgrounds-gnome \
    && dnf clean all && rmdir /run/systemd/seats
COPY startwm.sh /defaults/startwm.sh
COPY openbox.xml /defaults/fedora-openbox.xml
COPY desktop-video.conf /etc/pipewire/client.conf.d/20-desktop-video.conf
COPY background.gschema.override /usr/share/glib-2.0/schemas/99_ephemio-background.gschema.override
RUN glib-compile-schemas /usr/share/glib-2.0/schemas
ENV LP_NUM_THREADS=2
COPY gnome-input.py patch-gnome-input.py /defaults/
RUN /usr/bin/python3 -c 'from gi.repository import Gio, GLib' \
    && /lsiopy/bin/python3 /defaults/patch-gnome-input.py \
    && /lsiopy/bin/python3 -m py_compile /lsiopy/lib/python3.14/site-packages/selkies/input_handler.py
COPY firefox-prefs.js /usr/lib64/firefox/defaults/pref/ephemio.js
COPY wait-gnome.sh /defaults/wait-gnome.sh
RUN rm /etc/s6-overlay/s6-rc.d/svc-de/dependencies.d/svc-selkies \
    && mkdir -p /etc/s6-overlay/s6-rc.d/init-gnome-ready/dependencies.d \
    && printf 'oneshot\n' > /etc/s6-overlay/s6-rc.d/init-gnome-ready/type \
    && printf '/bin/bash /defaults/wait-gnome.sh\n' > /etc/s6-overlay/s6-rc.d/init-gnome-ready/up \
    && touch /etc/s6-overlay/s6-rc.d/init-gnome-ready/dependencies.d/svc-de \
       /etc/s6-overlay/s6-rc.d/svc-selkies/dependencies.d/init-gnome-ready \
       /etc/s6-overlay/s6-rc.d/user/contents.d/init-gnome-ready
EXPOSE 3000
VOLUME /config
