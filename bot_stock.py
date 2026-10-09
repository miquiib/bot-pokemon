import os
import datetime
from curl_cffi import requests
from bs4 import BeautifulSoup

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URL = "https://www.elcorteingles.es/juguetes/A202035444-30th-blister-de-sobres-de-mejora-de-celebracion-30-aniversario-de-jcc-pokemon-pokemon-bandai/"

def obtener_o_crear_mensaje_fijado():
    if not TOKEN or not CHAT_ID:
        return None
    
    # 1. Consultar si ya existe un mensaje fijado en el chat
    url_get_chat = f"https://api.telegram.org/bot{TOKEN}/getChat"
    try:
        resp = requests.post(url_get_chat, data={"chat_id": CHAT_ID}, timeout=10)
        data = resp.json()
        if data.get("ok") and "pinned_message" in data.get("result", {}):
            return data["result"]["pinned_message"]["message_id"]
    except Exception as e:
        print(f"Error consultando getChat: {e}")

    # 2. Si no hay mensaje fijado, enviamos uno inicial y lo fijamos
    url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "📌 [PANEL DE ESTADO] Iniciando monitor de stock...",
        "disable_notification": "true"
    }
    try:
        resp = requests.post(url_send, data=payload, timeout=10)
        data = resp.json()
        if data.get("ok"):
            msg_id = data["result"]["message_id"]
            url_pin = f"https://api.telegram.org/bot{TOKEN}/pinChatMessage"
            requests.post(url_pin, data={"chat_id": CHAT_ID, "message_id": msg_id, "disable_notification": "true"}, timeout=10)
            return msg_id
    except Exception as e:
        print(f"Error creando mensaje fijado: {e}")
        
    return None

def actualizar_estado_sin_notificacion(texto_estado):
    msg_id = obtener_o_crear_mensaje_fijado()
    if msg_id and TOKEN and CHAT_ID:
        url_edit = f"https://api.telegram.org/bot{TOKEN}/editMessageText"
        payload = {
            "chat_id": CHAT_ID,
            "message_id": msg_id,
            "text": texto_estado
        }
        try:
            requests.post(url_edit, data=payload, timeout=10)
        except Exception as e:
            print(f"Error editando mensaje: {e}")

def enviar_alerta_stock(mensaje_texto):
    if TOKEN and CHAT_ID:
        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": mensaje_texto
        }
        try:
            requests.post(url_send, data=payload, timeout=10)
        except Exception as e:
            print(f"Error enviando alerta de stock: {e}")

def comprobar_stock():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    
    try:
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
        
        # Hora actual para indicar en el mensaje de estado
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")

        if esta_deshabilitado:
            print("El producto de Pokémon en El Corte Inglés sigue AGOTADO...")
            texto_estado = (
                f"📌 [PANEL DE ESTADO]\n\n"
                f"Última comprobación: {hora_actual}\n"
                f"Estado: 🔴 AGOTADO\n\n"
                f"El bot sigue revisando automáticamente."
            )
            # Edita el mensaje fijado (generando 0 notificaciones)
            actualizar_estado_sin_notificacion(texto_estado)
        else:
            print("¡¡HAY STOCK!! Enviando aviso a Telegram...")
            mensaje = (
                "🚨 ¡ATENCIÓN! STOCK DETECTADO EN EL CORTE INGLÉS 🚨\n\n"
                "El blíster de sobres Pokémon 30º Aniversario ya se puede añadir a la cesta.\n\n"
                f"Enlace directo:\n{URL}"
            )
            # Envía un mensaje totalmente NUEVO que sí hace sonar la alarma
            enviar_alerta_stock(mensaje)
            
    except Exception as e:
        print(f"Error al consultar El Corte Inglés: {e}")

if __name__ == "__main__":
    comprobar_stock()
