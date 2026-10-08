import os
from curl_cffi import requests
from bs4 import BeautifulSoup

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URL = "https://www.elcorteingles.es/juguetes/A202035444-30th-blister-de-sobres-de-mejora-de-celebracion-30-aniversario-de-jcc-pokemon-pokemon-bandai/"

def enviar_telegram(mensaje):
    if TOKEN and CHAT_ID:
        url_api = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": mensaje}
        try:
            # Para el envío a Telegram usamos una petición directa
            import requests as req_std
            req_std.post(url_api, data=payload, timeout=10)
        except Exception as e:
            print(f"Error enviando mensaje a Telegram: {e}")

def comprobar_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    
    try:
        # impersonate="chrome120" camufla la conexión para saltar la protección 403
        respuesta = requests.get(URL, headers=headers, impersonate="chrome120", timeout=20)
        
        if respuesta.status_code != 200:
            print(f"La web respondió con estado {respuesta.status_code}. Posible bloqueo.")
            return

        soup = BeautifulSoup(respuesta.text, "html.parser")
        
        boton = soup.find("button", id="add_to_cart_main_button")
        
        if not boton:
            print("No se encontró el botón de compra principal.")
            return

        clases = boton.get("class", [])
        aria_disabled = boton.get("aria-disabled")
        
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
