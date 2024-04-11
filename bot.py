import pytesseract
import pandas as pd
from PIL import Image
import pyautogui as pg
import time
import os
from PIL import ImageChops 
import re

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
salviaPaths = ["ojoIA/salvia1.PNG","ojoIA/salvia2.PNG"]
nogalPaths = ["ojoIA/nogal1.PNG","ojoIA/nogal2.PNG", "ojoIA/nogal3.PNG"]

hierroPaths = ["ojoIA/hierro1.PNG", "ojoIA/hierro2.PNG", "ojoIA/hierro3.PNG","ojoIA/hierro4.PNG", "ojoIA/hierro5.PNG"]


confidenceLevel = 0.7
screenshotsDir = "ojoIA"
DIRECTIONS = [ 'right','right', 'up','up','right','up','up','right','down','down','down','up','up','right','right','up','right','up','up','left','up','right','up','left']
#1,23 TR
#4,21
CURRENT_DIRECTION_INDEX = 0
REGION_TO_CAPTURE = (0, 65, 100 , 90-50)
COMBAT_MODE_REGION = (0, 65, 100, 40)
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

map_data_statistics = {}

if not os.path.exists(mapLocationDir):
    os.makedirs(mapLocationDir)

if not os.path.exists(screenshotsDir):
    os.makedirs(screenshotsDir)

def update_map_statistics(coordinates, zone_name):
    """Agrega los datos del mapa al diccionario y los escribe en Excel."""
    # Si la zona no está en el diccionario, la añade
    if zone_name not in map_data_statistics:
        map_data_statistics[zone_name] = {'coordinates': coordinates, 'count': 1}
    else:
        # Si la zona ya está, solo incrementa el contador
        map_data_statistics[zone_name]['count'] += 1

    # Convierte el diccionario a DataFrame de pandas para escribir en Excel
    df = pd.DataFrame.from_dict(map_data_statistics, orient='index')

    # Define la ruta del archivo Excel dentro del directorio mapLocationDir
    excel_path = os.path.join(mapLocationDir, 'map_data_statistics.xlsx')
    # Escribe el DataFrame en un archivo Excel
    df.to_excel(excel_path, index_label='Zone')

def is_exception_case(object_name, pos):
    # Definimos las excepciones previsibles
    exceptions = {
        'fresno': {
            'ignored_positions': [(1438, 822)],  # Lista de posiciones a ignorar
        },
        'trigo': {
            'special_click_offsets': [(907, 588, 4, 0)],  # (x, y, offset_x, offset_y) donde x, y es la posición a buscar y (offset_x, offset_y) es cuánto mover el mouse antes de clickear
        }
    }

    # Verificamos si el objeto actual tiene alguna excepción
    if object_name in exceptions:
        # Para el caso de fresno ignorado
        if 'ignored_positions' in exceptions[object_name]:
            for ignored_pos in exceptions[object_name]['ignored_positions']:
                if pos.left == ignored_pos[0] and pos.top == ignored_pos[1]:
                    print(f"[INFO] {object_name} encontrado en posición ignorada: {ignored_pos}. Ignorando...")
                    return True  # Retorna True si es una excepción

        # Para el caso de trigo que necesita un clic especial
        if 'special_click_offsets' in exceptions[object_name]:
            for special_click in exceptions[object_name]['special_click_offsets']:
                if pos.left == special_click[0] and pos.top == special_click[1]:
                    # Realiza el clic especial
                    pg.moveTo(pos.left + special_click[2], pos.top + special_click[3])
                    pg.click()
                    print(f"[INFO] Clic especial para {object_name} realizado en {pos.left + special_click[2]}, {pos.top + special_click[3]}.")
                    return True  # Retorna True si es una excepción

    return False 

def click_image(paths, object_name):
    image_not_found_count = 0

    for path in paths:
        try:
            print(f"[BUSCANDO] {object_name}...")
            pos = pg.locateOnScreen(path, confidence=confidenceLevel)

            # Verifica si la posición encontrada es una excepción
            if pos and is_exception_case(object_name, pos):
                continue  # Ignora esta posición y continúa con la siguiente imagen

            if pos:
                # Ajuste para salvia: mover un píxel más arriba antes de clickear
                if object_name == 'salvia':
                    click_x, click_y = pos.left + imageOffset, pos.top + imageOffset - 1
                else:
                    click_x, click_y = pos.left + imageOffset, pos.top + imageOffset

                pg.moveTo(click_x, click_y)
                pg.click()
                print(f"[INFO] {object_name} encontrado y clickeado en {pos}.")
                time.sleep(waitTime)
                #capture_screenshot(pos, object_name)
                return True

        except pg.ImageNotFoundException:
            image_not_found_count += 1
        except Exception as e:
            print(f"[ERROR] Error al buscar {object_name} con {path}: {e}")

    if image_not_found_count == len(paths):
        print(f"[INFO] {object_name} no encontrado con las imágenes proporcionadas.")

    return False

def take_screenshot(region):
    return pg.screenshot(region=region)

def resource_search_loop():
    while True:
        try:
            if is_in_combat_mode():
                print("[INFO] Modo combate detectado. Entrando en flujo de combate...")
                while is_in_combat_mode():
                    print("[INFO] En combate, esperando a que finalice...")
                    time.sleep(5)  # Espera un tiempo antes de volver a chequear.
                print("[INFO] Modo combate finalizado. Reanudando búsqueda de recursos.")
                continue
        except Exception as e:
            print(f"[ERROR] Un error ocurrió mientras se verificaba el modo de combate: {e}")
        print("[FASE] Comenzando búsqueda de recursos...")
        
        resource_found = False
        for paths, resource in [(trigoPaths, "trigo"), (fresnoPaths, "fresno"), (castanoPaths, "castaño"),(nogalPaths, "nogal"), (ortigaPaths, "ortiga"),(salviaPaths, "salvia")]:
            resource_found = click_image(paths, resource)
            if resource_found:
                break  # Si se encuentra un recurso, rompe el bucle y reinicia la búsqueda

        if not resource_found:
            print("[INFO] No se encontraron recursos. Intentando cambiar de mapa...")
            change_map_result = change_map()
            if change_map_result == True:
                print("[INFO] Cambio de mapa exitoso.")
            elif change_map_result == 'combat':
                print("[INFO] Modo combate detectado durante el cambio de mapa. Pausando búsqueda de recursos.")
                while is_in_combat_mode():
                    print("[INFO] En combate, esperando a que finalice...")
                    time.sleep(5)
                print("[INFO] Modo combate finalizado. Reanudando búsqueda de recursos.")
            else:
                print("[ERROR] Fallo al cambiar de mapa. Deteniendo la búsqueda.")
                break  # Sale del bucle si falla el cambio de mapa.

def change_map():
    global CURRENT_DIRECTION_INDEX
    try:
        # Toma una captura de pantalla del área de interés y extrae el texto para estadísticas
        screenshot_before = take_and_save_screenshot("before_map_change.png", REGION_TO_CAPTURE)
        text_before = pytesseract.image_to_string(screenshot_before).strip()
        print("[INFO] Estado del mapa antes del cambio:")
        print(f"       Texto extraído para estadísticas: {text_before}")

        # Actualiza las estadísticas antes del cambio de mapa
        update_map_statistics("Before Change", text_before)

        # Intenta cambiar de mapa en una dirección
        direction = DIRECTIONS[CURRENT_DIRECTION_INDEX]
        print(f"[ACTION] Intentando cambiar de mapa hacia {direction}...")
        CURRENT_DIRECTION_INDEX = (CURRENT_DIRECTION_INDEX + 1) % len(DIRECTIONS)
        region = TOOLTIP_REGIONS[direction]
        pg.moveTo(region[0] + region[2] // 2, region[1] + region[3] // 2)
        pg.click()
        time.sleep(6)  # Tiempo de espera ajustable según la velocidad de cambio de mapa

        # Toma otra captura de pantalla después del cambio de mapa
        screenshot_after = take_and_save_screenshot("after_map_change.png", REGION_TO_CAPTURE)
        text_after = pytesseract.image_to_string(screenshot_after).strip()
        print("[INFO] Estado del mapa después del cambio:")
        print(f"       Texto extraído para estadísticas: {text_after}")

        # Actualiza las estadísticas después del cambio de mapa
        update_map_statistics("After Change", text_after)

        # Utiliza ImageChops para verificar si hay diferencia entre las imágenes
        if ImageChops.difference(screenshot_before, screenshot_after).getbbox() is None:
            print("[WARNING] No se detectaron cambios en las coordenadas del mapa.")
            # Llama a is_in_combat_mode para comprobar si estamos en modo combate
            if is_in_combat_mode():
                print("[INFO] Entrando en flujo de combate...")
                # Aquí iría la lógica para manejar el modo combate
                # break # Si deseas salir del bucle en este punto
                return 'combat'  # Puedes retornar un valor específico para indicar el modo combate
            else:
                print("[INFO] No se detectó el modo combate, puede ser un fallo al cambiar de mapa.")
                return False
        else:
            print("[SUCCESS] El cambio de mapa parece haber sido exitoso.")
            return True

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

def extract_information(text):
    """Extrae la información cruda sin usar regex."""
    return text.strip()

def is_in_combat_mode():
    try:
        # Definir la región donde se busca el indicador de combate.
        COMBAT_INDICATOR_REGION = (1310, 930, 165 , 75)  # x, y, ancho, alto
        
        # Ruta a la imagen del indicador de combate.
        combat_indicator_image_path = 'ojoIA/combat_indicator.PNG'

        # Verificar si el indicador de combate está presente en la región definida.
        combat_indicator = pg.locateOnScreen(combat_indicator_image_path, region=COMBAT_INDICATOR_REGION, confidence=0.4)

        if combat_indicator:
            print("[INFO] Modo combate detectado.")
            return True
        else:
            print("[INFO] No se detectó el modo combate.")
            return False
    except Exception as e:
        print(f"[ERROR] Un error ocurrió mientras se verificaba el modo de combate: {e}")
        # Dependiendo de tu flujo, podrías querer retornar False o manejar de otra manera
        return False


# Para empezar la búsqueda de recursos
resource_search_loop()
