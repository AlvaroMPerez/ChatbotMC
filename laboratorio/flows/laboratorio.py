# flows/laboratorio.py
from services.whatsapp_service import send_whatsapp_message, send_whatsapp_buttons
from handlers.whatsapp_handlers import MessageHandler
from models.user_state import (
    set_user_state, 
    get_user_state, 
    clear_user_state)
from models.bloqueos import (clear_bloqueo,
                             set_bloqueo)
import os
from utils.helpers import is_8_hours

BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")


class Laboratorio:
    def __init__(self, handler: MessageHandler):
        self.handler    = handler
        self.wa_id      = handler.wa_id
        self.button_id  = (handler.button_id or "").strip()
        self.ts_raw     = handler.ts_raw

    # ---------- Router principal ----------
    def lab_flow(self) -> None:
        print(f"🧪 Ejecutando lab_flow con button_id: {self.button_id!r}")
        print(f"🧪 Estado del usuario: {get_user_state(self.wa_id)!r}")
        

        match self.button_id:
           # Aquí van los casos de los botones 
            case "2.1_info_si":
                self.cuenta_con_orden_medica()
                
            case "2.3_orden_medica_si":
                self.orden_medica_si()
            
            case "2.4_orden_medica_no":
                clear_user_state(self.wa_id)
                self.estudio_interes()
            
            case "2.2_info_no":
                self.tiene_duda()
                
            case "2.5_tiene_duda_si":
                self.agente_atiende()
                
            case "2.6_tiene_duda_no":
                self.finalizar()
            
            case "2.1_paciente_si" | "2.2_paciente_no":
                self.mas_informacion()
            
            case "2.1_cita_si" | "2.2_cita_no":
                self.politica_privacidad()
                self.agente_atiende()
            case "2.3_cambiar_cita":
                self.agente_atiende()
            
            case _:
                print("‼️ Sin coincidencia en Laboratorio")
                
    # ---------- Politica de privacidad ----------
    def politica_privacidad(self) -> None:
        body = ("Por favor, lea nuestra política de privacidad "
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tristique dapibus purus eget egestas. Lorem ipsum dolor sit amet, consectetur.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
    
    # ---------- Tiene cita? ----------
    def tiene_cita(self) -> None:
        body = "¿Tiene una cita programada?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_cita_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_cita_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ---------- Ha sido paciente? ----------
    def ha_sido_paciente(self) -> None:
        body = "¿Ha sido paciente de Medical Care anteriormente?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_paciente_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_paciente_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
     
    # ---------- Más información --------
    def mas_informacion(self) -> None:
        body = "¿Le gustaría más información?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.1_info_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.2_info_no", "title": "No"}},
            {"type": "reply", "reply": {"id": "2.3_cambiar_cita", "title": "Cambiar cita"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ---------- Cuenta con orden Médica? ----------
    def cuenta_con_orden_medica(self) -> None:
        body = "¿Cuenta con una orden médica?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.3_orden_medica_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.4_orden_medica_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    def orden_medica_si(self) -> None:
        body = ("Por favor, envíe una foto de su orden médica "
                "o escribala los estudios deseados en este chat para que podamos procesar su solicitud.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_orden_medica")
    # --------- Tiene alguna duda? ---------
    def tiene_duda(self) -> None:
        body = "¿Tiene alguna duda?"
        buttons = [
            {"type": "reply", "reply": {"id": "2.5_tiene_duda_si", "title": "Sí"}},
            {"type": "reply", "reply": {"id": "2.6_tiene_duda_no", "title": "No"}}
        ]
        send_whatsapp_buttons(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body, buttons)
    
    # ----------- Agente atiende ---------
    def agente_atiende(self) -> None:
        body = "Un agente de atención al cliente le atenderá en breve."
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)
        clear_bloqueo(self.wa_id)
        set_bloqueo(self.wa_id, self.ts_raw)
    
    # ----------- Estudio de interés -----------
    def estudio_interes(self) -> None:
        '''
         En deshuso por redundancia
        '''
        set_user_state(self.wa_id, "esperando_estudio_interes")
        body = ("Por favor, indíquenos el nombre del estudio "
                "en el que está interesado para que podamos ayudarle.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
    
    # ----------- Pedir nombre -----------
    def pedir_nombre (self) -> None:
        body = ("Por favor, proporcione su nombre completo "
                "para que podamos identificarlo correctamente.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_nombre")
    
    # ----------- Pedir fecha nacimiento -----------
    def pedir_fecha_nacimiento(self) -> None:
        body = ("Por favor, proporcione su fecha de nacimiento "
                "para que podamos identificarlo correctamente.")
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        set_user_state(self.wa_id, "esperando_fecha_nacimiento")
    
    # ------ Finalizar flujo -----
    def finalizar(self) -> None:
        body = "Gracias por contactarnos. ¡Que tenga un buen día!"
        send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, body)
        clear_user_state(self.wa_id)