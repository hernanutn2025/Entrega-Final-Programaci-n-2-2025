import ventanaPrincipal
import basededatos
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap,QIcon
from PyQt5.QtCore import Qt
import os
import sys

class VentanaRegistro(QWidget):
    def __init__(self, conexion, parent_login=None):
        super().__init__()
        self.setWindowTitle("NBA FIBA - Registro")
        self.resize(1600, 900)
        self.cargar_icono_ventana("imagenes/icono.png")
        self.conexion = conexion
        self.parent_login = parent_login
        
        self.constructor_registro()
        self.configurar_fuentes()

    def cargar_icono_ventana(self, ruta_icono):
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        absolute_path = os.path.join(script_dir, ruta_icono)
        
        if os.path.exists(absolute_path):
            icono = QIcon(absolute_path)
            self.setWindowIcon(icono)
            print(f"Ícono de ventana cargado: {absolute_path}")
            return icono
        else:
            print(f"Advertencia: No se encontró el ícono en {absolute_path}")
            return QIcon()
        
    def configurar_fuentes(self):
        self.fuente_titulo = self.obtener_fuente("Poppins", 12, True)
        self.fuente_datos = self.obtener_fuente("Roboto", 10, False)
        
        self.etiqueta_usuario.setFont(self.fuente_titulo)
        self.etiqueta_contraseña.setFont(self.fuente_titulo)
        self.etiqueta_email.setFont(self.fuente_titulo)
        
        self.datos_usuario.setFont(self.fuente_datos)
        self.datos_contraseña.setFont(self.fuente_datos)
        self.datos_email.setFont(self.fuente_datos)
        self.boton_registrar.setFont(self.fuente_datos)

    def obtener_fuente(self, familia, tamaño, negrita=False):
        font = QFont(familia, tamaño)
        font.setBold(negrita)
        
        font_families = QFontDatabase().families()
        if familia in font_families:
            return font
        else:
            return QFont("Arial", tamaño, QFont.Bold if negrita else QFont.Normal)

    def constructor_registro(self):
        layout_principal = QVBoxLayout()
        
        # Header con título e íconos - MÁS GRANDE Y LLAMATIVO
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(30)  # Más espacio entre elementos
        
        # Cargar y mostrar ícono izquierdo - MÁS GRANDE
        icono_izquierdo = QLabel()
        pixmap = self.cargar_icono("imagenes/icono.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Aumentado a 150x150
            icono_izquierdo.setPixmap(pixmap)
        icono_izquierdo.setAlignment(Qt.AlignCenter)
        icono_izquierdo.setStyleSheet("padding: 10px;")
        header_layout.addWidget(icono_izquierdo)
        
        # Título - MÁS GRANDE Y COLOR MÁS RESALTANTE
        titulo = QLabel("Planilla FIBA")
        titulo.setFont(QFont("Arial", 36, QFont.Bold))  # Aumentado a 36
        titulo.setStyleSheet("""
            color: #FF6B35;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF6B35, stop:0.5 #FF8E53, stop:1 #FF6B35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 30px;
            padding: 15px;
            border: 3px solid #FF8E53;
            border-radius: 15px;
            background-color: rgba(255, 255, 255, 0.9);
        """)
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        # Cargar y mostrar ícono derecho - MÁS GRANDE
        icono_derecho = QLabel()
        icono_derecho.setPixmap(pixmap)  # Mismo ícono
        icono_derecho.setAlignment(Qt.AlignCenter)
        icono_derecho.setStyleSheet("padding: 10px;")
        header_layout.addWidget(icono_derecho)
        
        layout_principal.addLayout(header_layout)
        
        # Formulario de registro
        formulario_layout = QVBoxLayout()
        formulario_layout.setAlignment(Qt.AlignCenter)
        formulario_layout.setSpacing(20)
        
        # Widget contenedor del formulario
        formulario_widget = QWidget()
        formulario_widget.setMaximumWidth(500)  # Un poco más ancho
        formulario_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 40px;
                border: 2px solid #FF6B35;
            }
        """)
        
        formulario_interno = QVBoxLayout(formulario_widget)
        formulario_interno.setSpacing(20)
        
        self.etiqueta_usuario = QLabel("Usuario")
        self.etiqueta_usuario.setStyleSheet("color: #2a2a2a; font-weight: bold; font-size: 14px;")
        self.datos_usuario = QLineEdit()
        self.datos_usuario.setPlaceholderText("Nuevo usuario..")
        self.datos_usuario.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B35;
                background-color: #FFF5F0;
            }
        """)
        
        self.etiqueta_contraseña = QLabel("Contraseña")
        self.etiqueta_contraseña.setStyleSheet("color: #2a2a2a; font-weight: bold; font-size: 14px;")
        self.datos_contraseña = QLineEdit()
        self.datos_contraseña.setEchoMode(QLineEdit.Password)
        self.datos_contraseña.setPlaceholderText("Nueva contraseña..")
        self.datos_contraseña.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B35;
                background-color: #FFF5F0;
            }
        """)

        self.etiqueta_email = QLabel("Email")
        self.etiqueta_email.setStyleSheet("color: #2a2a2a; font-weight: bold; font-size: 14px;")
        self.datos_email = QLineEdit()
        self.datos_email.setPlaceholderText("email@ejemplo.com..")
        self.datos_email.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B35;
                background-color: #FFF5F0;
            }
        """)

        self.boton_registrar = QPushButton("Confirmar Registro")
        self.boton_registrar.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #E55A2B;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #CC4A24;
            }
        """)
        self.boton_registrar.clicked.connect(self.intentar_registrar)

        formulario_interno.addWidget(self.etiqueta_usuario)
        formulario_interno.addWidget(self.datos_usuario)
        formulario_interno.addWidget(self.etiqueta_contraseña)
        formulario_interno.addWidget(self.datos_contraseña)
        formulario_interno.addWidget(self.etiqueta_email)
        formulario_interno.addWidget(self.datos_email)
        formulario_interno.addWidget(self.boton_registrar)
        
        formulario_layout.addWidget(formulario_widget)
        layout_principal.addLayout(formulario_layout)
        
        # Fondo con imagen más llamativa
        self.setStyleSheet("""
            VentanaRegistro {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
            }
        """)

        self.setLayout(layout_principal)
    
    def cargar_icono(self, ruta_icono):
        """Método para cargar íconos con manejo de errores"""
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        absolute_path = os.path.join(script_dir, ruta_icono)
        
        if os.path.exists(absolute_path):
            return QPixmap(absolute_path)
        else:
            # Crear un ícono simple como fallback
            pixmap = QPixmap(150, 150)
            pixmap.fill(Qt.red)
            return pixmap
    
    def intentar_registrar(self):
        usuario = self.datos_usuario.text()
        contraseña = self.datos_contraseña.text()
        email = self.datos_email.text()
        
        if not usuario or not contraseña or not email:
            QMessageBox.warning(self,"Atención","Por favor, completar todos los campos para completar el registro.")
            return 
        if self.conexion and self.conexion.is_connected():
            if basededatos.registrar_usuario(self.conexion,usuario,contraseña,email):
                QMessageBox.information(self,"Registrado con éxito","Usuario "+usuario+" registrado! Ya puedes iniciar sesión.")
                self.close()
        else:
            QMessageBox.critical(self,"Error de conexión","Conexión a la base de datos perdida..")
    
    def closeEvent(self,event):
        if self.parent_login:
            self.parent_login.show()
        event.accept()

class VentanaLogin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NBA FIBA - Login")
        self.resize(1600, 900)
        self.cargar_icono_ventana("imagenes/icono.png")
        self.ventana_registro = None 
        
        self.conexion = basededatos.conectar_base()
        if not self.conexion:
            QMessageBox.critical(self,"Error","No se pudo conectar a la base de datos NBA")
            QApplication.instance().quit()
            return
        
        self.constructor_login()
        self.configurar_fuentes()

    def cargar_icono_ventana(self, ruta_icono):
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        absolute_path = os.path.join(script_dir, ruta_icono)
        
        if os.path.exists(absolute_path):
            icono = QIcon(absolute_path)
            self.setWindowIcon(icono)
            print(f"Ícono de ventana cargado: {absolute_path}")
            return icono
        else:
            print(f"Advertencia: No se encontró el ícono en {absolute_path}")
            return QIcon()
        
    def configurar_fuentes(self):
        self.fuente_titulo = self.obtener_fuente("Poppins", 12, True)
        self.fuente_datos = self.obtener_fuente("Roboto", 10, False)
        
        self.etiqueta_usuario.setFont(self.fuente_titulo)
        self.etiqueta_contraseña.setFont(self.fuente_titulo)
        
        self.datos_usuario.setFont(self.fuente_datos)
        self.datos_contraseña.setFont(self.fuente_datos)
        self.boton_login.setFont(self.fuente_datos)
        self.boton_registro.setFont(self.fuente_datos)

    def obtener_fuente(self, familia, tamaño, negrita=False):
        font = QFont(familia, tamaño)
        font.setBold(negrita)
        
        font_families = QFontDatabase().families()
        if familia in font_families:
            return font
        else:
            return QFont("Arial", tamaño, QFont.Bold if negrita else QFont.Normal)

    def constructor_login(self):
        layout_principal = QVBoxLayout()
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        header_layout.setSpacing(30)  
        icono_izquierdo = QLabel()
        pixmap = self.cargar_icono("imagenes/icono.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icono_izquierdo.setPixmap(pixmap)
        icono_izquierdo.setAlignment(Qt.AlignCenter)
        icono_izquierdo.setStyleSheet("padding: 10px;")
        header_layout.addWidget(icono_izquierdo)
        
        titulo = QLabel("Planilla FIBA")
        titulo.setFont(QFont("Arial", 36, QFont.Bold))  # Aumentado a 36
        titulo.setStyleSheet("""
            color: #FF6B35;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF6B35, stop:0.5 #FF8E53, stop:1 #FF6B35);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 30px;
            padding: 15px;
            border: 3px solid #FF8E53;
            border-radius: 15px;
            background-color: rgba(255, 255, 255, 0.9);
        """)
        titulo.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(titulo)
        
        icono_derecho = QLabel()
        icono_derecho.setPixmap(pixmap) 
        icono_derecho.setAlignment(Qt.AlignCenter)
        icono_derecho.setStyleSheet("padding: 10px;")
        header_layout.addWidget(icono_derecho)
        
        layout_principal.addLayout(header_layout)
        
        formulario_layout = QVBoxLayout()
        formulario_layout.setAlignment(Qt.AlignCenter)
        formulario_layout.setSpacing(20)
        
        formulario_widget = QWidget()
        formulario_widget.setMaximumWidth(500)
        formulario_widget.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                padding: 40px;
                border: 2px solid #FF6B35;
            }
        """)
        
        formulario_interno = QVBoxLayout(formulario_widget)
        formulario_interno.setSpacing(20)

        self.etiqueta_usuario = QLabel("Usuario")
        self.etiqueta_usuario.setStyleSheet("color: #2a2a2a; font-weight: bold; font-size: 14px;")
        self.datos_usuario = QLineEdit()
        self.datos_usuario.setPlaceholderText("Ingresar usuario..")
        self.datos_usuario.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B35;
                background-color: #FFF5F0;
            }
        """)

        self.etiqueta_contraseña = QLabel("Contraseña")
        self.etiqueta_contraseña.setStyleSheet("color: #2a2a2a; font-weight: bold; font-size: 14px;")
        self.datos_contraseña = QLineEdit()
        self.datos_contraseña.setEchoMode(QLineEdit.Password)
        self.datos_contraseña.setPlaceholderText("Ingresar contraseña..")
        self.datos_contraseña.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B35;
                background-color: #FFF5F0;
            }
        """)

        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(15)
        
        self.boton_login = QPushButton("Iniciar Sesión")
        self.boton_login.setStyleSheet("""
            QPushButton {
                background-color: #FF6B35;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #E55A2B;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #CC4A24;
            }
        """)
        self.boton_login.clicked.connect(self.intentar_logear)
        
        self.boton_registro = QPushButton("Registrarse")
        self.boton_registro.setStyleSheet("""
            QPushButton {
                background-color: #6A6A6A;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #5A5A5A;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #4A4A4A;
            }
        """)
        self.boton_registro.clicked.connect(self.abrir_registro)

        botones_layout.addWidget(self.boton_login)
        botones_layout.addWidget(self.boton_registro)

        formulario_interno.addWidget(self.etiqueta_usuario)
        formulario_interno.addWidget(self.datos_usuario)
        formulario_interno.addWidget(self.etiqueta_contraseña)
        formulario_interno.addWidget(self.datos_contraseña)
        formulario_interno.addLayout(botones_layout)
        
        formulario_layout.addWidget(formulario_widget)
        layout_principal.addLayout(formulario_layout)
        
        self.setStyleSheet("""
            VentanaLogin {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.5 #16213e, stop:1 #0f3460);
            }
        """)

        self.setLayout(layout_principal)

    def cargar_icono(self, ruta_icono):
        """Método para cargar íconos con manejo de errores"""
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        absolute_path = os.path.join(script_dir, ruta_icono)
        
        if os.path.exists(absolute_path):
            return QPixmap(absolute_path)
        else:
            pixmap = QPixmap(150, 150)
            pixmap.fill(Qt.red)
            return pixmap

    def intentar_logear(self):
        usuario = self.datos_usuario.text()
        contraseña = self.datos_contraseña.text()

        if not usuario or not contraseña:
            QMessageBox.warning(self,"¡Advertencia!","Por favor, complete los campos para ingresar.")
            return
        if self.conexion and self.conexion.is_connected():
            if basededatos.autenticar_usuario(self.conexion,usuario,contraseña):
                QMessageBox.information(self,f"Ingreso exitoso","Bienvenido "+usuario+"!")
                self.ventana_principal()
            else:
                QMessageBox.critical(self,"Error al ingresar","Usuario o contraseña incorrectos.")
        else:
            QMessageBox.critical(self,"Error de Conexión", "Conexión a la base de datos perdida..")      
    
    def abrir_registro(self):
        self.hide()
        self.ventana_registro = VentanaRegistro(self.conexion,self)
        self.ventana_registro.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.intentar_logear()
        else:
            super().keyPressEvent(event)
    
    def ventana_principal(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            self.close()

            self.ventana = ventanaPrincipal.VentanaPrincipal()
            self.ventana.show()