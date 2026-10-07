FROM ghcr.io/linuxserver/baseimage-selkies@sha256:7cab02f9222937ad1e704cd904534d69a2300b2406af466241817be0ce1d0493
ENV TITLE="Linux Mint Cinnamon" DEBIAN_FRONTEND=noninteractive
COPY linuxmint-keyring.deb /tmp/linuxmint-keyring.deb
RUN dpkg -i /tmp/linuxmint-keyring.deb \
    && echo 'deb https://ftp-stud.hs-esslingen.de/pub/Mirrors/packages.linuxmint.com zena main upstream import backport' > /etc/apt/sources.list.d/mint.list \
    && printf 'Package: *\nPin: origin ftp-stud.hs-esslingen.de\nPin-Priority: 700\n' > /etc/apt/preferences.d/mint \
    && apt-get update && apt-get install -y --no-install-recommends \
    cinnamon cinnamon-session cinnamon-control-center cinnamon-settings-daemon \
    nemo xed xreader xviewer mint-themes mint-y-icons mint-backgrounds-wallpapers mint-artwork mintdesktop \
    mint-info-cinnamon base-files firefox gnome-terminal file-roller dbus-x11 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/linuxmint-keyring.deb
RUN printf 'Package: base-files\nPin: origin ftp-stud.hs-esslingen.de\nPin-Priority: 1001\n' > /etc/apt/preferences.d/mint-base-files \
    && apt-get update && apt-get install -y --no-install-recommends --allow-downgrades base-files librsvg2-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY startwm.sh /defaults/startwm.sh
EXPOSE 3000
VOLUME /config
