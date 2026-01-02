#!/bin/sh

cp ../hetzner-fw-update.service /etc/systemd/system/hetzner-fw-update.service
cp ../hetzner.timer /etc/systemd/system/hetzner.timer
systemctl daemon-reload


