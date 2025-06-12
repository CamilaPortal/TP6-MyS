"""
TP 6: Modelo y Simulación de un Sistema de Atención al Público
Simulador de boxes de atención con visualización gráfica animada
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict
from collections import deque

@dataclass
class Cliente:
    """Representa un cliente en el sistema"""
    id: int
    tiempo_ingreso: int  # en segundos desde apertura
    tiempo_inicio_atencion: Optional[int] = None
    tiempo_fin_atencion: Optional[int] = None
    box_asignado: Optional[int] = None
    abandono: bool = False
    tiempo_abandono: Optional[int] = None
    posicion_x: float = 0.0  # Para animación
    posicion_y: float = 0.0  # Para animación
    
    @property
    def tiempo_espera(self) -> Optional[int]:
        """Calcula el tiempo de espera en cola"""
        if self.tiempo_inicio_atencion is not None:
            return self.tiempo_inicio_atencion - self.tiempo_ingreso
        elif self.abandono and self.tiempo_abandono is not None:
            return self.tiempo_abandono - self.tiempo_ingreso
        return None
    
    @property
    def tiempo_atencion(self) -> Optional[int]:
        """Calcula el tiempo de atención en box"""
        if self.tiempo_inicio_atencion is not None and self.tiempo_fin_atencion is not None:
            return self.tiempo_fin_atencion - self.tiempo_inicio_atencion
        return None

@dataclass
class Box:
    """Representa un box de atención"""
    id: int
    ocupado: bool = False
    cliente_actual: Optional[Cliente] = None
    tiempo_fin_atencion: Optional[int] = None
    posicion_x: float = 0.0  # Para animación
    posicion_y: float = 0.0  # Para animación

class SimuladorAtencionPublico:
    """Simulador principal del sistema de atención"""
    
    def __init__(self, num_boxes: int, velocidad_animacion: float = 1.0):
        # Validación de parámetros
        if not 1 <= num_boxes <= 10:
            raise ValueError("El número de boxes debe estar entre 1 y 10")
        
        self.num_boxes = num_boxes
        self.velocidad_animacion = velocidad_animacion
        
        # Inicialización de componentes
        self.boxes = [Box(i) for i in range(num_boxes)]
        self.cola = deque()
        self.clientes_ingresados = []
        self.clientes_atendidos = []
        self.clientes_abandonaron = []
        
        # Parámetros de simulación (según especificaciones)
        self.DURACION_SIMULACION = 4 * 3600  # 4 horas (8-12) en segundos
        self.PROB_INGRESO = 1/144  # Probabilidad por segundo de ingreso de cliente
        self.TIEMPO_MAX_ESPERA = 30 * 60  # 30 minutos en segundos
        self.MEDIA_ATENCION = 10 * 60  # 10 minutos en segundos
        self.DESVIO_ATENCION = 5 * 60  # 5 minutos en segundos
        self.COSTO_BOX = 1000  # Costo por box por día
        self.PERDIDA_CLIENTE = 10000  # Pérdida por cliente que abandona
        
        # Variables de control
        self.tiempo_actual = 0
        self.contador_clientes = 0
        self.simulacion_activa = False
        
        # Para animación
        self.fig = None
        self.ax = None
        self.rectangulos_boxes = []
        self.rectangulos_clientes = []
        self.texto_info = None
        self.frames_guardados = []
        
        # Estadísticas
        self.estadisticas = {
            'clientes_ingresados': 0,
            'clientes_atendidos': 0,
            'clientes_abandonaron': 0,
            'tiempo_min_atencion': float('inf'),
            'tiempo_max_atencion': 0,
            'tiempo_min_espera': float('inf'),
            'tiempo_max_espera': 0,
            'costo_total': 0
        }
    
    def generar_tiempo_atencion(self) -> int:
        """Genera un tiempo de atención usando distribución normal"""
        tiempo = np.random.normal(self.MEDIA_ATENCION, self.DESVIO_ATENCION)
        return max(60, int(tiempo))  # Mínimo 1 minuto
    
    def procesar_llegadas(self):
        """Procesa la llegada de nuevos clientes"""
        if self.tiempo_actual < self.DURACION_SIMULACION:
            if random.random() < self.PROB_INGRESO:
                cliente = Cliente(
                    id=self.contador_clientes,
                    tiempo_ingreso=self.tiempo_actual
                )
                self.contador_clientes += 1
                self.clientes_ingresados.append(cliente)
                self.cola.append(cliente)
                self.estadisticas['clientes_ingresados'] += 1
    
    def asignar_clientes_a_boxes(self):
        """Asigna clientes de la cola a boxes disponibles"""
        for box in self.boxes:
            if not box.ocupado and self.cola:
                cliente = self.cola.popleft()
                tiempo_atencion = self.generar_tiempo_atencion()
                
                # Asignar cliente al box
                box.ocupado = True
                box.cliente_actual = cliente
                box.tiempo_fin_atencion = self.tiempo_actual + tiempo_atencion
                
                # Actualizar cliente
                cliente.tiempo_inicio_atencion = self.tiempo_actual
                cliente.box_asignado = box.id
    
    def procesar_finalizacion_atencion(self):
        """Procesa la finalización de atenciones en boxes"""
        for box in self.boxes:
            if box.ocupado and self.tiempo_actual >= box.tiempo_fin_atencion:
                cliente = box.cliente_actual
                cliente.tiempo_fin_atencion = self.tiempo_actual
                
                # Actualizar estadísticas
                self.clientes_atendidos.append(cliente)
                self.estadisticas['clientes_atendidos'] += 1
                
                tiempo_atencion = cliente.tiempo_atencion
                if tiempo_atencion:
                    self.estadisticas['tiempo_min_atencion'] = min(
                        self.estadisticas['tiempo_min_atencion'], tiempo_atencion
                    )
                    self.estadisticas['tiempo_max_atencion'] = max(
                        self.estadisticas['tiempo_max_atencion'], tiempo_atencion
                    )
                
                tiempo_espera = cliente.tiempo_espera
                if tiempo_espera is not None:
                    self.estadisticas['tiempo_min_espera'] = min(
                        self.estadisticas['tiempo_min_espera'], tiempo_espera
                    )
                    self.estadisticas['tiempo_max_espera'] = max(
                        self.estadisticas['tiempo_max_espera'], tiempo_espera
                    )
                
                # Liberar box
                box.ocupado = False
                box.cliente_actual = None
                box.tiempo_fin_atencion = None
    
    def procesar_abandonos(self):
        """Procesa clientes que abandonan por tiempo de espera"""
        clientes_a_remover = []
        
        for cliente in self.cola:
            tiempo_espera = self.tiempo_actual - cliente.tiempo_ingreso
            if tiempo_espera >= self.TIEMPO_MAX_ESPERA:
                cliente.abandono = True
                cliente.tiempo_abandono = self.tiempo_actual
                self.clientes_abandonaron.append(cliente)
                self.estadisticas['clientes_abandonaron'] += 1
                clientes_a_remover.append(cliente)
        
        # Remover clientes que abandonaron
        for cliente in clientes_a_remover:
            self.cola.remove(cliente)
    
    def calcular_costos(self):
        """Calcula el costo total de operación"""
        costo_boxes = self.num_boxes * self.COSTO_BOX
        costo_perdidas = len(self.clientes_abandonaron) * self.PERDIDA_CLIENTE
        self.estadisticas['costo_total'] = costo_boxes + costo_perdidas
    
    def simular_paso(self):
        """Ejecuta un paso de la simulación"""
        self.procesar_llegadas()
        self.asignar_clientes_a_boxes()
        self.procesar_finalizacion_atencion()
        self.procesar_abandonos()
        self.tiempo_actual += 1
    
    def condicion_finalizacion(self) -> bool:
        """Verifica si la simulación debe finalizar"""
        # Continúa si hay clientes en boxes o en cola después del cierre
        boxes_ocupados = any(box.ocupado for box in self.boxes)
        return self.tiempo_actual >= self.DURACION_SIMULACION and not self.cola and not boxes_ocupados
    
    def configurar_animacion(self):
        """Configura la visualización para la animación"""
        self.fig, self.ax = plt.subplots(figsize=(16, 10))
        self.ax.set_xlim(0, 16)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
        self.ax.set_title('Simulación Sistema de Atención al Público', fontsize=16, fontweight='bold')
        
        # Configurar boxes
        box_width = 2.0
        box_height = 1.5
        start_x = 2.0
        start_y = 7.0
        
        for i, box in enumerate(self.boxes):
            x = start_x + (i % 5) * 2.5
            y = start_y - (i // 5) * 2.0
            box.posicion_x = x
            box.posicion_y = y
            
            rect = Rectangle((x, y), box_width, box_height, 
                           linewidth=2, edgecolor='black', facecolor='lightgray')
            self.ax.add_patch(rect)
            self.rectangulos_boxes.append(rect)
            
            # Etiqueta del box
            self.ax.text(x + box_width/2, y + box_height/2, f'Box {i+1}', 
                        ha='center', va='center', fontweight='bold')
        
        # Área de cola
        self.ax.add_patch(Rectangle((1, 1), 14, 3, linewidth=2, 
                                  edgecolor='blue', facecolor='lightblue', alpha=0.3))
        self.ax.text(8, 2.5, 'ÁREA DE ESPERA', ha='center', va='center', 
                    fontsize=12, fontweight='bold', color='blue')
        
        # Panel de información
        self.texto_info = self.ax.text(0.5, 9.5, '', fontsize=10, verticalalignment='top',
                                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Configurar leyenda
        self.ax.text(14, 9, 'LEYENDA:', fontweight='bold', fontsize=10)
        self.ax.add_patch(Rectangle((14, 8.5), 0.3, 0.3, facecolor='green', alpha=0.7))
        self.ax.text(14.5, 8.65, 'Cliente siendo atendido', fontsize=9)
        self.ax.add_patch(Rectangle((14, 8), 0.3, 0.3, facecolor='orange', alpha=0.7))
        self.ax.text(14.5, 8.15, 'Cliente en cola', fontsize=9)
        self.ax.add_patch(Rectangle((14, 7.5), 0.3, 0.3, facecolor='lightgray'))
        self.ax.text(14.5, 7.65, 'Box libre', fontsize=9)
        self.ax.add_patch(Rectangle((14, 7), 0.3, 0.3, facecolor='lightgreen'))
        self.ax.text(14.5, 7.15, 'Box ocupado', fontsize=9)
        
        plt.tight_layout()
    
    def actualizar_animacion(self, frame):
        """Actualiza la animación en cada frame"""
        if not self.condicion_finalizacion():
            self.simular_paso()
        
        # Limpiar clientes anteriores
        for rect in self.rectangulos_clientes:
            rect.remove()
        self.rectangulos_clientes.clear()
        
        # Actualizar boxes
        for i, box in enumerate(self.boxes):
            color = 'lightgreen' if box.ocupado else 'lightgray'
            self.rectangulos_boxes[i].set_facecolor(color)
        
        # Dibujar clientes en boxes
        for box in self.boxes:
            if box.ocupado and box.cliente_actual:
                rect = Rectangle((box.posicion_x + 0.25, box.posicion_y + 0.25), 
                               0.5, 0.5, facecolor='green', alpha=0.8)
                self.ax.add_patch(rect)
                self.rectangulos_clientes.append(rect)
        
        # Dibujar clientes en cola
        for i, cliente in enumerate(list(self.cola)[:20]):  # Máximo 20 clientes visibles
            x = 1.5 + (i % 10) * 1.3
            y = 3.5 - (i // 10) * 0.8
            rect = Rectangle((x, y), 0.3, 0.3, facecolor='orange', alpha=0.7)
            self.ax.add_patch(rect)
            self.rectangulos_clientes.append(rect)
        
        # Actualizar información
        tiempo_actual_min = self.tiempo_actual // 60
        horas = 8 + tiempo_actual_min // 60
        minutos = tiempo_actual_min % 60
        
        info_text = f"""SIMULACIÓN SISTEMA DE ATENCIÓN
        
Tiempo: {horas:02d}:{minutos:02d}
Boxes activos: {self.num_boxes}
Clientes en cola: {len(self.cola)}
Boxes ocupados: {sum(1 for box in self.boxes if box.ocupado)}

ESTADÍSTICAS:
Ingresaron: {self.estadisticas['clientes_ingresados']}
Atendidos: {self.estadisticas['clientes_atendidos']}
Abandonaron: {self.estadisticas['clientes_abandonaron']}"""
        
        self.texto_info.set_text(info_text)
        
        return self.rectangulos_clientes + [self.texto_info]
    
    def actualizar_visualizacion(self):
        """Actualiza solo la parte visual de la animación (sin lógica de simulación)"""
        # Limpiar clientes anteriores
        for rect in self.rectangulos_clientes:
            rect.remove()
        self.rectangulos_clientes.clear()
        
        # Actualizar boxes
        for i, box in enumerate(self.boxes):
            color = 'lightgreen' if box.ocupado else 'lightgray'
            self.rectangulos_boxes[i].set_facecolor(color)
        
        # Dibujar clientes en boxes
        for box in self.boxes:
            if box.ocupado and box.cliente_actual:
                rect = Rectangle((box.posicion_x + 0.25, box.posicion_y + 0.25), 
                               0.5, 0.5, facecolor='green', alpha=0.8)
                self.ax.add_patch(rect)
                self.rectangulos_clientes.append(rect)
        
        # Dibujar clientes en cola
        for i, cliente in enumerate(list(self.cola)[:20]):  # Máximo 20 clientes visibles
            x = 1.5 + (i % 10) * 1.3
            y = 3.5 - (i // 10) * 0.8
            rect = Rectangle((x, y), 0.3, 0.3, facecolor='orange', alpha=0.7)
            self.ax.add_patch(rect)
            self.rectangulos_clientes.append(rect)
        
        # Actualizar información
        tiempo_actual_min = self.tiempo_actual // 60
        horas = 8 + tiempo_actual_min // 60
        minutos = tiempo_actual_min % 60
        
        info_text = f"""SIMULACIÓN SISTEMA DE ATENCIÓN
        
Tiempo: {horas:02d}:{minutos:02d}
Boxes activos: {self.num_boxes}
Clientes en cola: {len(self.cola)}
Boxes ocupados: {sum(1 for box in self.boxes if box.ocupado)}

ESTADÍSTICAS:
Ingresaron: {self.estadisticas['clientes_ingresados']}
Atendidos: {self.estadisticas['clientes_atendidos']}
Abandonaron: {self.estadisticas['clientes_abandonaron']}"""
        
        self.texto_info.set_text(info_text)
        
        return self.rectangulos_clientes + [self.texto_info]
    
    def ejecutar_simulacion_con_animacion(self, guardar_video=True, velocidad=50):
        """Ejecuta la simulación completa con animación"""
        print(f"Iniciando simulación con {self.num_boxes} boxes...")
        print("Configurando animación...")
        
        self.configurar_animacion()
        
        # Calcular intervalo e implementar velocidad variable
        if velocidad >= 90:
            intervalo = 1
            pasos_por_frame = max(1, velocidad // 10)  # Múltiples pasos por frame
        elif velocidad >= 70:
            intervalo = 5
            pasos_por_frame = max(1, velocidad // 20)
        elif velocidad >= 50:
            intervalo = 10
            pasos_por_frame = 1
        elif velocidad >= 30:
            intervalo = 20
            pasos_por_frame = 1
        elif velocidad >= 10:
            intervalo = 50
            pasos_por_frame = 1
        else:
            intervalo = max(100, int(1000 / max(1, velocidad)))
            pasos_por_frame = 1
        
        print(f"Velocidad: {velocidad}, Intervalo: {intervalo}ms, Pasos por frame: {pasos_por_frame}")
        
        # Estimar frames con optimización para velocidades altas
        if pasos_por_frame > 1:
            frames_estimados = (self.DURACION_SIMULACION + 3600) // pasos_por_frame
        else:
            frames_estimados = self.DURACION_SIMULACION + 3600
        
        # Crear función de actualización optimizada
        def actualizar_optimizado(frame):
            # Ejecutar múltiples pasos de simulación para velocidades altas
            for _ in range(pasos_por_frame):
                if not self.condicion_finalizacion():
                    self.simular_paso()
            
            # Actualizar visualización
            return self.actualizar_visualizacion()
        
        # Crear animación
        print("Ejecutando simulación...")
        print(f"Frames estimados: {frames_estimados}")
        
        if pasos_por_frame > 1:
            anim = animation.FuncAnimation(
                self.fig, actualizar_optimizado, 
                frames=frames_estimados, interval=intervalo, blit=False, repeat=False
            )
        else:
            anim = animation.FuncAnimation(
                self.fig, self.actualizar_animacion, 
                frames=frames_estimados, interval=intervalo, blit=False, repeat=False
            )
        
        if guardar_video:
            print("Guardando video... (esto puede tomar varios minutos)")
            fps = max(10, velocidad//2)  # FPS mínimo de 10
            writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='Simulador'), codec='libxvid', bitrate=1800)
            anim.save(f'simulacion_{self.num_boxes}_boxes.avi', writer=writer, progress_callback=self._progreso_guardado)
            print(f"Video guardado: simulacion_{self.num_boxes}_boxes.avi")
        
        plt.show()
        
        # Finalizar cálculos
        self.calcular_costos()
        return anim
    
    def _progreso_guardado(self, current_frame, total_frames):
        """Callback para mostrar progreso del guardado del video"""
        if current_frame % 1000 == 0:  # Mostrar cada 1000 frames
            porcentaje = (current_frame / total_frames) * 100
            print(f"Guardando video: {porcentaje:.1f}% ({current_frame}/{total_frames} frames)")
    
    def ejecutar_simulacion_rapida(self):
        """Ejecuta la simulación sin visualización para obtener resultados rápidos"""
        print(f"Ejecutando simulación rápida con {self.num_boxes} boxes...")
        
        while not self.condicion_finalizacion():
            self.simular_paso()
        
        self.calcular_costos()
        print("Simulación completada.")
    
    def imprimir_resultados(self):
        """Imprime los resultados finales de la simulación"""
        print("\n" + "="*60)
        print("RESULTADOS DE LA SIMULACIÓN")
        print("="*60)
        print(f"Número de boxes utilizados: {self.num_boxes}")
        print(f"Duración de simulación: 4 horas (08:00 - 12:00)")
        print()
        print("ESTADÍSTICAS DE CLIENTES:")
        print(f"1) Clientes que ingresaron: {self.estadisticas['clientes_ingresados']}")
        print(f"2) Clientes atendidos: {self.estadisticas['clientes_atendidos']}")
        print(f"3) Clientes no atendidos (abandonaron): {self.estadisticas['clientes_abandonaron']}")
        print()
        print("TIEMPOS DE ATENCIÓN:")
        if self.estadisticas['tiempo_min_atencion'] != float('inf'):
            print(f"4) Tiempo mínimo de atención: {self.estadisticas['tiempo_min_atencion']//60:.0f} min {self.estadisticas['tiempo_min_atencion']%60:.0f} seg")
            print(f"5) Tiempo máximo de atención: {self.estadisticas['tiempo_max_atencion']//60:.0f} min {self.estadisticas['tiempo_max_atencion']%60:.0f} seg")
        else:
            print("4) Tiempo mínimo de atención: N/A")
            print("5) Tiempo máximo de atención: N/A")
        print()
        print("TIEMPOS DE ESPERA:")
        if self.estadisticas['tiempo_min_espera'] != float('inf'):
            print(f"6) Tiempo mínimo de espera: {self.estadisticas['tiempo_min_espera']//60:.0f} min {self.estadisticas['tiempo_min_espera']%60:.0f} seg")
            print(f"7) Tiempo máximo de espera: {self.estadisticas['tiempo_max_espera']//60:.0f} min {self.estadisticas['tiempo_max_espera']%60:.0f} seg")
        else:
            print("6) Tiempo mínimo de espera: N/A")
            print("7) Tiempo máximo de espera: N/A")
        print()
        print("COSTOS DE OPERACIÓN:")
        print(f"Costo de boxes: ${self.num_boxes * self.COSTO_BOX:,}")
        print(f"Costo por clientes perdidos: ${len(self.clientes_abandonaron) * self.PERDIDA_CLIENTE:,}")
        print(f"8) Costo total de operación: ${self.estadisticas['costo_total']:,}")
        print("="*60)
    
    def generar_reporte_detallado(self, filename=None):
        """Genera un reporte detallado en archivo de texto"""
        if filename is None:
            filename = f"reporte_simulacion_{self.num_boxes}_boxes.txt"
        
        with open(filename, 'w') as f:
            f.write("REPORTE DETALLADO DE SIMULACIÓN\n")
            f.write("="*50 + "\n\n")
            f.write(f"Configuración:\n")
            f.write(f"- Número de boxes: {self.num_boxes}\n")
            f.write(f"- Duración: 4 horas (08:00 - 12:00)\n")
            f.write(f"- Probabilidad de llegada: {self.PROB_INGRESO}\n")
            f.write(f"- Tiempo máximo de espera: {self.TIEMPO_MAX_ESPERA//60} minutos\n\n")
            
            f.write("Resultados:\n")
            f.write("-"*20 + "\n")
            f.write(f"Clientes ingresados: {self.estadisticas['clientes_ingresados']}\n")
            f.write(f"Clientes atendidos: {self.estadisticas['clientes_atendidos']}\n")
            f.write(f"Clientes abandonaron: {self.estadisticas['clientes_abandonaron']}\n")
            f.write(f"Costo total: ${self.estadisticas['costo_total']:,}\n\n")
            
            f.write("Tiempos de atención:\n")
            f.write("-"*20 + "\n")
            if self.estadisticas['tiempo_min_atencion'] != float('inf'):
                f.write(f"Tiempo mínimo de atención: {self.estadisticas['tiempo_min_atencion']//60:.0f} min {self.estadisticas['tiempo_min_atencion']%60:.0f} seg\n")
                f.write(f"Tiempo máximo de atención: {self.estadisticas['tiempo_max_atencion']//60:.0f} min {self.estadisticas['tiempo_max_atencion']%60:.0f} seg\n")
            else:
                f.write("Tiempo mínimo de atención: N/A\n")
                f.write("Tiempo máximo de atención: N/A\n")
            
            f.write("\nTiempos de espera:\n")
            f.write("-"*20 + "\n")
            if self.estadisticas['tiempo_min_espera'] != float('inf'):
                f.write(f"Tiempo mínimo de espera: {self.estadisticas['tiempo_min_espera']//60:.0f} min {self.estadisticas['tiempo_min_espera']%60:.0f} seg\n")
                f.write(f"Tiempo máximo de espera: {self.estadisticas['tiempo_max_espera']//60:.0f} min {self.estadisticas['tiempo_max_espera']%60:.0f} seg\n")
            else:
                f.write("Tiempo mínimo de espera: N/A\n")
                f.write("Tiempo máximo de espera: N/A\n")
            
            f.write("\nEficiencia del sistema:\n")
            f.write("-"*20 + "\n")
            if self.estadisticas['clientes_ingresados'] > 0:
                tasa_atencion = (self.estadisticas['clientes_atendidos'] / 
                               self.estadisticas['clientes_ingresados']) * 100
                tasa_abandono = (self.estadisticas['clientes_abandonaron'] / 
                               self.estadisticas['clientes_ingresados']) * 100
                f.write(f"Tasa de atención: {tasa_atencion:.1f}%\n")
                f.write(f"Tasa de abandono: {tasa_abandono:.1f}%\n")
        
        print(f"Reporte guardado en: {filename}")

