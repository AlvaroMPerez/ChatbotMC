# handlers/message_handler.py
from services.whatsapp_service import (
    send_whatsapp_message,
    send_whatsapp_buttons)
from models.user_state import (
    get_user_state,
    set_user_state,
    clear_user_state
)
from utils.helpers import is_8_hours
from flows.dudas import espere_un_momento
import emoji, os
import datetime
import re

BUSINESS_PHONE_NUMBER_ID = os.getenv("BUSINESS_PHONE_NUMBER_ID")


class MessageHandler:
    # ---------- Inicialización ----------
    def __init__(self, wa_id: str, name: str, message: dict, body: str | None, horario: bool, ts_raw: int, hora_local:datetime) -> None:
        self.wa_id   = wa_id
        self.message = message
        self.body    = body or ""
        self.name    = self.clean_name(name)
        self.horario = horario
        self.ts_raw = ts_raw
        self.hora_local = hora_local
        

        # 1. Procesar saludos / info
        if message["type"] == "text":
            self._handle_text_greetings()

        # 2. Procesar estados 
        if message["type"] in ("text", "image"):
            self._handle_lab_states()

        # 3. Procesar botones
        if message["type"] == "interactive":
            self._handle_buttons()

    # ---------- Parte 1 – Saludos, información, promociones, ubicación----------
    def _handle_text_greetings(self) -> None: 
        """ 
        Maneja los mensajes de texto que contienen promociones
        """  
        
        passed, msg = is_8_hours(self.wa_id)
        
        if passed: 
            # clear_user_state(self.wa_id)  # Limpiamos el estado del usuario si ya pasaron 8 horas
            print(f"✅ Usuario desbloqueado: {msg}")
            user_state: str = get_user_state(self.wa_id)
            print (f"📝 Estado del usuario: {user_state!r}")    
            if self.wants_promotions():
                
                # Continua con el flujo normal
            
                if self.horario == True:  # Esto lo tengo que cambiar por debugging <-------
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Aquí tienes información sobre nuestras promociones vigentes."
                    )
                    # ---- Inicia flujo del bot ------
                    
                    lab.politica_privacidad()
                    lab.ha_sido_paciente()             
                    
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(. "
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
                
            elif self.wants_location():
                """
                Maneja los mensajes que contienen ubicación
                """
                if self.horario:
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Aquí tienes nuestra ubicación. "
                        "https://maps.app.goo.gl/a3239cawd54ucPxH9"
                    )
                    lab.politica_privacidad()
                    # ---- Inicia flujo del bot ------
                    lab.ha_sido_paciente()
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        (f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(. "
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                        "pero aquí tienes neustra ubicación. https://maps.app.goo.gl/a3239cawd54ucPxH9")  
                    )
            
            elif self.wants_appointment():
                """
                Maneja mensajes de texto que contengan palabras clave relacionadas con citas
                """
                is_8_hours(self.wa_id)
                if self.horario:
                    from flows.laboratorio import Laboratorio
                    lab: Laboratorio = Laboratorio(self)
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,("Bienvenido a Medical Care. Gustosamente le apoyo"
                                                                                "para que pueda agendar su cita."))
                    lab.politica_privacidad()
                    lab.ha_sido_paciente()
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            elif self.greetings():
                is_8_hours(self.wa_id)
                if self.horario:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! ¿En qué puedo ayudarte hoy?"
                    )
                else:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        f"¡Hola {self.name or 'paciente'}! Actualmente no nos encontramos en la oficina :(."
                        "Estamos disponibles de lunes a viernes de 7 AM a 3 PM."
                    )
            return  
        else:
            # Usuario bloqueado, no puede enviar mensajes
            print(f"❌ Usuario bloqueado: {msg}")
            send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id, msg)
            return
                 
        

    # ---------- Parte 2 – Estados de Laboratorio ----------
    def _handle_lab_states(self) -> None:
        """
        Gestiona los estados del usuario, dependiendo del estado cambia el flujo del bot.
        """
        from flows.laboratorio import Laboratorio

        lab  = Laboratorio(self)
        state = get_user_state(self.wa_id)
        
        match state:
            case"esperando_orden_medica":
                clear_user_state(self.wa_id)
                send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                    f"Gracias {self.name or 'paciente'}")
                # lab.estudio_interes()
                lab.pedir_nombre()
                
            case "esperando_estudio_interes":
                clear_user_state(self.wa_id)
                send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                    f"Gracias nuevamente {self.name or 'paciente'}")
                lab.pedir_nombre()
                
            case "esperando_nombre":
                clear_user_state(self.wa_id)
                self.name = self.clean_name(self.body)
                if not self.name:
                    send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                        "Por favor, envíe su nombre para continuar.")
                    set_user_state(self.wa_id, "esperando_nombre")
                    return   
                send_whatsapp_message(BUSINESS_PHONE_NUMBER_ID, self.wa_id,
                    f"Gracias {self.name or 'paciente'} por tu nombre. "
                )
                lab.pedir_fecha_nacimiento()
            
            case "esperando_fecha_nacimiento":
                clear_user_state(self.wa_id)
                lab.agente_atiende()
        
        
    # ---------- Parte 3 – Botones ----------
    def _handle_buttons(self) -> None:
        message_id = self.button_id

        # Laboratorio → todos los botones empiezan con "2"
        if message_id and message_id.startswith("2"):
            from flows.laboratorio import Laboratorio
            Laboratorio(self).lab_flow()
            return

    # ---------- Utilidades ----------
    @property
    def button_id(self) -> str | None:
        if self.message.get("type") == "interactive":
            return self.message.get("interactive", {}) \
                               .get("button_reply", {}) \
                               .get("id")
        return None

    #----- Promociones vigentes -----
    def wants_promotions(self) -> bool:
        PROMOTION_KEYWORDS = ["promociones", "promos", "info", "promoción", "promocion","información", "informacion",
                              "promo", "oferta", "ofertas", "descuento", "descuentos"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in PROMOTION_KEYWORDS for tok in tokens)
    
    # ------- Ubicación -------
    def wants_location(self) -> bool:
        LOCATION_KEYWORDS = ["ubicación", "dirección", "direcciónes","locacion","ubicacion","diraccion","direccion",
                             "unbicación"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in LOCATION_KEYWORDS for tok in tokens)

    # ---------- cita ----------
    def wants_appointment(self) -> bool:
        APPOINTMENT_KEYWORDS = ["cita", "turno", "agendar", "reservar", "horario"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in APPOINTMENT_KEYWORDS for tok in tokens)
    
    # --------- Saludos ---------
    def greetings(self) -> bool:
        GREETING_KEYWORDS = ["hola", "buenos días", "buenas tardes", "buenas noches", "saludos"]
        tokens = re.findall(r"\w+", self.body.lower())
        return any(tok in GREETING_KEYWORDS for tok in tokens)
    # ---------- Helpers ----------
    @staticmethod
    def is_emoji(ch: str) -> bool:
        return ch in emoji.EMOJI_DATA

    def clean_name(self, name: str) -> str:
        if not name:
            return ""
        if self.is_emoji(name):
            return ""
        return name.split()[0]