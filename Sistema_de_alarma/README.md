## 📍 Situación problemática
En la chipacería **Chispita Caliente**, ubicada en **Resistencia, Chaco**, los empleados tienen la costumbre de abrir la caja de los chipacitos sin autorización, consumiendo el producto destinado a la venta.  
Esto genera **pérdidas económicas** y **clientes insatisfechos**.  

Para resolver este problema, el dueño decidió implementar un **sistema casero antirrobo** utilizando un **microcontrolador Raspberry Pi Pico W**, junto con sensores y actuadores, para **detectar y alertar** cualquier intento de manipulación o robo.

---

## ⚙️ Lógica de estados

| Estado | Descripción | Acción |
|:--:|:--|:--|
| **0 - Normal** | No se detecta ningún evento. | El display muestra “0”. |
| **1 - Inclinación** | Si el *tilt switch* detecta inclinación durante 1 segundo. | El display muestra “1” y el LED titila 5 veces. |
| **2 - Luz sospechosa** | Luego de la inclinación, se detecta luz durante 1 segundo. | El display muestra “2” y el buzzer suena 2 veces. |
| **3 - Alarma de robo** | Se detecta nuevamente luz durante 1 segundo. | El display muestra “3” y tanto el LED como el buzzer se activan varias veces. |

---

## 💻 Control serial

Mediante el **puerto serial**, el usuario encargado puede:

- **Consultar el estado** con el comando `status`, visualizando:
  - Estado actual  
  - Cantidad de activaciones de cada sensor  
  - Hora de la última alarma  
- **Reiniciar el sistema** con el comando `reset`, volviendo al estado “0”.

### 🧩 Orden de detección
Para evitar falsas alarmas, el sistema **debe detectar primero la inclinación y luego la luz**.  
Si se detecta luz antes de la inclinación, los estados no se activan.

---

## 🔄 Lazos de control

### Sin eventos:
- Mantener Display en “0”.

### Lazo 1 (Inclinación):
- Lee el *tilt switch*.  
- Si hay inclinación por 1 segundo → LED 5 veces → Display “1”.

### Lazo 2 (Luz):
- Lee el potenciómetro (simulando la fotoresistencia).  
- Si detecta luz por 1 segundo → Buzzer 2 veces → Display “2”.

### Integración:
- Si ambas condiciones se cumplen → Display “3” + LED titilando + Buzzer activado.

---

## 🧩 Componentes principales

### 🥇 Raspberry Pi Pico W
Placa de desarrollo basada en el microcontrolador **RP2040**, diseñada por Raspberry Pi.  
Incluye conectividad **Wi-Fi**, múltiples pines GPIO y permite programar en **MicroPython o CircuitPython**.  
En el sistema actúa como **unidad central de control**, gestionando las entradas de los sensores y las salidas hacia los actuadores.

---

### 🌞 Fotoresistencia (KY-018)
Sensor que **varía su resistencia según la cantidad de luz recibida**.  
A mayor iluminación, menor resistencia, y viceversa.  
> 🔧 *Fue reemplazada por un potenciómetro debido a un defecto en el componente original.*

---

### 🎚️ Potenciómetro
Resistor variable de tres terminales que permite ajustar manualmente un valor de tensión o resistencia.  
En este proyecto **simula la fotoresistencia**, permitiendo variar la resistencia para emular diferentes niveles de luz.

---

### ⚙️ Tilt Switch (KY-017)
Sensor de **inclinación o vibración** que contiene una pequeña esfera metálica en su interior.  
Cuando el sensor cambia de posición, la esfera **abre o cierra el circuito**, generando una señal digital.  
Permite detectar movimiento o manipulación del objeto protegido.

---

### 🔊 Buzzer
Transductor acústico que **emite sonido cuando recibe una señal eléctrica**.  
Se utiliza como **alarma sonora** en los estados de luz sospechosa o robo.

---

### 💡 LED y resistencia
El **LED** (diodo emisor de luz) convierte corriente eléctrica en luz visible.  
Se coloca una **resistencia en serie** para **limitar la corriente** y proteger el componente, evitando que se queme.

---

### 🔢 Display de 7 segmentos
Conjunto de siete LEDs dispuestos en forma de número 8.  
Permite representar los dígitos del 0 al 9.  
El microcontrolador enciende los segmentos necesarios para **mostrar el estado actual del sistema**.

---

## 🧠 Diagrama del circuito

![Diagrama del circuito](16800bca-0ffb-4c73-b949-e0badb663de6.png)

---

## 🧾 Consideraciones

Durante el armado del microcontrolador, se presentaron algunos inconvenientes.  
Inicialmente, el **buzzer** no funcionaba correctamente, por lo que fue reemplazado por uno nuevo.  
Asimismo, la **fotoresistencia KY-018** no censaba los valores de luz adecuadamente, motivo por el cual fue sustituida por un **potenciómetro**, utilizado para simular la detección de luminosidad.

---

## 🛠️ Cómo ejecutar el proyecto

### 📦 Requisitos
- **Visual Studio Code** con la extensión *Pico-W-Go* o *Thonny*.  
- **Firmware de MicroPython** cargado en la Raspberry Pi Pico W.  
- **Cable micro USB** para conexión al PC.  
- Librerías estándar de MicroPython.

### ▶️ Pasos
1. Conectar la **Raspberry Pi Pico 2W** al ordenador mediante USB.  
2. Abrir el proyecto en **VS Code** o en la consola con el comando **picocom**
3. Subir el archivo `code.py` al microcontrolador.  
4. Abrir el **Serial Monitor** para observar las lecturas de sensores y los estados.  
5. Escribir los comandos disponibles:
   - `status` → muestra el estado actual.  
   - `reset` → reinicia el sistema.  
6. Manipular el **potenciómetro** (simulando luz) y el **tilt switch** para observar los cambios de estado en el display y las alarmas.

---

## 🌐 Código fuente (segunda parte)

Para la segunda parte se implementó con todo el curso una **comunicación entre los microcontroladores dentro de una red de dispositivos IoT** mediante el protocolo **MQTT (Message Queuing Telemetry Transport)**.  
Esto permite el **envío de datos captados por sensores hacia un broker central**, desde donde pueden ser visualizados o analizados.

El siguiente código establece la **conexión WiFi** utilizando el nombre y la contraseña configurados.  
Una vez conectado, el microcontrolador obtiene una **dirección IP**, confirmando su integración a la red local.

Al establecer la conexión con el **broker MQTT**, el dispositivo envía un mensaje inicial al tópico `"descubrir"`, en formato **JSON**, donde informa su **nombre** y las **magnitudes que es capaz de medir**.

La función `publish()` se encarga de **enviar, cada 5 segundos**, los valores capturados por los sensores (en este caso una **fotoresistencia** y un **sensor de inclinación**), publicándolos en el tópico correspondiente del broker.

---


Proyecto de laboratorio - Ingeniería en Sistemas de Información  
Universidad Tecnológica Nacional (UTN)
