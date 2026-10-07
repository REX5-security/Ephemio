FROM ghcr.io/linuxserver/baseimage-selkies@sha256:7cab02f9222937ad1e704cd904534d69a2300b2406af466241817be0ce1d0493
ENV TITLE="Ubuntu Desktop" DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnome-shell gnome-session ubuntu-session ubuntu-settings \
    gnome-shell-extension-ubuntu-dock gnome-shell-extension-appindicator \
    gnome-control-center gnome-settings-daemon nautilus gnome-terminal \
    gnome-text-editor file-roller eog yaru-theme-gtk yaru-theme-icon \
    ubuntu-wallpapers firefox fonts-ubuntu dbus-x11 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY mozilla.asc /etc/apt/keyrings/mozilla.asc
RUN echo 'deb [signed-by=/etc/apt/keyrings/mozilla.asc] https://packages.mozilla.org/apt mozilla main' > /etc/apt/sources.list.d/mozilla.list \
    && printf 'Package: firefox*\nPin: origin packages.mozilla.org\nPin-Priority: 1001\n' > /etc/apt/preferences.d/mozilla \
    && apt-get update && apt-get install -y --no-install-recommends --allow-downgrades firefox \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY startwm.sh /defaults/startwm.sh
RUN apt-get update && apt-get install -y --no-install-recommends librsvg2-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN rmdir /run/systemd/seats \
    && mkdir -p /defaults/gnome-autostart \
    && printf '[GNOME Session]\nName=Ubuntu Desktop\nRequiredComponents=org.gnome.Shell;\n' > /usr/share/gnome-session/sessions/ephemio.session
EXPOSE 3000
VOLUME /config
