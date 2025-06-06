#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket  # https://wiki.python.org/moin/UdpCommunication

# Paramètres
localPort = 8888
bufferSize = 1024

# Création du socket UDP (famille IPv4, type UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def init():
    # Autorise le réemploi du port (pour redémarrages rapides)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Active le mode broadcast si nécessaire
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    # Bind sur toutes les interfaces locales ('') et sur le port 8888
    sock.bind(('', localPort))
    # Affiche l’IP locale et le port
    print("UDP server démarré sur {}:{}".format(get_ip_address(), localPort))

def main():
    while True:
        data, addr = sock.recvfrom(bufferSize)  # Lecture du buffer
        message = data.decode()
        print("Message reçu : {!r} de {}".format(message, addr))
        
        # Si le message reçu est ROTARY_OK, afficher OK
        if message == "ROTARY_OK":
            print("OK")
        
        # Réponse au client (optionnel)
        sock.sendto(b"RPi received OK", addr)

def get_ip_address():
    """
    Récupère l'adresse IP locale du Raspberry Pi en ouvrant
    un socket temporaire vers 8.8.8.8.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "127.0.0.1"
    finally:
        s.close()
    return ip_address

if __name__ == '__main__':
    init()
    main()

