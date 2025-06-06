import cv2
import threading
import simpleaudio as sa
import time
import socket
from PIL import Image


# ------------------------------------------
# CONFIGURATION
# ------------------------------------------

VIDEO_PATH = "long.mp4"   # Vidéo à lire
AUDIO_PATH = "long.wav"   # WAV extrait via ffmpeg
UDP_LISTEN_PORT = 8888    # Port sur lequel le Pi écoute les commandes UDP

# ------------------------------------------
# ÉTATS GLOBAUX PARTAGÉS
# ------------------------------------------
paused_event = threading.Event()
# Si paused_event.is_set(): on est en pause ; sinon on lit
exit_event = threading.Event()
# Lorsque exit_event.is_set(), on arrête tout (vidéo + audio + UDP)


# ------------------------------------------
# FONCTION: lecture audio dans un thread
# ------------------------------------------
def play_audio(wav_path):
    """
    Lit le fichier WAV en bloc (bloquant) mais on peut le stopper
    en testant exit_event avant chaque portion.
    """
    try:
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        # Tant que le son n'est pas fini, on boucle en vérifiant exit_event
        while play_obj.is_playing():
            if exit_event.is_set():
                play_obj.stop()
                return
            time.sleep(0.1)
    except Exception as e:
        print("Erreur audio :", e)


# ------------------------------------------
# FONCTION: lecture vidéo en plein écran
# ------------------------------------------
def play_video_fullscreen(mp4_path):
    cap = cv2.VideoCapture(mp4_path)
    if not cap.isOpened():
        print("Erreur : impossible d’ouvrir", mp4_path)
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    delay_ms = int(1000 / fps)

    window_name = "Lecture Vidéo (q pour quitter)"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while not exit_event.is_set():
        # Si on est en pause → on saute l'affichage des frames
        if paused_event.is_set():
            # on vérifie toutes les 100 ms si on doit quitter ou sortir de pause
            if cv2.waitKey(100) & 0xFF == ord('q'):
                exit_event.set()
                break
            continue

        ret, frame = cap.read()
        if not ret:
            # fin de la vidéo : on sort
            exit_event.set()
            break

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(delay_ms) & 0xFF
        if key == ord('q'):
            # L'utilisateur a appuyé sur q dans la fenêtre OpenCV : on arrête
            exit_event.set()
            break

    cap.release()
    cv2.destroyAllWindows()


# ------------------------------------------
# FONCTION: serveur UDP pour contrôler lecture
# ------------------------------------------
def udp_server():
    """
    Écoute en boucle sur UDP_LISTEN_PORT.
    Quand on reçoit "PAUSE", on bascule paused_event.
    Quand on reçoit "FORWARD", on avance de 10 frames.
    Quand on reçoit "BACKWARD", on recule de 10 frames.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", UDP_LISTEN_PORT))
    print(f"UDP server démarré, écoute sur le port {UDP_LISTEN_PORT}")

    # Pour l'avance/recul, on stocke la capture VideoCapture partagée
    vc = cv2.VideoCapture(VIDEO_PATH)

    while not exit_event.is_set():
        try:
            sock.settimeout(0.5)
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            continue

        message = data.decode().strip().upper()
        print(f"Commande UDP reçue : '{message}' de {addr}")

        if message == "PAUSE":
            # Toggle pause / reprise
            if paused_event.is_set():
                print("→ Reprise lecture")
                paused_event.clear()
            else:
                print("→ Pause lecture")
                paused_event.set()

        elif message == "FORWARD":
            # Avance de 10 frames
            current = int(vc.get(cv2.CAP_PROP_POS_FRAMES))
            new_pos = current + 10
            vc.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
            print(f"→ Avance à la frame {new_pos}")

        elif message == "BACKWARD":
            # Recule de 10 frames (au minimum à 0)
            current = int(vc.get(cv2.CAP_PROP_POS_FRAMES))
            new_pos = max(0, current - 10)
            vc.set(cv2.CAP_PROP_POS_FRAMES, new_pos)
            print(f"→ Recule à la frame {new_pos}")

        else:
            print("→ Commande inconnue :", message)

        # (optionnel) on renvoie un accusé de réception
        sock.sendto(b"RPi OK", addr)

    vc.release()
    sock.close()


# ------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------
def main():
    # 1. Lance le thread audio
    audio_thread = threading.Thread(target=play_audio, args=(AUDIO_PATH,))
    audio_thread.daemon = True
    audio_thread.start()

    # 2. Lance le thread UDP pour recevoir les commandes
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    udp_thread.start()

    # 3. Lit la vidéo en plein écran (bloquant jusqu’à exit_event)
    play_video_fullscreen(VIDEO_PATH)

    # 4. À la sortie (fin vidéo ou touche 'q'), on demande aux autres threads d’arrêter
    exit_event.set()

    # 5. Attend que le thread audio se termine
    audio_thread.join()
    udp_thread.join()
    print("Lecture terminée, script arrête.")


if __name__ == "__main__":
    main()
