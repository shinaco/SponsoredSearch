sudo openvpn --config `ls us*443.ovpn | shuf | head -1` --auth-user-pass auth.txt
