import tkinter as tk
from tkinter import Menu
import random
import os
import sys
import json
from pynput import mouse, keyboard
from PIL import Image, ImageTk

# Importamos la lógica de la tienda desde tu archivo tienda.py
from tienda import TiendaMascotas

class MascotaPro:

    def __init__(self, carpeta_recursos, tipo_mascota):
        self.carpeta_script = carpeta_recursos
        self.tipo_mascota = tipo_mascota
        self.archivo_guardado = os.path.join(self.carpeta_script, "datos_mascota.json")


        # --- DATOS DEL JUGADOR ---

        self.total_pulsaciones = 0
        self.monedas = 0
        self.nivel_recompensa = 0
        self.misiones = [2000, 5000, 10000, 50000, 100000]
        self.cargar_datos()

        # --- VENTANA PRINCIPAL ---
        self.window = tk.Tk()
        self.window.title(f"Mascota - AKUMARYUDOJO")
        self.window.overrideredirect(True)
        self.window.attributes('-topmost', True)
        self.window.geometry("350x480+500+150") # Espacio extra para el botón

        self.color_invisible = "#010101"
        self.window.config(bg=self.color_invisible)
        self.window.attributes('-transparentcolor', self.color_invisible)
        self.tamano_mascota_display = (128, 128)
       
        # Controladores de tiempo

        self.animacion_parpadeo_id = None
        self.animacion_mirar_derecha_id = None
        self.reset_alerta_id = None
        self.esta_en_alerta = False
        self.mirando_derecha = False

        # Carga inicial de imágenes

        self.sprites = {}
        self.cargar_recursos()

        # --- ELEMENTOS VISUALES ---
        self.label_mascota = tk.Label(self.window, image=self.sprites.get('normal'), bg=self.color_invisible, bd=0)
        self.label_mascota.pack(pady=20)

        self.label_stats = tk.Label(
            self.window,
            text=f"Pulsaciones: {self.total_pulsaciones}\nMonedas: {self.monedas}",
            bg=self.color_invisible, fg="yellow", font=("Consolas", 11, "bold")

        )

        self.label_stats.pack()
        meta_txt = self.misiones[self.nivel_recompensa] if self.nivel_recompensa < len(self.misiones) else "MAX"
        self.label_mision = tk.Label(
            self.window, text=f"Próxima meta: {meta_txt}",
            bg=self.color_invisible, fg="cyan", font=("Consolas", 10)

        )

        self.label_mision.pack()

        # BOTÓN TIENDA / EQUIPAR

        self.btn_tienda = tk.Button(
            self.window,
            text="🛒 TIENDA / EQUIPAR",
            command=self.abrir_tienda,
            font=("Arial", 9, "bold"),
            bg="#222", fg="white", activebackground="#444"

        )

        self.btn_tienda.pack(pady=15)

        # --- EVENTOS ---
        self.label_mascota.bind("<Button-3>", self.mostrar_menu)
        self.label_mascota.bind("<ButtonPress-1>", self.iniciar_arrastre)
        self.label_mascota.bind("<B1-Motion>", self.arrastrar)



        self.iniciar_escucha_global()
        self.iniciar_animaciones_automaticas()

        self.window.mainloop()



    # --- LÓGICA DE CAMBIO DE MASCOTA EN VIVO ---

    def cambiar_mascota_en_vivo(self, nueva_mascota):

        if self.tipo_mascota == nueva_mascota:

            return

        # Detener todo para evitar que el perro intente hacer animaciones de gato

        if self.animacion_parpadeo_id: self.window.after_cancel(self.animacion_parpadeo_id)
        if self.animacion_mirar_derecha_id: self.window.after_cancel(self.animacion_mirar_derecha_id)
        if self.reset_alerta_id: self.window.after_cancel(self.reset_alerta_id)



        self.tipo_mascota = nueva_mascota
        self.esta_en_alerta = False
        self.mirando_derecha = False
        self.sprites = {}
        self.cargar_recursos()

        if 'normal' in self.sprites:
            self.label_mascota.config(image=self.sprites['normal'])

        self.iniciar_animaciones_automaticas()

    def abrir_tienda(self):

        # Añadimos self.tipo_mascota al final para que la tienda sepa quién es el activo

        TiendaMascotas(

            self.window,
            self.monedas,
            self.actualizar_monedas_desde_tienda,
            self.cambiar_mascota_en_vivo,
            self.tipo_mascota

        )



    def actualizar_monedas_desde_tienda(self, nuevas_monedas):

        self.monedas = nuevas_monedas
        self.label_stats.config(text=f"Pulsaciones: {self.total_pulsaciones}\nMonedas: {self.monedas}")
        self.guardar_datos()

    # --- GESTIÓN DE DATOS ---

    def guardar_datos(self):

        datos = {

            "total_pulsaciones": self.total_pulsaciones,
            "monedas": self.monedas,
            "nivel_recompensa": self.nivel_recompensa

        }

        with open(self.archivo_guardado, "w") as f:

            json.dump(datos, f)

    def cargar_datos(self):

        if os.path.exists(self.archivo_guardado):
            with open(self.archivo_guardado, "r") as f:
                datos = json.load(f)
                self.total_pulsaciones = datos.get("total_pulsaciones", 0)
                self.monedas = datos.get("monedas", 0)
                self.nivel_recompensa = datos.get("nivel_recompensa", 0)



    def cargar_recursos(self):

        mapas = {

            'perro': {

                'normal': "perro_normal.png",
                'parpadeo': "perro_parpadeo.png",
                'alerta': "perro_alerta.png"

            },

            'gato': {

                'normal': "gato_reposo.png",
                'parpadeo': "gato_parpadeo.png",
                'derecha': "gato_derecha.png",
                'alerta': "gato_despierto.png"

            }

        }

        nombres = mapas.get(self.tipo_mascota)

        for clave, nombre in nombres.items():
            ruta = os.path.join(self.carpeta_script, nombre)
            if os.path.exists(ruta):
                img = Image.open(ruta).convert("RGBA").resize(self.tamano_mascota_display, Image.Resampling.LANCZOS)
                self.sprites[clave] = ImageTk.PhotoImage(img)

    # --- CICLOS DE ANIMACIÓN ---

    def iniciar_animaciones_automaticas(self):

        self.iniciar_ciclo_parpadeo()
        if self.tipo_mascota == 'gato':
            self.iniciar_ciclo_mirar_derecha()

    def iniciar_ciclo_parpadeo(self):
        if not self.esta_en_alerta and not self.mirando_derecha:
            self.animacion_parpadeo_id = self.window.after(random.randint(2000, 5000), self.hacer_parpadeo)

    def hacer_parpadeo(self):
        if not self.esta_en_alerta and not self.mirando_derecha and 'parpadeo' in self.sprites:
            self.label_mascota.config(image=self.sprites['parpadeo'])
            self.window.after(200, self.abrir_ojos)

    def abrir_ojos(self):
        if not self.esta_en_alerta and not self.mirando_derecha:
            self.label_mascota.config(image=self.sprites['normal'])
            self.iniciar_ciclo_parpadeo()

    def iniciar_ciclo_mirar_derecha(self):
        if not self.esta_en_alerta:
            self.animacion_mirar_derecha_id = self.window.after(random.randint(5000, 10000), self.mirar_a_la_derecha)

    def mirar_a_la_derecha(self):
        if not self.esta_en_alerta and 'derecha' in self.sprites:
            self.mirando_derecha = True
            if self.animacion_parpadeo_id: self.window.after_cancel(self.animacion_parpadeo_id)
            self.label_mascota.config(image=self.sprites['derecha'])
            self.window.after(random.randint(200, 490), self.volver_al_reposo)

    def volver_al_reposo(self):
        if not self.esta_en_alerta:
            self.mirando_derecha = False
            self.label_mascota.config(image=self.sprites['normal'])
            self.iniciar_ciclo_parpadeo()
            self.iniciar_ciclo_mirar_derecha()

    def ejecutar_animacion_alerta(self):
        self.total_pulsaciones += 1
        self.verificar_misiones()
        self.label_stats.config(text=f"Pulsaciones: {self.total_pulsaciones}\nMonedas: {self.monedas}")

        if self.reset_alerta_id: self.window.after_cancel(self.reset_alerta_id)

        if not self.esta_en_alerta:
            self.esta_en_alerta = True
            self.mirando_derecha = False

            if self.animacion_parpadeo_id: self.window.after_cancel(self.animacion_parpadeo_id)

            if self.animacion_mirar_derecha_id: self.window.after_cancel(self.animacion_mirar_derecha_id)

            if 'alerta' in self.sprites: self.label_mascota.config(image=self.sprites['alerta'])

        self.reset_alerta_id = self.window.after(1000, self.reset_mascota)

    def reset_mascota(self):
        self.esta_en_alerta = False
        self.reset_alerta_id = None

        if 'normal' in self.sprites:
            self.label_mascota.config(image=self.sprites['normal'])
            self.iniciar_animaciones_automaticas()

        self.guardar_datos()

    def verificar_misiones(self):
        if self.nivel_recompensa < len(self.misiones):

            if self.total_pulsaciones >= self.misiones[self.nivel_recompensa]:
                self.monedas += 100
                self.nivel_recompensa += 1
                self.guardar_datos()

                meta = self.misiones[self.nivel_recompensa] if self.nivel_recompensa < len(self.misiones) else "MAX"

                self.label_mision.config(text=f"Próxima meta: {meta}")

    def iniciar_escucha_global(self):

        mouse.Listener(on_click=lambda x,y,b,p: self.ejecutar_animacion_alerta() if p else None).start()

        keyboard.Listener(on_press=lambda k: self.ejecutar_animacion_alerta()).start()

    def iniciar_arrastre(self, event): self.x, self.y = event.x, event.y

    def arrastrar(self, event):

        x, y = self.window.winfo_x() + (event.x - self.x), self.window.winfo_y() + (event.y - self.y)

        self.window.geometry(f"+{x}+{y}")

    def mostrar_menu(self, event):
        menu_cierre = Menu(self.window, tearoff=0)
        menu_cierre.add_command(label="Cerrar y Guardar", command=self.cerrar_programa)
        menu_cierre.post(event.x_root, event.y_root)

    def cerrar_programa(self):
        self.guardar_datos()
        self.window.destroy()

        os._exit(0)

if __name__ == "__main__":

    MascotaPro(os.path.dirname(os.path.abspath(__file__)), "perro")