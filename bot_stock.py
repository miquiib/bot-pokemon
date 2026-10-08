import os
import requests
from bs4 import BeautifulSoup

# Obtenemos las claves secretas guardadas en GitHub Secrets
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# URL exactadel producto de El Corte Inglés
URL = "https://www.elcorteingles.es/juguetes/A202035444-30th-blister-de-sobres-de-mejora-de-celebracion-30-aniversario-de-jcc-pokemon-pokemon-bandai/"

def enviar_telegram(mensaje):
    if TOKEN and CHAT_ID:
        url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensaje}
        try:
            requests.post(url_api, data=payload, timeout=10)
        except Exception as e:
            print(f"Error enviando mensaje a Telegram: {e}")

def comprobar_stock():
    # Cabeceras para simular un navegador real en El Corte Inglés
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    
    try:
        respuesta = requests.get(URL, headers=headers, timeout=15)
        
        # Comprobar si la web responde correctamente
        if respuesta.status_code != 200:
            print(f"La web respondió con estado {respuesta.status_code}. Posible bloqueo.")
            return

        soup = BeautifulSoup(respuesta.text, "html.parser")
        
        # Buscamos el botón id="add_to_cart_main_button" de El Corte Inglés
        boton = soup.find("button", id="add_to_cart_main_button")
        
        if not boton:
            print("No se encontró el botón de compra principal.")
            return

        clases = boton.get("class", [])
        aria_disabled = boton.get("aria-disabled")
        
        # Verifica si está deshabilitado
        esta_deshabilitado = (aria_disabled == "true") or ("pds-button--is-disabled" in clases)
        
        if esta_deshabilitado:
            print("El producto de Pokémon en El Corte Inglés sigue AGOTADO...")
        else:
            print("¡¡HAY STOCK!! Enviando aviso a Telegram...")
            mensaje = (
                "🚨 ¡ATENCIÓN! STOCK DETECTADO EN EL CORTE INGLÉS 🚨\n\n"
                "El blíster de sobres Pokémon 30º Aniversario ya se puede añadir a la cesta.\n\n"
                f"Enlace directo:\n{URL}"
            )
            enviar_telegram(mensaje)
            
    except Exception as e:
        print(f"Error al consultar El Corte Inglés: {e}")

if __name__ == "__main__":
    comprobar_stock()