import board # pyright: ignore[reportMissingImports] 
import time 
import digitalio 
import analogio 
import json 
import time 
import wifi 
import socketpool 
import adafruit_minimqtt.adafruit_minimqtt as MQTT 
import supervisor

# Configuracion de RED 
SSID = "wfrre-Docentes" 
PASSWORD = "20$tscFrre.24" 
BROKER = "10.13.100.154" 
NOMBRE_EQUIPO = "benders" 
DESCOVERY_TOPIC = "descubrir" 
TOPIC = f"sensores/{NOMBRE_EQUIPO}" 

print(f"Intentando conectar a {SSID}...") 
try: 
        wifi.radio.connect(SSID, PASSWORD) 
        print(f"Conectado a {SSID}") 
        print(f"Direccion IP: {wifi.radio.ipv4_address}") 
except Exception as e: 
    print(f"Error al conectar a WiFi: {e}") 
    while True: 
        pass 

# Configuracion MQTT 
pool = socketpool.SocketPool(wifi.radio) 
def connect(client, userdata, flags, rc): 
    print("Conectado al broker MQTT") 
    client.publish(DESCOVERY_TOPIC, json.dumps({"equipo":NOMBRE_EQUIPO,"magnitudes": ["luz", "inclinacion"]})) 
    
mqtt_client = MQTT.MQTT( 
    broker=BROKER, 
    port=1883, 
    socket_pool=pool 
) 
    
mqtt_client.on_connect = connect 
mqtt_client.connect() 

# Usamos estas varibles globales para controlar cada cuanto publicamos 
last_pub = 0 
PUB_INTERVAL = 5 
    
def publish(): 
    global last_pub 
    now = time.monotonic() 
    print(sensor_luz.value) 
    if now - last_pub >= PUB_INTERVAL: 
        try: 
            luz_topic = f"{TOPIC}/luz" 
            mqtt_client.publish(luz_topic, str(sensor_luz.value)) 
            
            incl_topic = f"{TOPIC}/inclinacion" 
            mqtt_client.publish(incl_topic, str(sensor_inclinacion.value)) 
            
            last_pub = now 
        except Exception as e: 
            print(f"Error publicando MQTT: {e}") 
            
led = digitalio.DigitalInOut(board.GP15)
led.direction = digitalio.Direction.OUTPUT

buzzer = digitalio.DigitalInOut(board.GP14)
buzzer.direction = digitalio.Direction.OUTPUT

# --- Sensores ---
sensor_luz = analogio.AnalogIn(board.GP28)
sensor_inclinacion = digitalio.DigitalInOut(board.GP27)
sensor_inclinacion.direction = digitalio.Direction.INPUT
sensor_inclinacion.pull = digitalio.Pull.DOWN

# --- Display 7 segmentos ---
segmentos = {
    "a": digitalio.DigitalInOut(board.GP4),
    "b": digitalio.DigitalInOut(board.GP5),
    "c": digitalio.DigitalInOut(board.GP8),
    "d": digitalio.DigitalInOut(board.GP7),
    "e": digitalio.DigitalInOut(board.GP6),
    "f": digitalio.DigitalInOut(board.GP3),
    "g": digitalio.DigitalInOut(board.GP2),
}

for seg in segmentos.values():
    seg.direction = digitalio.Direction.OUTPUT

numeros = {
    0: ["a", "b", "c", "d", "e", "f"],
    1: ["b", "c"],
    2: ["a", "b", "d", "e", "g"],
    3: ["a", "b", "c", "d", "g"]
}

def apagar_display():
    for seg in segmentos.values():
        seg.value = False

def mostrar_numero(n):
    apagar_display()
    if n in numeros:
        for seg in numeros[n]:
            segmentos[seg].value = True

def beep(times):
    for _ in range(times):
        buzzer.value = True
        time.sleep(0.2)
        buzzer.value = False
        time.sleep(0.2)

def blink_led(times):
    for _ in range(times):
        led.value = True
        time.sleep(0.2)
        led.value = False
        time.sleep(0.2)

# --- Variables globales ---
estado = 0
umbral_luz = 20000
tilt_count = 0
luz_eventos = 0
ultimo_tilt = 0
luz_activa = False
ultima_lectura = time.monotonic()
ultima_alarma = None
inclinacion_detectada = False

# --- Funciones de control serial ---
def guardar_estado(_):
    pass  

def cargar_estado():
    return 0  # Devuelve estado inicial

def mostrar_estado():
    print("Estado actual:", estado)
    print("Inclinacion detectada:", inclinacion_detectada)
    print("Luz detectada:", luz_eventos)

def resetear():
    global estado, inclinacion_detectada, luz_eventos, tilt_count
    estado = 0
    inclinacion_detectada = False
    luz_eventos = 0
    tilt_count = 0
    mostrar_numero(0)
    print("Sistema reiniciado.")

# --- Inicialización ---
mostrar_numero(0)
print("Sistema iniciado: Estado 0 (Todo en orden!)")

# --- Bucle principal ---
while True:
    tilt_val = sensor_inclinacion.value
    luz_val = sensor_luz.value

    # Mostrar cada segundo
    if time.monotonic() - ultima_lectura >= 1:
        print(f"Luz: {luz_val} | Inclinacion: {tilt_val} | Estado: {estado}")
        ultima_lectura = time.monotonic()

    # --- Detectar inclinacion ---
    if tilt_val == 1 and ultimo_tilt == 0:
        tilt_count += 1
        ultimo_tilt = 1
        start_tilt = time.monotonic()
        while sensor_inclinacion.value == 1:
            if time.monotonic() - start_tilt >= 1:  # 1 segundo de inclinación
                estado = 1
                inclinacion_detectada = True
                mostrar_numero(1)
                blink_led(5)
                print(" Estado 1: Inclinación detectada")
                break
        time.sleep(0.1)
    elif tilt_val == 0:
        ultimo_tilt = 0

    # --- Detectar luz ---
    if luz_val > umbral_luz and not luz_activa and estado >= 1:
        start_light = time.monotonic()
        while sensor_luz.value > umbral_luz:
            if time.monotonic() - start_light >= 1:
                luz_eventos += 1
                luz_activa = True
                if luz_eventos == 1 and estado < 2:
                    estado = 2
                    mostrar_numero(2)
                    beep(2)
                    print(" Estado 2: Luz sospechosa detectada")
                elif luz_eventos >= 2:
                    estado = 3
                    mostrar_numero(3)
                    ultima_alarma = time.localtime()
                    print(" Estado 3: ¡Alarma de robo!")
                    for _ in range(3):
                        blink_led(3)
                        beep(3)
                break
        time.sleep(0.1)
    elif luz_val <= umbral_luz:
        luz_activa = False
        publish()

    # --- Lectura de comandos seriales ---
    if supervisor.runtime.serial_bytes_available:
        comando = input().strip().lower()
        if comando == "status":
            mostrar_estado()
        elif comando == "reset":
            resetear()