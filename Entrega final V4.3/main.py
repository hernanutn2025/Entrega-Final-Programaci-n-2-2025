from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from ventanaPrincipal import VentanaPrincipal
import sys
import os

def main():
    try:
        print("🚀 Iniciando aplicación en MODO DESARROLLO (sin login)...")
        
        app = QApplication(sys.argv)
        
        # Verificar ícono
        icon_path = "imagenes/icono.png"
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
            print("✅ Ícono cargado")
        else:
            print(f"⚠️  Ícono no encontrado en: {icon_path}")
        
        # Saltar directamente a la ventana principal
        print("✅ Saltando login...")
        ventana_principal = VentanaPrincipal()
        ventana_principal.show()
        
        print("✅ VentanaPrincipal mostrada - Listo para trabajar!")
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Presiona Enter para salir...")

if __name__ == "__main__":
    main()