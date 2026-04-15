import tkinter as tk
from tkinter import messagebox
import json
import os

class TiendaMascotas:
    def __init__(self, root, monedas_actuales, callback_monedas, callback_equipar, mascota_activa):
        self.window = tk.Toplevel(root)
        self.window.title("Tienda de Mascotas")
        self.window.geometry("300x450")
        
        self.monedas = monedas_actuales
        self.mascota_actual = mascota_activa # Recibimos cuál está puesta ahora
        self.actualizar_monedas_principal = callback_monedas
        self.equipar_mascota_principal = callback_equipar
        
        self.mascotas_compradas = self.cargar_propiedades()
        self.crear_interfaz()

    def cargar_propiedades(self):
        if os.path.exists("progreso_tienda.json"):
            with open("progreso_tienda.json", "r") as f:
                return json.load(f)
        return {"perro": True, "gato": False}

    def guardar_propiedades(self):
        with open("progreso_tienda.json", "w") as f:
            json.dump(self.mascotas_compradas, f)

    def crear_interfaz(self):
        # Limpiar ventana para refrescar
        for widget in self.window.winfo_children():
            widget.destroy()

        tk.Label(self.window, text=f"Tus Monedas: {self.monedas}", font=("Arial", 12, "bold")).pack(pady=10)
        
        lista_mascotas = [
            ("Pastor Alemán", "perro", 0),
            ("Gato Siamés", "gato", 150)
        ]

        for nombre, clave, precio in lista_mascotas:
            frame = tk.Frame(self.window, bd=1, relief="solid")
            frame.pack(pady=5, padx=10, fill="x")
            
            tk.Label(frame, text=nombre, font=("Arial", 10)).pack(side="left", padx=5)
            
            # LÓGICA DE BOTONES
            if clave == self.mascota_actual:
                # ESTADO: EQUIPADO (Color Azul)
                btn = tk.Button(frame, text="Equipado", fg="blue", font=("Arial", 9, "bold"), state="disabled")
                btn.pack(side="right", padx=5)
            
            elif self.mascotas_compradas.get(clave, False):
                # ESTADO: COMPRADO PERO NO ACTIVO
                btn = tk.Button(frame, text="Equipar", bg="#4CAF50", fg="white",
                               command=lambda c=clave: self.seleccionar(c))
                btn.pack(side="right", padx=5)
            
            else:
                # ESTADO: NO COMPRADO
                btn = tk.Button(frame, text=f"Comprar ({precio})", 
                               command=lambda c=clave, p=precio: self.comprar(c, p))
                btn.pack(side="right", padx=5)

    def comprar(self, mascota, precio):
        if self.monedas >= precio:
            self.monedas -= precio
            self.mascotas_compradas[mascota] = True
            self.guardar_propiedades()
            self.actualizar_monedas_principal(self.monedas)
            self.crear_interfaz() 
            messagebox.showinfo("Tienda", f"¡Has desbloqueado al {mascota}!")
        else:
            messagebox.showwarning("Tienda", "Monedas insuficientes.")

    def seleccionar(self, mascota):
        self.mascota_actual = mascota # Actualizar localmente para el refresco visual
        self.equipar_mascota_principal(mascota)
        self.crear_interfaz() # Refrescar para que el nuevo diga "Equipado" en azul