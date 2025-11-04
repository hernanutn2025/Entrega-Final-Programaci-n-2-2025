import ventanaPrincipal
import basededatos
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,QHBoxLayout,QLabel,QLineEdit,QPushButton,QMessageBox)
from PyQt5.QtCore import Qt

class VentanaRegistro(QWidget):
    def __init__(self,conexion,parent_login=None):
        super().__init__()
        self.setWindowTitle("NBA FIBA - Registro")
        self.resize(350,250)
        self.conexion = conexion
        self.parent_login = parent_login
        self.constructor_registro()

    def constructor_registro(self):
        layout = QVBoxLayout()
        self.etiqueta_usuario=QLabel("Usuario")
        self.datos_usuario=QLineEdit()
        self.datos_usuario.setPlaceholderText("Nuevo usuario..")
        
        self.etiqueta_contraseña=QLabel("Contraseña")
        self.datos_contraseña=QLineEdit()
        self.datos_contraseña.setEchoMode(QLineEdit.Password)
        self.datos_contraseña.setPlaceholderText("Nueva contraseña..")

        self.etiqueta_email = QLabel("Email")
        self.datos_email=QLineEdit()
        self.datos_email.setPlaceholderText("email@ejemplo.com..")

        self.boton_registrar = QPushButton("Confirmar Registro")
        self.boton_registrar.clicked.connect(self.intentar_registrar)

        layout.addWidget(self.etiqueta_usuario)
        layout.addWidget(self.datos_usuario)
        layout.addWidget(self.etiqueta_contraseña)
        layout.addWidget(self.datos_contraseña)
        layout.addWidget(self.etiqueta_email)
        layout.addWidget(self.datos_email)
        layout.addWidget(self.boton_registrar)

        self.setLayout(layout)
    
    def intentar_registrar(self):
        usuario = self.datos_usuario.text()
        contraseña = self.datos_contraseña.text()
        email = self.datos_email.text()
        
        if not usuario or not contraseña or not email:
            QMessageBox.warning(self,"Atención","Por favor, completar todos los campos para completar el registro.")
            return 
        if self.conexion and self.conexion.is_connected():
            if basededatos.registrar_usuario(self.conexion,usuario,contraseña,email):
                QMessageBox.information(self,"Registrado con éxito","Usuario "+usuario+"registrado! Ya puedes iniciar sesión.")
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
        self.resize(400,180)
        self.ventana_registro = None 

        self.conexion = basededatos.conectar_base()
        if not self.conexion:
            QMessageBox.critical(self,"Error","No se pudo conectar a la base de datos NBA")
            QApplication.instance().quit()
            return
        
        self.constructor_login()


    def constructor_login(self):
        login_layout = QVBoxLayout()
        botones_layout = QHBoxLayout()

        self.etiqueta_usuario=QLabel("Usuario")
        self.datos_usuario=QLineEdit()
        self.datos_usuario.setPlaceholderText("Ingresar usuario..")

        self.etiqueta_contraseña=QLabel("Contraseña")
        self.datos_contraseña=QLineEdit()
        self.datos_contraseña.setEchoMode(QLineEdit.Password)
        self.datos_contraseña.setPlaceholderText("Ingresar contraseña..")

        self.boton_login=QPushButton("Iniciar Sesión")
        self.boton_login.clicked.connect(self.intentar_logear)
        self.boton_registro=QPushButton("Registrarse")
        self.boton_registro.clicked.connect(self.abrir_registro)

        login_layout.addWidget(self.etiqueta_usuario)
        login_layout.addWidget(self.datos_usuario)
        login_layout.addWidget(self.etiqueta_contraseña)
        login_layout.addWidget(self.datos_contraseña)
        
        botones_layout.addWidget(self.boton_login)
        botones_layout.addWidget(self.boton_registro)
        
        login_layout.addLayout(botones_layout)
        self.setLayout(login_layout)

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

    def ventana_principal(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
            self.close()
            ventana = ventanaPrincipal.VentanaPrincipal()
            ventana.show()

     
            