import os

def listar_estructura(directorio, prefijo=""):
    for item in os.listdir(directorio):
        ruta = os.path.join(directorio, item)
        print(prefijo + "├── " + item)
        if os.path.isdir(ruta):
            listar_estructura(ruta, prefijo + "│   ")

print("📁 Estructura del Proyecto:")
listar_estructura(".")
