import cv2
import threading
import simpleaudio as sa
import time
from PIL import Image

def play_audio(wav_path):
    """
    Lit le fichier WAV en bloc (bloquant) puis retourne.
    On l’exécute dans un thread séparé.
    """
    try:
        wave_obj = sa.WaveObject.from_wave_file(wav_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except Exception as e:
        print("Erreur audio :", e)

def play_video_fullscreen(mp4_path):
    """
    Ouvre le MP4 avec OpenCV et affiche chaque frame en plein écran.
    """
    cap = cv2.VideoCapture(mp4_path)
    if not cap.isOpened():
        print("Erreur : impossible d’ouvrir", mp4_path)
        return

    # Récupère la résolution de la vidéo
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps    = cap.get(cv2.CAP_PROP_FPS) or 30

    # Crée une fenêtre nommée et la passe en fullscreen
    window_name = "Lecture Fullscreen"
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # Boucle de lecture
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # (Optionnel) Si vous voulez absolument passer par Pillow :
        # Convertit frame (BGR) en RGB et crée un objet PIL.Image
        # img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # Ensuite on peut faire un traitement PIL ici si besoin.
        # Mais pour afficher, on retourne la frame OpenCV en BGR…

        # Affiche directement la frame
        cv2.imshow(window_name, frame)

        # Attend le temps nécessaire pour atteindre le FPS d’origine
        if cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    wav_path = "long.wav"
    mp4_path = "long.mp4"

    # Démarre l’audio dans un thread
    audio_thread = threading.Thread(target=play_audio, args=(wav_path,))
    audio_thread.daemon = True
    audio_thread.start()

    # Petit délai pour synchroniser (optionnel)
    time.sleep(0.1)

    # Lance la vidéo en plein écran (bloquant jusqu’à la fin)
    play_video_fullscreen(mp4_path)

    # Attend que l’audio se termine (normalement, les deux dureront sensiblement pareil)
    audio_thread.join()

if __name__ == "__main__":
    main()
