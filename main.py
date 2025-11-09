from PyQt5.QtGui import QIcon,QFont,QFontDatabase
from PyQt5.QtWidgets import QApplication
from ventanaLogin import VentanaLogin
import sys
import os
def cargar_fuentes():
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    poppins_path = os.path.join(script_dir, "fonts", "Poppins-Regular.ttf")
    poppins_bold_path = os.path.join(script_dir, "fonts", "Poppins-Bold.ttf")
    
    roboto_path = os.path.join(script_dir, "fonts", "Roboto-Regular.ttf")
    roboto_bold_path = os.path.join(script_dir, "fonts", "Roboto-Bold.ttf")
    
    font_ids = {}
    
    if os.path.exists(poppins_path):
        font_ids['poppins'] = QFontDatabase.addApplicationFont(poppins_path)
    if os.path.exists(poppins_bold_path):
        font_ids['poppins_bold'] = QFontDatabase.addApplicationFont(poppins_bold_path)
    if os.path.exists(roboto_path):
        font_ids['roboto'] = QFontDatabase.addApplicationFont(roboto_path)
    if os.path.exists(roboto_bold_path):
        font_ids['roboto_bold'] = QFontDatabase.addApplicationFont(roboto_bold_path)
    
    return font_ids

def configurar_fuente_aplicacion():
    font_families = QFontDatabase().families()
    
    roboto_families = [f for f in font_families if 'Roboto' in f]
    if roboto_families:
        default_font = QFont(roboto_families[0], 10)
        QApplication.setFont(default_font)
    else:
        default_font = QFont("Arial", 10)
        QApplication.setFont(default_font)

def cargar_icono_aplicacion():
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    icon_path = os.path.join(script_dir, "imagenes", "icono.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        QApplication.setWindowIcon(app_icon)
        print(f"Ícono de aplicación cargado: {icon_path}")
    else:
        print(f"Advertencia: No se encontró el ícono en {icon_path}")

def main():
    app = QApplication(sys.argv)
    cargar_icono_aplicacion()
    cargar_fuentes()
    configurar_fuente_aplicacion()
    login = VentanaLogin()
    login.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()