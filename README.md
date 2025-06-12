# TP 6: Simulador de Sistema de Atención al Público

## Descripción
Simulador de un sistema de atención al público que modela el funcionamiento de boxes de atención (cajas de supermercado, bancos, etc.) con visualización gráfica animada.

## Características
- Simulación de 1 a 10 boxes de atención
- Modelado realista de llegadas de clientes (probabilidad 1/144 por segundo)
- Tiempos de atención con distribución normal (media=10min, desvío=5min)
- Abandono de clientes después de 30 minutos de espera
- Cálculo de costos de operación
- Animación gráfica en tiempo real
- Generación de videos AVI
- Reportes detallados

## Requisitos
- Python 3.7+
- NumPy
- Matplotlib
- FFmpeg (para generación de videos)

## Instalación
```bash
pip install -r requirements.txt
```

Para videos, también necesitas FFmpeg:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Descargar desde https://ffmpeg.org/
```

## Uso
```bash
python main.py
```

El programa te pedirá:
1. Número de boxes (1-10)
2. Tipo de simulación:
   - Con animación y video
   - Solo resultados (rápida)
   - Solo animación (sin video)
3. Velocidad de animación (1-100, donde 100 es más rápido)

## Resultados
El simulador responde a las 9 preguntas del TP:
1. Clientes que ingresaron
2. Clientes atendidos
3. Clientes no atendidos (abandonaron)
4. Tiempo mínimo de atención
5. Tiempo máximo de atención
6. Tiempo mínimo de espera
7. Tiempo máximo de espera
8. Costo total de operación
9. Video animado (archivo AVI)

## Control de Velocidad
La velocidad de animación se controla con un parámetro de 1-100:
- **1-20**: Animación muy lenta, ideal para análisis detallado
- **30-50**: Velocidad moderada, recomendada para visualización
- **60-80**: Animación rápida
- **90-100**: Animación muy rápida, múltiples pasos por frame

## Archivos Generados
- `simulacion_N_boxes.avi` - Video de la animación
- `reporte_simulacion_N_boxes.txt` - Reporte detallado

## Parámetros del Modelo
- Horario: 8:00 AM - 12:00 PM (4 horas)
- Probabilidad de llegada: 1/144 por segundo
- Tiempo máximo de espera: 30 minutos
- Distribución de atención: Normal(10min, 5min)
- Costo por box: $1,000
- Pérdida por cliente: $10,000

## Estructura del Código
- `main.py`: Función principal y interfaz de usuario
- `simulacion_boxes.py`: Contiene todas las clases y lógica del simulador
  - `Cliente`: Clase para modelar clientes
  - `Box`: Clase para modelar boxes de atención
  - `SimuladorAtencionPublico`: Clase principal del simulador
- Métodos de simulación paso a paso
- Sistema de animación con matplotlib
- Generación de reportes y estadísticas
