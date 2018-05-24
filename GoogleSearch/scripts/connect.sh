#!/bin/sh
openvpn --redirect-gateway autolocal --config `ls ~/ResearchProject/GoogleSearch/vpn/us*443.ovpn | shuf | head -1` --auth-user-pass ../scripts/auth.txt
