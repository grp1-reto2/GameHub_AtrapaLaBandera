from game_module import GameModule 

def main():
    print("--- MENU DE INICIO ---")
    name = input("Nombre de usuario: ")
    print("1. Unirse a partida (Cliente)")
    print("2. Crear partida (Host/Servidor + Cliente)")
    
    try:
        resp = int(input("Selecciona (1/2): "))
    except ValueError:
        print("Por favor escribe un número.")
        return


    manager = GameModule(name)
    
    if resp == 2:
        print("Iniciando como HOST...")
        try:
            manager.start_as_host()
        except Exception as e:
            print(f"Error iniciando Host: {e}")
            import traceback; traceback.print_exc()
    else:
        ip = input("IP del servidor:")
        if not ip: ip = "127.0.0.1"
        
        print(f"Conectando a {ip}...")
        try: 
            manager.start_as_client(ip)
        except Exception as e:
            print(f"Error iniciando Cliente: {e}")
            import traceback; traceback.print_exc()

if __name__ == "__main__":
    main()