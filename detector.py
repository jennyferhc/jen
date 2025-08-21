import cv2
import numpy as np
import pygame
import threading

# Variables globales
fire_reported = 0
alarm_status = False

# Inicializar mixer de pygame una sola vez
pygame.mixer.init()

# Función para reproducir el audio de la alarma
def play_audio():
    pygame.mixer.music.load("Alarm.mp3")  # asegúrate de que el archivo esté en la misma carpeta
    pygame.mixer.music.play(-1)  # -1 = loop infinito

# Función para detener el audio de la alarma
def stop_audio():
    pygame.mixer.music.stop()

# Inicializar captura de video
video = cv2.VideoCapture(0)

if not video.isOpened():
    print("❌ No se pudo abrir la cámara.")
    exit()

while True:
    ret, frame = video.read()
    if not ret:
        print("❌ Error al leer frame de la cámara.")
        break

    # Redimensionar el frame
    frame = cv2.resize(frame, dsize=(1000, 600))

    # Ajustar brillo y contraste
    brightness = 10
    contrast = 1.5
    frame = cv2.convertScaleAbs(frame, alpha=contrast, beta=brightness)

    # Aplicar desenfoque
    blur = cv2.GaussianBlur(frame, ksize=(15, 15), sigmaX=0)

    # Convertir a HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # Definir rangos para detección de color de fuego (amarillo/naranja)
    lower = np.array([18, 50, 50], dtype=np.uint8)
    upper = np.array([35, 255, 255], dtype=np.uint8)

    # Crear máscara
    mask = cv2.inRange(hsv, lower, upper)

    # Encontrar contornos
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fire_detected = False

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 2000:  # filtrar ruido pequeño
            fire_detected = True
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, "🔥 Fuego detectado", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("Detector de fuego", frame)

    # Lógica para alarma
    if fire_detected:
        fire_reported += 1
    else:
        fire_reported = 0

    if fire_reported >= 1:
        if not alarm_status:
            threading.Thread(target=play_audio, daemon=True).start()
            alarm_status = True

    if fire_reported == 0 and alarm_status:
        stop_audio()
        alarm_status = False

    # Salida con tecla ESC
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break

# Liberar recursos
video.release()
cv2.destroyAllWindows()
stop_audio()
