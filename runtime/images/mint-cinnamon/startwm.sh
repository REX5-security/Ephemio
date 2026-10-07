#!/bin/bash
export XDG_CURRENT_DESKTOP=X-Cinnamon XDG_SESSION_TYPE=x11 LIBGL_ALWAYS_SOFTWARE=1
unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS
exec dbus-run-session -- bash -c '
  gsettings set org.cinnamon.desktop.session idle-delay 0
  gsettings set org.cinnamon.desktop.screensaver lock-enabled false
  gsettings set org.cinnamon.desktop.interface gtk-theme Mint-Y
  gsettings set org.cinnamon.desktop.interface icon-theme Mint-Y
  gsettings set org.cinnamon.theme name Mint-Y
  exec cinnamon-session
'
