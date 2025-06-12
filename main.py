from simulacion_boxes import SimuladorAtencionPublico

def main():
    """Función principal del programa"""
    print("="*60)
    print("SIMULADOR DE SISTEMA DE ATENCIÓN AL PÚBLICO")
    print("="*60)
    print()
    
    while True:
        try:
            num_boxes = int(input("Ingrese número de boxes (1-10): "))
            if 1 <= num_boxes <= 10:
                break
            else:
                print("Error: El número debe estar entre 1 y 10")
        except ValueError:
            print("Error: Ingrese un número válido")
    
    print("\nOpciones de simulación:")
    print("1. Simulación con animación y video")
    print("2. Simulación rápida (solo resultados)")
    print("3. Simulación con animación (sin video)")
    
    while True:
        try:
            opcion = int(input("Seleccione una opción (1-3): "))
            if 1 <= opcion <= 3:
                break
            else:
                print("Error: Seleccione una opción válida (1-3)")
        except ValueError:
            print("Error: Ingrese un número válido")
    
    # Crear simulador
    simulador = SimuladorAtencionPublico(num_boxes)
    
    if opcion == 1:
        # Simulación con animación y video
        velocidad = int(input("Velocidad de animación (1-100, recomendado 60): ") or "60")
        simulador.ejecutar_simulacion_con_animacion(guardar_video=True, velocidad=velocidad)
    elif opcion == 2:
        # Simulación rápida
        simulador.ejecutar_simulacion_rapida()
    else:
        # Simulación con animación sin video
        velocidad = int(input("Velocidad de animación (1-100, recomendado 50): ") or "50")
        simulador.ejecutar_simulacion_con_animacion(guardar_video=False, velocidad=velocidad)
    
    # Mostrar resultados
    simulador.imprimir_resultados()
    
    # Preguntar si quiere generar reporte
    if input("\n¿Generar reporte detallado? (s/n): ").lower() == 's':
        simulador.generar_reporte_detallado()
    
    print("\nSimulación finalizada. ¡Gracias por usar el simulador!")

if __name__ == "__main__":
    main()