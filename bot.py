import pyautogui as pg
import time
import os
from PIL import ImageChops 


# Configuración de parámetros
mapLocationDir = "mapLocation"
imageOffset = 25
waitTime = 8
screenshotSize = 100
trigoPaths = ["ojoIA/trigo1.PNG", "ojoIA/trigo2.PNG", "ojoIA/trigo3.PNG","ojoIA/trigo4.PNG","ojoIA/trigo5.PNG"]
fresnoPaths = ["ojoIA/fresno1.PNG", "ojoIA/fresno2.PNG", "ojoIA/fresno3.PNG"]
castanoPaths = ["ojoIA/casta1.PNG", "ojoIA/casta2.PNG", "ojoIA/casta3.PNG", "ojoIA/casta4.PNG", "ojoIA/casta5.PNG" ]
ortigaPaths = ["ojoIA/ortiga1.PNG", "ojoIA/ortiga2.PNG", "ojoIA/ortiga3.PNG", "ojoIA/ortiga4.PNG", "ojoIA/ortiga5.PNG"]


confidenceLevel = 0.7
screenshotsDir = "ojoIA"
DIRECTIONS = ['down', 'down', 'right','right','up','up', 'up','left', 'left',]
CURRENT_DIRECTION_INDEX = 0
REGION_TO_CAPTURE = (200, 200, 880, 1720)
TOOLTIP_REGIONS = {
    'up': (960 - 50, 0, 100, 50),   
    'left': (0, 540 - 25, 100, 50),  
    'right': (1920 - 100, 540 - 25, 100, 50), 
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
    for path in paths:
        try:
            pos = pg.locateOnScreen(path, confidence=confidenceLevel)
            if pos:
                pg.moveTo(pos[0] + imageOffset, pos[1] + imageOffset)
                pg.click()
                print(f"SÍÍÍ SE ENCONTRÓ {object_name} y se hizo clic en {pos}.")
                time.sleep(waitTime)
                capture_screenshot(pos, object_name)
                return True
        except pg.ImageNotFoundException:
            print(f"No se encontró la imagen {object_name} en la pantalla con el archivo {path}.")
        except Exception as e:
            print(f"Error al buscar {object_name} con el archivo {path}: {e}")
    print(f"No se encontró {object_name} con ninguna de las imágenes proporcionadas.")
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
                (ortigaPaths, "ortiga")
            ]
        )
        if not resource_found:
            print("No se encontraron recursos. Intentando cambiar de mapa.")
            if change_map():
                print("Cambio de mapa exitoso. Reanudando la búsqueda de recursos.")
            else:
                print("Fallo al intentar cambiar de mapa.")
                break

def change_map():
    global CURRENT_DIRECTION_INDEX
    try:
        # Toma una captura de pantalla inicial del identificador del mapa
        initial_screenshot = take_and_save_screenshot("initial_map_location.png", REGION_TO_CAPTURE)

        # Intenta cambiar de mapa en una dirección
        direction = DIRECTIONS[CURRENT_DIRECTION_INDEX]
        CURRENT_DIRECTION_INDEX = (CURRENT_DIRECTION_INDEX + 1) % len(DIRECTIONS)
        region = TOOLTIP_REGIONS[direction]
        pg.moveTo(region[0] + region[2] // 2, region[1] + region[3] // 2)
        pg.click()
        time.sleep(3)  # Espera para que el cambio de mapa se complete

        # Toma una captura de pantalla después del intento de cambio de mapa
        after_screenshot = take_and_save_screenshot("after_map_change.png", REGION_TO_CAPTURE)

        # Compara las capturas de pantalla para verificar el cambio de mapa
        if not ImageChops.difference(initial_screenshot, after_screenshot).getbbox():
            print(f"Cambio de mapa {direction} fallido.")
            return False

        print(f"Cambio de mapa {direction} parece exitoso.")
        return True

    except Exception as e:
        print(f"Error durante el cambio de mapa: {e}")
        return False

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
    return screenshot

def screenshots_are_different(img1, img2):
    """Compara dos imágenes y devuelve True si son diferentes."""
    diff = ImageChops.difference(img1, img2)
    if diff.getbbox():
        return True
    else:
        return False


# Para empezar la búsqueda de recursos
resource_search_loop()
