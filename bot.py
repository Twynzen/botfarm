import pytesseract
from PIL import Image
import pyautogui as pg
import time
import os
from PIL import ImageChops 

# Configura la ubicación de Tesseract en tu sistema
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configuración de parámetros
mapLocationDir = "mapLocation"
imageOffset = 25
waitTime = 8
screenshotSize = 100
trigoPaths = ["ojoIA/trigo1.PNG", "ojoIA/trigo2.PNG", "ojoIA/trigo3.PNG","ojoIA/trigo4.PNG","ojoIA/trigo5.PNG"]
fresnoPaths = ["ojoIA/fresno1.PNG", "ojoIA/fresno2.PNG", "ojoIA/fresno3.PNG"]
castanoPaths = ["ojoIA/casta1.PNG", "ojoIA/casta2.PNG", "ojoIA/casta3.PNG", "ojoIA/casta4.PNG" ]
ortigaPaths = ["ojoIA/ortiga1.PNG", "ojoIA/ortiga2.PNG", "ojoIA/ortiga3.PNG", "ojoIA/ortiga4.PNG", "ojoIA/ortiga5.PNG"]
hierroPaths = ["ojoIA/hierro1.PNG", "ojoIA/hierro2.PNG", "ojoIA/hierro3.PNG","ojoIA/hierro4.PNG", "ojoIA/hierro5.PNG"]


confidenceLevel = 0.7
screenshotsDir = "ojoIA"
DIRECTIONS = [ 'right','right', 'up','up','right','up','up','right','down','right','right','up','right','up','up','left','up','right','up','left']
#1,23 TR
#4,21
CURRENT_DIRECTION_INDEX = 0
REGION_TO_CAPTURE = (0, 25, 280, 220)
TOOLTIP_REGIONS = {
    'up': (960 - 50, 0, 100, 50),   
    'left': (0 + 300, 540 - 25, 100, 50),  
    'right': (1920 - 400, 540 - 25, 100, 50), 
    'down': (960 - 50, 1080 - 200, 100, 50),
}

TOOLTIP_IMAGES = {
    'up': 'ojoIA/tooltip_image1.PNG',
    'left': 'ojoIA/tooltip_image2.PNG',
    'right': 'ojoIA/tooltip_image3.PNG',
}

if not os.path.exists(mapLocationDir):
    os.makedirs(mapLocationDir)

if not os.path.exists(screenshotsDir):
    os.makedirs(screenshotsDir)

def click_image(paths, object_name):
    image_not_found_count = 0  # Contador para el número de imágenes no encontradas

    for path in paths:
        try:
            pos = pg.locateOnScreen(path, confidence=confidenceLevel)
            if pos:
                pg.moveTo(pos[0] + imageOffset, pos[1] + imageOffset)
                pg.click()
                print(f"[INFO] Se encontró {object_name} y se hizo clic en {pos}.")
                time.sleep(waitTime)
                capture_screenshot(pos, object_name)
                return True
        except pg.ImageNotFoundException:
            image_not_found_count += 1
            continue  # Continúa con la siguiente imagen
        except Exception as e:
            print(f"[ERROR] Error al buscar {object_name} con el archivo {path}: {e}")

    if image_not_found_count == len(paths):
        print(f"[INFO] No se encontró {object_name} con ninguna de las imágenes proporcionadas.")

    return False


def take_screenshot(region):
    return pg.screenshot(region=region)

def resource_search_loop():
    while True:
        resource_found = any(
            click_image(paths, resource) for paths, resource in [
                (trigoPaths, "trigo"),
                (fresnoPaths, "fresno"),
                (castanoPaths, "castaño"),
                (ortigaPaths, "ortiga"),
               # (hierroPaths, "hierro")

            ]
        )
        if not resource_found:
            print("No se encontraron recursos. Intentando cambiar de mapa.")
            if change_map():
                print("Cambio de mapa exitoso. Reanudando la búsqueda de recursos.")
            else:
                print("Fallo al intentar cambiar de mapa.")
                break

# ... (resto del código antes de la función change_map)

def change_map():
    global CURRENT_DIRECTION_INDEX
    try:
        # Toma una captura de pantalla del área de interés y extrae el texto
        screenshot_before = take_and_save_screenshot("before_map_change.png", REGION_TO_CAPTURE)
        text_before = pytesseract.image_to_string(screenshot_before)
        print("[INFO] Estado del mapa antes del cambio:")
        print(f"       Texto extraído: {text_before.strip()}")

        # Intenta cambiar de mapa en una dirección
        direction = DIRECTIONS[CURRENT_DIRECTION_INDEX]
        print(f"[ACTION] Intentando cambiar de mapa hacia {direction}...")
        CURRENT_DIRECTION_INDEX = (CURRENT_DIRECTION_INDEX + 1) % len(DIRECTIONS)
        region = TOOLTIP_REGIONS[direction]
        pg.moveTo(region[0] + region[2] // 2, region[1] + region[3] // 2)
        pg.click()
        time.sleep(6)  # Tiempo de espera ajustable según la velocidad de cambio de mapa

        # Toma otra captura de pantalla después del cambio de mapa y extrae el texto
        # Captura y análisis del estado del mapa después del cambio
        screenshot_after = take_and_save_screenshot("after_map_change.png", REGION_TO_CAPTURE)
        text_after = pytesseract.image_to_string(screenshot_after)
        print("[INFO] Estado del mapa después del cambio:")
        print(f"       Texto extraído: {text_after.strip()}")

        # Comparación de textos para confirmar el cambio de mapa
        if text_before != text_after:
            print("[SUCCESS] El cambio de mapa parece haber sido exitoso.")
        else:
            print("[WARNING] No se detectaron cambios significativos en la posición del mapa.")

        return text_before != text_after  # Retorna True si hay un cambio, False si no

    except Exception as e:
        print(f"[ERROR] Excepción capturada durante el cambio de mapa: {e}")
        return False


# ... (resto del código posterior a la función change_map)

def capture_screenshot(pos, object_name, offset=25, size=100, directory="ojoIA"):
    if pos is None:
        print("Error: La posición pasada es None.")
        return
    try:
        x, y = int(pos.left + offset - size // 2), int(pos.top + offset - size // 2)
        region = (x, y, size, size)
        screenshot = pg.screenshot(region=region)
        screenshot_path = os.path.join(directory, f"{object_name}_screenshot.png")
        screenshot.save(screenshot_path)
        print(f"Captura guardada en {screenshot_path}")
    except Exception as e:
        print(f"Error al capturar o guardar la captura de pantalla: {e}")


def take_and_save_screenshot(filename, region):
    """Toma una captura de pantalla y la guarda en el directorio especificado."""
    screenshot = pg.screenshot(region=region)
    filepath = os.path.join(mapLocationDir, filename)
    screenshot.save(filepath)
    return Image.open(filepath)

def screenshots_are_different(img1, img2):
    """Compara dos imágenes y devuelve True si son diferentes."""
    diff = ImageChops.difference(img1, img2)
    if diff.getbbox():
        return True
    else:
        return False


# Para empezar la búsqueda de recursos
resource_search_loop()
