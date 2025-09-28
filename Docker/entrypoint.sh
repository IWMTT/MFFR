#!/bin/bash

# Create User
USER=${USER:-root}
HOME=/root

if [ "$USER" != "root" ]; then
    if id "$USER" &>/dev/null; then
        echo "* user \"$USER\" already exists, skipping creation"
    else
        echo "* creating user: $USER"
        useradd --create-home --shell /bin/bash --user-group --groups adm,sudo "$USER"
        echo "$USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
        if [ -z "$PASSWORD" ]; then
            echo "  set default password to \"ubuntu\""
            PASSWORD=ubuntu
        fi
        echo "$USER:$PASSWORD" | /usr/sbin/chpasswd 2>/dev/null || echo ""
    fi

    HOME="/home/$USER"
    cp -r /root/{.config,.gtkrc-2.0,.asoundrc} "$HOME" 2>/dev/null || true
    chown -R "$USER:$USER" "$HOME"
    [ -d "/dev/snd" ] && chgrp -R adm /dev/snd
    echo "user creation finished"
fi

if [ "$USER" != "root" ]; then
    echo "switching to $USER"
    exec su - "$USER" -c "bash"
else
    exec bash
fi

exec "$@"