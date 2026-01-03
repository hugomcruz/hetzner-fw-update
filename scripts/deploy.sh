#!/bin/sh

cp ../systemd/hetzner-fw-update.service /etc/systemd/system/hetzner-fw-update.service
cp ../systemd/hetzner-fw-update.timer /etc/systemd/system/hetzner-fw-update.timer
systemctl daemon-reload


