import sys
import os
from nba_extractor import NBADataExtractor
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QAction, QDesktopWidget, QTableWidget, QLineEdit,
    QCheckBox, QGroupBox, QTabWidget, QTextEdit, QComboBox, QMessageBox
    ,QInputDialog,QTableWidgetItem,QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter,QFont,QFontDatabase


class BackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        
        # Construir la ruta absoluta
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        absolute_path = os.path.join(script_dir, image_path)
        
        self.background_image = QPixmap(absolute_path)
        
        # Verificar si la imagen se cargó
        if self.background_image.isNull():
             print(f"Error: No se pudo cargar la imagen de fondo en {absolute_path}")
        
        self.setAutoFillBackground(True) 

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if self.background_image.isNull():
            return
            
        painter = QPainter(self)
        
        # Escalar la imagen al tamaño actual del widget, manteniendo aspecto y expandiendo
        scaled_pixmap = self.background_image.scaled(
            self.size(),
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation
        )
        
        # Calcular la posición (x, y) para centrar la imagen
        x = int((self.width() - scaled_pixmap.width()) / 2)
        y = int((self.height() - scaled_pixmap.height()) / 2)
        
        # Dibujar la imagen
        painter.drawPixmap(x, y, scaled_pixmap)
        painter.end()


class LogoLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(150, 150)  # Tamaño más grande para el lado derecho
        self.setStyleSheet("background-color: transparent; border: none;")
        
    def set_logo(self, logo_path):
        """Cargar y mostrar el logo del equipo"""
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Escalar manteniendo la relación de aspecto
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.setPixmap(scaled_pixmap)
            else:
                self.set_logo_placeholder()
        else:
            self.set_logo_placeholder()
    
    def set_logo_placeholder(self):
        self.setText("🏀")
        self.setStyleSheet("font-size: 60px; background-color: rgba(255,255,255,150); border-radius: 10px;")


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(self.cargar_icono("imagenes/icono.png"))
        self.setWindowTitle("Planilla NBA-FIBA")
        self.resize(1600, 900)
        self.centrar_ventana()
        self.setWindowIcon(self.cargar_icono("imagenes/icono.png"))
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2a2a2a;
                color: white;
            }
            QMainWindow::title {
                background-color: #000000;
                color: #ff0000;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        
        self.extractor = NBADataExtractor()
        
        self.puntos_local = [0, 0, 0, 0, 0] 
        self.puntos_visitante = [0, 0, 0, 0, 0]
        self.marcador_local = 0
        self.marcador_visitante = 0
        
        self.cuarto_actual = 0  
        
        self.faltas_local = 0
        self.faltas_visitante = 0

        self.minutos = 10
        self.segundos = 0
        self.timer_corriendo = False
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.actualizar_cronometro)

        self.configurar_fuentes()
        barra_menu = self.menuBar()
        barra_menu.setStyleSheet("""
            QMenuBar {
                background-color: #000000;
                color: #ff0000;
                border: 1px solid #333333;
                font-weight: bold;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                color: #ff0000;
            }
            QMenuBar::item:selected {
                background-color: #333333;
                color: #ff0000;
            }
            QMenuBar::item:pressed {
                background-color: #555555;
                color: #ff0000;
            }
            QMenu {
                background-color: #000000;
                color: #ff0000;
                border: 1px solid #333333;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #ff0000;
            }
            QMenu::item:selected {
                background-color: #333333;
                color: #ff0000;
            }
        """)
        menu_archivo = barra_menu.addMenu("Archivo")
        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.pestaña_principal = self.crear_pestaña_principal()
        self.tab_widget.addTab(self.pestaña_principal, "Planilla y Tablero")

        self.pestaña_estadisticas = self.crear_pantalla_estadisticas()
        self.tab_widget.addTab(self.pestaña_estadisticas, "Resumen de Juego")

        self.pestaña_historial = self.crear_pestaña_historial()
        self.tab_widget.addTab(self.pestaña_historial, "Historial de Partidos")

        self.estadisticas_local = {}  
        self.estadisticas_visitante = {}
        
        self.cargar_equipos()
        self.nombre_local_cb.currentTextChanged.connect(self.actualizar_estadisticas)
        self.nombre_visitante_cb.currentTextChanged.connect(self.actualizar_estadisticas)
#----------------------------------------------Fuentes y Aspectos
    def configurar_fuentes(self):
        self.fuente_titulo = self.obtener_fuente("Poppins", 16, True)  
        self.fuente_datos = self.obtener_fuente("Roboto", 10, False)   
        self.fuente_datos_bold = self.obtener_fuente("Roboto", 10, True)
    
    def obtener_fuente(self, familia, tamaño, negrita=False):
        font = QFont(familia, tamaño)
        font.setBold(negrita)
        
        # Verificar si la fuente existe en el sistema
        font_families = QFontDatabase().families()
        if familia in font_families:
            return font
        else:
            # Fallback a fuentes del sistema
            if "Poppins" in familia:
                return QFont("Arial", tamaño, QFont.Bold if negrita else QFont.Normal)
            else:
                return QFont("Segoe UI", tamaño, QFont.Bold if negrita else QFont.Normal)
            
    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

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

    def cargar_icono(self, ruta_icono):
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        absolute_path = os.path.join(script_dir, ruta_icono)
        
        print(f"Intentando cargar ícono: {absolute_path}")
        
        if os.path.exists(absolute_path):
            icono = QIcon(absolute_path)
            if icono.isNull():
                print(f"Error: El ícono en {absolute_path} se cargó pero está vacío")
            else:
                print(f"Ícono cargado exitosamente: {absolute_path}")
            return icono
        else:
            print(f"Error: No se encontró el archivo de ícono: {absolute_path}")
            return QIcon()

    def obtener_ruta_logo(self, nombre_equipo):
        """Obtener la ruta del logo basado en el nombre del equipo"""
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        # Limpiar el nombre del equipo para el archivo
        nombre_archivo = nombre_equipo.replace(" ", "_").replace("/", "_").replace("\\", "_") + ".png"
        ruta_logo = os.path.join(script_dir, "imagenes", nombre_archivo)
        
        # Verificar si existe el archivo
        if os.path.exists(ruta_logo):
            return ruta_logo
        
        # Si no existe, intentar con extensión .jpg
        ruta_logo_jpg = os.path.join(script_dir, "imagenes", nombre_archivo.replace(".png", ".jpg"))
        if os.path.exists(ruta_logo_jpg):
            return ruta_logo_jpg
            
        return None
#----------------------------------------------Funciones para cargar datos
    def cargar_equipos(self):
        lista_equipos = self.extractor.get_all_teams()

        if lista_equipos:
            self.nombre_equipos = [equipo["full_name"] for equipo in lista_equipos]
            self.nombre_local_cb.addItem("Seleccionar Equipo Local...")
            self.nombre_local_cb.addItems(self.nombre_equipos)
            self.nombre_visitante_cb.addItem("Seleccionar Equipo Visitante...")
            self.nombre_visitante_cb.addItems(self.nombre_equipos)

            self.nombre_local_cb.currentTextChanged.connect(self.actualizar_logo_local)
            self.nombre_visitante_cb.currentTextChanged.connect(self.actualizar_logo_visitante)
            
            self.nombre_local_cb.currentTextChanged.connect(lambda: self.actualizar_tabla_equipo("local"))
            self.nombre_visitante_cb.currentTextChanged.connect(lambda: self.actualizar_tabla_equipo("visitante"))
            
            # Conectar para evitar equipos duplicados
            self.nombre_local_cb.currentTextChanged.connect(self.verificar_equipos_duplicados)
            self.nombre_visitante_cb.currentTextChanged.connect(self.verificar_equipos_duplicados)

            if len(self.nombre_equipos) > 0:
                self.nombre_local_cb.setCurrentIndex(0)
                self.nombre_visitante_cb.setCurrentIndex(0)
            self.actualizar_tablero()
        else:
            QMessageBox.critical(self, "Error de api", "No se pudo cargar la lista de equipos..")

    def verificar_equipos_duplicados(self):
        """Evitar que se seleccionen los mismos equipos"""
        equipo_local = self.nombre_local_cb.currentText()
        equipo_visitante = self.nombre_visitante_cb.currentText()
        
        if (equipo_local == equipo_visitante and 
            not equipo_local.startswith("Seleccionar") and 
            not equipo_visitante.startswith("Seleccionar")):
            
            QMessageBox.warning(self, "Equipos Duplicados", 
                              "No puedes seleccionar el mismo equipo para local y visitante.")
            
            # Revertir el cambio dependiendo de qué combobox se modificó
            if self.sender() == self.nombre_local_cb:
                self.nombre_local_cb.setCurrentIndex(0)
            else:
                self.nombre_visitante_cb.setCurrentIndex(0)

    def actualizar_logo_local(self, nombre_equipo):
        """Actualizar el logo del equipo local en ambos lados"""
        if nombre_equipo and not nombre_equipo.startswith("Seleccionar"):
            ruta_logo = self.obtener_ruta_logo(nombre_equipo)
            if ruta_logo:
                self.logo_local_izquierdo.set_logo(ruta_logo)
                self.logo_local_derecho.set_logo(ruta_logo)
            else:
                self.logo_local_izquierdo.set_logo_placeholder()
                self.logo_local_derecho.set_logo_placeholder()
        else:
            self.logo_local_izquierdo.set_logo_placeholder()
            self.logo_local_derecho.set_logo_placeholder()

    def actualizar_logo_visitante(self, nombre_equipo):
        """Actualizar el logo del equipo visitante en ambos lados"""
        if nombre_equipo and not nombre_equipo.startswith("Seleccionar"):
            ruta_logo = self.obtener_ruta_logo(nombre_equipo)
            if ruta_logo:
                self.logo_visitante_izquierdo.set_logo(ruta_logo)
                self.logo_visitante_derecho.set_logo(ruta_logo)
            else:
                self.logo_visitante_izquierdo.set_logo_placeholder()
                self.logo_visitante_derecho.set_logo_placeholder()
        else:
            self.logo_visitante_izquierdo.set_logo_placeholder()
            self.logo_visitante_derecho.set_logo_placeholder()

    #------------------------------------------Pantalla principal
    def crear_pestaña_principal(self):
        widget = QWidget()
        layout_principal = QHBoxLayout(widget)

        lado_izquierdo = QVBoxLayout()

        grupo_local = QGroupBox("Equipo Local")
        layout_local = QVBoxLayout(grupo_local)
        
        layout_superior_local = QHBoxLayout()
        
        self.logo_local_izquierdo = LogoLabel()
        self.logo_local_izquierdo.setFixedSize(60, 60)
        layout_superior_local.addWidget(self.logo_local_izquierdo)
        
        self.nombre_local_cb = QComboBox()
        self.nombre_local_cb.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.nombre_local_cb.currentIndexChanged.connect(self.actualizar_tablero)
        layout_superior_local.addWidget(self.nombre_local_cb)
        
        layout_local.addLayout(layout_superior_local)

        grupo_tm_local = QGroupBox("Tiempo Muerto")
        layout_tm_local = QVBoxLayout(grupo_tm_local)
        layout_tm_local.setContentsMargins(2, 2, 2, 2)
        layout_tm_local.setSpacing(2)

        def fila_tm(label_text, checkboxes):
            layout = QHBoxLayout()
            layout.setSpacing(2)
            lbl = QLabel(label_text)
            lbl.setFixedWidth(30)
            layout.addWidget(lbl)
            for cb in checkboxes:
                cb.setFixedWidth(20)
                cb.setStyleSheet("margin:0px; padding:0px;")
                layout.addWidget(cb)
            layout.addStretch(1)
            return layout

        self.tm_local_1 = QCheckBox()
        self.tm_local_2 = QCheckBox()
        layout_tm_local.addLayout(fila_tm("1ra:", [self.tm_local_1, self.tm_local_2]))

        self.tm_local_3 = QCheckBox()
        self.tm_local_4 = QCheckBox()
        self.tm_local_5 = QCheckBox()
        layout_tm_local.addLayout(fila_tm("2da:", [self.tm_local_3, self.tm_local_4, self.tm_local_5]))

        self.tm_local_extra = QCheckBox()
        layout_tm_local.addLayout(fila_tm("T.X:", [self.tm_local_extra]))

        layout_local.addWidget(grupo_tm_local)

        self.tabla_local = self.crear_planilla_equipo("local")
        layout_local.addWidget(self.tabla_local)
        lado_izquierdo.addWidget(grupo_local)

        grupo_visitante = QGroupBox("Equipo Visitante")
        layout_visitante = QVBoxLayout(grupo_visitante)
        
        layout_superior_visitante = QHBoxLayout()
        
        self.logo_visitante_izquierdo = LogoLabel()
        self.logo_visitante_izquierdo.setFixedSize(60, 60) 
        layout_superior_visitante.addWidget(self.logo_visitante_izquierdo)
        
        self.nombre_visitante_cb = QComboBox()
        self.nombre_visitante_cb.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.nombre_visitante_cb.currentIndexChanged.connect(self.actualizar_tablero)
        layout_superior_visitante.addWidget(self.nombre_visitante_cb)
        
        layout_visitante.addLayout(layout_superior_visitante)

        grupo_tm_visitante = QGroupBox("Tiempo Muerto")
        layout_tm_visitante = QVBoxLayout(grupo_tm_visitante)
        layout_tm_visitante.setContentsMargins(2, 2, 2, 2)
        layout_tm_visitante.setSpacing(2)

        self.tm_visitante_1 = QCheckBox()
        self.tm_visitante_2 = QCheckBox()
        layout_tm_visitante.addLayout(fila_tm("1ra:", [self.tm_visitante_1, self.tm_visitante_2]))

        self.tm_visitante_3 = QCheckBox()
        self.tm_visitante_4 = QCheckBox()
        self.tm_visitante_5 = QCheckBox()
        layout_tm_visitante.addLayout(fila_tm("2da:", [self.tm_visitante_3, self.tm_visitante_4, self.tm_visitante_5]))

        self.tm_visitante_extra = QCheckBox()
        layout_tm_visitante.addLayout(fila_tm("T.X:", [self.tm_visitante_extra]))

        layout_visitante.addWidget(grupo_tm_visitante)

        self.tabla_visitante = self.crear_planilla_equipo("visitante")
        layout_visitante.addWidget(self.tabla_visitante)
        lado_izquierdo.addWidget(grupo_visitante)

        layout_principal.addLayout(lado_izquierdo, 75) 

        lado_derecho_widget = BackgroundWidget("imagenes/fondo.png")
        lado_derecho = QVBoxLayout(lado_derecho_widget)
        
        lado_derecho_widget = BackgroundWidget("imagenes/fondo.png")
        lado_derecho = QVBoxLayout(lado_derecho_widget)
        
        grupo_tiempo = QGroupBox("TIEMPO")
        grupo_tiempo.setFont(self.fuente_titulo)
        grupo_tiempo.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: red; }")
        layout_tiempo = QVBoxLayout(grupo_tiempo)

        self.label_cronometro = QLabel(f"{self.minutos:02d}:{self.segundos:02d}")
        self.label_cronometro.setAlignment(Qt.AlignCenter)
        self.label_cronometro.setFont(self.fuente_datos_bold)
        self.label_cronometro.setStyleSheet("font-size: 64px; font-weight: bold; color: red; margin: 15px;")
        layout_tiempo.addWidget(self.label_cronometro)

        self.label_cuarto_actual = QLabel("1°C")
        self.label_cuarto_actual.setAlignment(Qt.AlignCenter)
        self.label_cuarto_actual.setFont(self.fuente_datos_bold)
        self.label_cuarto_actual.setStyleSheet("font-size: 20px; font-weight: bold; color: red; background-color: rgba(255,255,255,150); padding: 5px; border-radius: 5px;")
        layout_tiempo.addWidget(self.label_cuarto_actual) 
        
        botones_crono = QHBoxLayout()
        btn_iniciar = QPushButton()
        btn_iniciar.setIcon(self.cargar_icono("imagenes/play.png"))
        btn_iniciar.setIconSize(QSize(35, 35))
        btn_iniciar.setFixedSize(50, 50)
        btn_iniciar.clicked.connect(self.iniciar_cronometro)
        botones_crono.addWidget(btn_iniciar)                 


        btn_pausar = QPushButton()
        btn_pausar.setIcon(self.cargar_icono("imagenes/pause.png"))
        btn_pausar.setIconSize(QSize(35, 35))
        btn_pausar.setFixedSize(50, 50)
        btn_pausar.clicked.connect(self.pausar_cronometro)
        botones_crono.addWidget(btn_pausar)

        btn_reiniciar = QPushButton()
        btn_reiniciar.setIcon(self.cargar_icono("imagenes/restart.png"))
        btn_reiniciar.setIconSize(QSize(35, 35))
        btn_reiniciar.setFixedSize(50, 50)
        btn_reiniciar.clicked.connect(self.reiniciar_cronometro)
        botones_crono.addWidget(btn_reiniciar)

        btn_sumar_min = QPushButton("+1")
        btn_sumar_min.setFixedSize(50, 50)
        btn_sumar_min.setStyleSheet("color: red; font-weight: bold;")
        btn_sumar_min.clicked.connect(self.sumar_minuto)
        botones_crono.addWidget(btn_sumar_min)

        btn_restar_min = QPushButton("-1")
        btn_restar_min.setFixedSize(50, 50)
        btn_restar_min.setStyleSheet("color: red; font-weight: bold;")
        btn_restar_min.clicked.connect(self.restar_minuto)
        botones_crono.addWidget(btn_restar_min)
        
        layout_tiempo.addLayout(botones_crono)
        
        layout_faltas = QHBoxLayout()
    
        self.label_faltas_local = QLabel(f"F. Local: {self.faltas_local}/5")
        self.label_faltas_local.setAlignment(Qt.AlignCenter)
        self.label_faltas_local.setFont(self.fuente_datos)
        self.label_faltas_local.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(255,255,255,150); padding: 5px; border-radius: 5px;")
        layout_faltas.addWidget(self.label_faltas_local)
                    
        self.label_faltas_visitante = QLabel(f"F. Visitante: {self.faltas_visitante}/5")
        self.label_faltas_visitante.setAlignment(Qt.AlignCenter)
        self.label_faltas_visitante.setFont(self.fuente_datos)
        self.label_faltas_visitante.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(255,255,255,150); padding: 5px; border-radius: 5px;")
        layout_faltas.addWidget(self.label_faltas_visitante)
                    
        layout_tiempo.addLayout(layout_faltas)
        
        lado_derecho.addWidget(grupo_tiempo)
        
        grupo_puntuaciones = QGroupBox("PUNTUACIÓN POR CUARTO")
        grupo_puntuaciones.setFont(self.fuente_titulo)
        grupo_puntuaciones.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: red; }")
        layout_puntuaciones = QGridLayout(grupo_puntuaciones)  # AGREGAR ESTA LÍNEA

        layout_puntuaciones.setColumnStretch(0, 2)
        layout_puntuaciones.setColumnStretch(1, 3)
        layout_puntuaciones.setColumnStretch(2, 3)
        
        layout_puntuaciones.addWidget(QLabel(""), 0, 0)

        self.logo_local_derecho = LogoLabel()
        self.logo_local_derecho.setFixedSize(150, 150)
        layout_puntuaciones.addWidget(self.logo_local_derecho, 0, 1)

        self.logo_visitante_derecho = LogoLabel()
        self.logo_visitante_derecho.setFixedSize(150, 150)
        layout_puntuaciones.addWidget(self.logo_visitante_derecho, 0, 2)

        cuartos = [
            ("1° CUARTO", 1),
            ("2° CUARTO", 2),
            ("3° CUARTO", 3),
            ("4° CUARTO", 4),
            ("TIEMPO EXTRA", 5)
        ]

        self.labels_puntos_local = []
        self.labels_puntos_visitante = []

        for fila, (nombre_cuarto, numero_cuarto) in enumerate(cuartos, 1):
            lbl_cuarto = QLabel(nombre_cuarto)
            lbl_cuarto.setStyleSheet("font-weight: bold; font-size: 12px; color: red; background-color: rgba(255,255,255,150); padding: 8px; margin: 2px; border-radius: 5px;")
            lbl_cuarto.setAlignment(Qt.AlignCenter)
            lbl_cuarto.setMinimumWidth(80)
            layout_puntuaciones.addWidget(lbl_cuarto, fila, 0)
            
            lbl_puntos_local = QLabel("0")
            lbl_puntos_local.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(173,216,230,150); padding: 10px; margin: 2px; border-radius: 5px;")
            lbl_puntos_local.setAlignment(Qt.AlignCenter)
            layout_puntuaciones.addWidget(lbl_puntos_local, fila, 1)
            self.labels_puntos_local.append(lbl_puntos_local)
            
            lbl_puntos_visitante = QLabel("0")
            lbl_puntos_visitante.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(255,182,193,150); padding: 10px; margin: 2px; border-radius: 5px;")
            lbl_puntos_visitante.setAlignment(Qt.AlignCenter)
            layout_puntuaciones.addWidget(lbl_puntos_visitante, fila, 2)
            self.labels_puntos_visitante.append(lbl_puntos_visitante)

        lbl_total = QLabel("TOTAL")
        lbl_total.setStyleSheet("font-weight: bold; font-size: 14px; color: red; background-color: rgba(255,255,255,200); padding: 10px; margin: 2px; border-radius: 5px;")
        lbl_total.setAlignment(Qt.AlignCenter)
        lbl_total.setMinimumWidth(80)
        layout_puntuaciones.addWidget(lbl_total, 6, 0)

        self.label_total_local = QLabel("0")
        self.label_total_local.setStyleSheet("font-size: 18px; font-weight: bold; color: red; background-color: rgba(135,206,250,200); padding: 12px; margin: 2px; border-radius: 5px;")
        self.label_total_local.setAlignment(Qt.AlignCenter)
        layout_puntuaciones.addWidget(self.label_total_local, 6, 1)

        self.label_total_visitante = QLabel("0")
        self.label_total_visitante.setStyleSheet("font-size: 18px; font-weight: bold; color: red; background-color: rgba(255,105,180,200); padding: 12px; margin: 2px; border-radius: 5px;")
        self.label_total_visitante.setAlignment(Qt.AlignCenter)
        layout_puntuaciones.addWidget(self.label_total_visitante, 6, 2)
        
        lado_derecho.addWidget(grupo_puntuaciones)

        lado_derecho.addStretch()
        layout_principal.addWidget(lado_derecho_widget, 25) 

        return widget

    def crear_planilla_equipo(self, equipo="local"):
        tabla = QTableWidget(15, 21)  
        tabla.setHorizontalHeaderLabels([
            "N°", "Jugador", "F1", "F2", "F3", "F4", "F5", 
            "1P✓", "1P✗", "2P✓", "2P✗", "3P✓", "3P✗",
            "AST", "REB", "PER", "ROB", "TAP", 
            "%1P", "%2P", "%3P"  
        ])
        
        tabla.setColumnWidth(0, 40)   
        tabla.setColumnWidth(1, 120)  
        for col in range(2, 7):       
            tabla.setColumnWidth(col, 30)
        for col in range(7, 13):      
            tabla.setColumnWidth(col, 40)
        for col in range(13, 18):     
            tabla.setColumnWidth(col, 45)
        for col in range(18, 21):     
            tabla.setColumnWidth(col, 50)
        
        tabla.verticalHeader().setDefaultSectionSize(60)
        
        icon_size = QSize(25, 25)
        
        for fila in range(15):
            tabla.setCellWidget(fila, 0, QLineEdit())
            
            tabla.setCellWidget(fila, 1, QLineEdit())
            
            checkboxes_faltas = []
            for col in range(2, 7):
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left:0px; margin-right:0px;")
                checkbox.stateChanged.connect(partial(self.controlar_faltas_secuencial, fila, col-2, tabla, equipo))
                tabla.setCellWidget(fila, col, checkbox)
                checkboxes_faltas.append(checkbox)
            
            simple_check = QPushButton()
            simple_check.setIcon(self.cargar_icono("imagenes/pelota1.png"))
            simple_check.setIconSize(icon_size)
            simple_check.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; }")
            simple_check.clicked.connect(partial(self.actualizar_puntos_jugador, fila, tabla, equipo, 1, True))
            tabla.setCellWidget(fila, 7, simple_check)
            
            simple_cross = QPushButton("✗")
            simple_cross.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; font-weight: bold; }")
            simple_cross.clicked.connect(partial(self.actualizar_puntos_jugador, fila, tabla, equipo, 1, False))
            tabla.setCellWidget(fila, 8, simple_cross)
            
            doble_check = QPushButton()
            doble_check.setIcon(self.cargar_icono("imagenes/pelota2.png"))
            doble_check.setIconSize(icon_size)
            doble_check.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; }")
            doble_check.clicked.connect(partial(self.actualizar_puntos_jugador, fila, tabla, equipo, 2, True))
            tabla.setCellWidget(fila, 9, doble_check)
            
            doble_cross = QPushButton("✗")
            doble_cross.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; font-weight: bold; }")
            doble_cross.clicked.connect(partial(self.actualizar_puntos_jugador, fila, tabla, equipo, 2, False))
            tabla.setCellWidget(fila, 10, doble_cross)
            
            triple_check = QPushButton()
            triple_check.setIcon(self.cargar_icono("imagenes/pelota3.png"))
            triple_check.setIconSize(icon_size)
            triple_check.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; }")
            triple_check.clicked.connect(partial(self.actualizar_puntos_jugador, fila, tabla, equipo, 3, True))
            tabla.setCellWidget(fila, 11, triple_check)
            
            triple_cross = QPushButton("✗")
            triple_cross.setStyleSheet("QPushButton { background-color: white; border: 1px solid gray; font-weight: bold; }")
            triple_cross.clicked.connect(partial(self.actualizar_puntos_jugador, fila, tabla, equipo, 3, False))
            tabla.setCellWidget(fila, 12, triple_cross)
            
            tabla.setCellWidget(fila, 13, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 13, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 13, -1, equipo)))
            
            tabla.setCellWidget(fila, 14, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 14, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 14, -1, equipo)))
            
            tabla.setCellWidget(fila, 15, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 15, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 15, -1, equipo)))
            
            tabla.setCellWidget(fila, 16, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 16, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 16, -1, equipo)))
            
            tabla.setCellWidget(fila, 17, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 17, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 17, -1, equipo)))
            
            porcentaje_1p = QLabel("0/0")
            porcentaje_1p.setAlignment(Qt.AlignCenter)
            porcentaje_1p.setStyleSheet("background-color: white; border: 1px solid gray; font-weight: bold;")
            tabla.setCellWidget(fila, 18, porcentaje_1p)
            
            porcentaje_2p = QLabel("0/0")
            porcentaje_2p.setAlignment(Qt.AlignCenter)
            porcentaje_2p.setStyleSheet("background-color: white; border: 1px solid gray; font-weight: bold;")
            tabla.setCellWidget(fila, 19, porcentaje_2p)
            
            porcentaje_3p = QLabel("0/0")
            porcentaje_3p.setAlignment(Qt.AlignCenter)
            porcentaje_3p.setStyleSheet("background-color: white; border: 1px solid gray; font-weight: bold;")
            tabla.setCellWidget(fila, 20, porcentaje_3p)
        
        return tabla

    def controlar_faltas_secuencial(self, fila, indice_falta, tabla, equipo, estado):
        if estado == Qt.Checked:
            for i in range(indice_falta):
                checkbox_anterior = tabla.cellWidget(fila, 2 + i)
                if isinstance(checkbox_anterior, QCheckBox) and not checkbox_anterior.isChecked():

                    checkbox_actual = tabla.cellWidget(fila, 2 + indice_falta)
                    if isinstance(checkbox_actual, QCheckBox):
                        checkbox_actual.setChecked(False)
                        QMessageBox.warning(self, "Faltas Secuenciales", 
                                          "Debes marcar las faltas en orden. Primero marca la falta 1, luego la 2, etc.")
                    return
        
        if estado == Qt.Unchecked:
            for i in range(indice_falta + 1, 5):  # 5 faltas totales (0-4)
                checkbox_siguiente = tabla.cellWidget(fila, 2 + i)
                if isinstance(checkbox_siguiente, QCheckBox) and checkbox_siguiente.isChecked():
                    checkbox_siguiente.setChecked(False)
        
        self.verificar_faltas(fila, tabla, equipo)

    def crear_celda_contador(self, valor_inicial, funcion_mas, funcion_menos):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)
        
        btn_menos = QPushButton("-")
        btn_menos.setFixedSize(20, 20)
        btn_menos.clicked.connect(funcion_menos)
        
        label = QLabel(str(valor_inicial))
        label.setAlignment(Qt.AlignCenter)
        label.setFixedWidth(25)
        label.setStyleSheet("background-color: white; border: 1px solid gray; font-weight: bold;")
        
        btn_mas = QPushButton("+")
        btn_mas.setFixedSize(20, 20)
        btn_mas.clicked.connect(funcion_mas)
        
        layout.addWidget(btn_menos)
        layout.addWidget(label)
        layout.addWidget(btn_mas)
        
        return widget

    def actualizar_estadistica(self, fila, columna, cambio, equipo):
        if equipo == "local":
            tabla = self.tabla_local
            estadisticas = self.estadisticas_local
        else:
            tabla = self.tabla_visitante
            estadisticas = self.estadisticas_visitante
        
        nombre_widget = tabla.cellWidget(fila, 1)
        if isinstance(nombre_widget, QLineEdit):
            nombre_jugador = nombre_widget.text()
            if not nombre_jugador:
                nombre_jugador = f"Jugador {fila+1}"
        else:
            nombre_jugador = f"Jugador {fila+1}"
        
        if nombre_jugador not in estadisticas:
            estadisticas[nombre_jugador] = {
                'puntos': 0, 'asistencias': 0, 'rebotes': 0, 
                'perdidas': 0, 'robos': 0, 'tapones': 0
            }
        
        mapeo_estadisticas = {
            13: 'asistencias',  
            14: 'rebotes',      
            15: 'perdidas',     
            16: 'robos',        
            17: 'tapones'      
        }
        
        if columna in mapeo_estadisticas:
            tipo_estadistica = mapeo_estadisticas[columna]
            estadisticas[nombre_jugador][tipo_estadistica] = max(0, 
                estadisticas[nombre_jugador][tipo_estadistica] + cambio)
        
        celda_widget = tabla.cellWidget(fila, columna)
        if celda_widget:
            # Buscar el QLabel dentro del widget
            for i in range(celda_widget.layout().count()):
                widget = celda_widget.layout().itemAt(i).widget()
                if isinstance(widget, QLabel):
                    try:
                        valor_actual = int(widget.text())
                        nuevo_valor = max(0, valor_actual + cambio)
                        widget.setText(str(nuevo_valor))
                        break
                    except ValueError:
                        print(f"Error: No se pudo convertir el valor del contador")
                    break

    def actualizar_puntos_jugador(self, fila, tabla, equipo, puntos, encesto):

        nombre_widget = tabla.cellWidget(fila, 1)
        if isinstance(nombre_widget, QLineEdit):
            nombre_jugador = nombre_widget.text()
            if not nombre_jugador:
                nombre_jugador = f"Jugador {fila+1}"
        else:
            nombre_jugador = f"Jugador {fila+1}"
        
        if equipo == "local":
            if nombre_jugador not in self.estadisticas_local:
                self.estadisticas_local[nombre_jugador] = {
                    'puntos': 0, 'asistencias': 0, 'rebotes': 0, 
                    'perdidas': 0, 'robos': 0, 'tapones': 0
                }
            if encesto:
                self.estadisticas_local[nombre_jugador]['puntos'] += puntos
        else:
            if nombre_jugador not in self.estadisticas_visitante:
                self.estadisticas_visitante[nombre_jugador] = {
                    'puntos': 0, 'asistencias': 0, 'rebotes': 0, 
                    'perdidas': 0, 'robos': 0, 'tapones': 0
                }
            if encesto:
                self.estadisticas_visitante[nombre_jugador]['puntos'] += puntos

        columna_porcentaje = {1: 18, 2: 19, 3: 20}[puntos]
        porcentaje_label = tabla.cellWidget(fila, columna_porcentaje)
        
        if isinstance(porcentaje_label, QLabel):
            texto_actual = porcentaje_label.text()
            if texto_actual == "0/0":
                if encesto:
                    nuevo_texto = "1/1"
                else:
                    nuevo_texto = "0/1"
            else:
                encestados, intentados = map(int, texto_actual.split('/'))
                intentados += 1
                if encesto:
                    encestados += 1
                nuevo_texto = f"{encestados}/{intentados}"
            
            porcentaje_label.setText(nuevo_texto)
        
        if encesto:
            if equipo == "local":
                self.puntos_local[self.cuarto_actual] += puntos
                self.labels_puntos_local[self.cuarto_actual].setText(str(self.puntos_local[self.cuarto_actual]))
            else:
                self.puntos_visitante[self.cuarto_actual] += puntos
                self.labels_puntos_visitante[self.cuarto_actual].setText(str(self.puntos_visitante[self.cuarto_actual]))
            
            self.actualizar_totales()

    def actualizar_totales(self):
        total_local = sum(self.puntos_local)
        total_visitante = sum(self.puntos_visitante)
        
        self.label_total_local.setText(str(total_local))
        self.label_total_visitante.setText(str(total_visitante))

    def crear_pestaña_historial(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        titulo = QLabel("Historial de Partidos")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(self.fuente_titulo)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #2a2a2a;")
        layout.addWidget(titulo)

        botones_layout = QHBoxLayout()
        
        btn_actualizar = QPushButton("Actualizar Historial")
        btn_actualizar.clicked.connect(self.cargar_historial_partidos)
        botones_layout.addWidget(btn_actualizar)
        
        btn_buscar = QPushButton("Buscar por ID")
        btn_buscar.clicked.connect(self.buscar_partido_por_id)
        botones_layout.addWidget(btn_buscar)
        
        layout.addLayout(botones_layout)

        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(8)
        self.tabla_historial.setHorizontalHeaderLabels([
            "ID", "Fecha", "Equipo Local", "Equipo Visitante", 
            "Marcador", "Faltas", "T.Muertos", "Cuarto"
        ])
        
        self.tabla_historial.setColumnWidth(0, 60)   
        self.tabla_historial.setColumnWidth(1, 150)  
        self.tabla_historial.setColumnWidth(2, 150)  
        self.tabla_historial.setColumnWidth(3, 150)  
        self.tabla_historial.setColumnWidth(4, 100)  
        self.tabla_historial.setColumnWidth(5, 80)   
        self.tabla_historial.setColumnWidth(6, 80)   
        self.tabla_historial.setColumnWidth(7, 80)   
        
        layout.addWidget(self.tabla_historial)

        self.cargar_historial_partidos()
        
        return widget

    def cargar_historial_partidos(self):
        try:
            import basededatos
            
            conexion = basededatos.conectar_base()
            if not conexion:
                QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
                return
            
            partidos = basededatos.obtener_partidos_usuario(conexion, limite=20)
            conexion.close()
            
            self.tabla_historial.setRowCount(len(partidos))
            
            for fila, partido in enumerate(partidos):

                self.tabla_historial.setItem(fila, 0, QTableWidgetItem(str(partido['id_partido'])))
                
                fecha = partido['fecha_partido'].strftime("%Y-%m-%d %H:%M") if partido['fecha_partido'] else "N/A"
                self.tabla_historial.setItem(fila, 1, QTableWidgetItem(fecha))
                
                self.tabla_historial.setItem(fila, 2, QTableWidgetItem(partido['equipo_local']))
                self.tabla_historial.setItem(fila, 3, QTableWidgetItem(partido['equipo_visitante']))
                
                marcador = f"{partido['marcador_local']} - {partido['marcador_visitante']}"
                self.tabla_historial.setItem(fila, 4, QTableWidgetItem(marcador))
                
                faltas = f"{partido['faltas_local']}/{partido['faltas_visitante']}"
                self.tabla_historial.setItem(fila, 5, QTableWidgetItem(faltas))
                
                tmuertos = f"{partido['tiempo_muertos_local']}/{partido['tiempo_muertos_visitante']}"
                self.tabla_historial.setItem(fila, 6, QTableWidgetItem(tmuertos))
                
                self.tabla_historial.setItem(fila, 7, QTableWidgetItem(partido.get('cuarto_actual', 'N/A')))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar historial: {str(e)}")

    def buscar_partido_por_id(self):
        try:
            id_partido, ok = QInputDialog.getInt(self, "Buscar Partido", 
                                            "Ingresa el ID del partido:", 
                                            min=1, max=10000)
            if ok:
                import basededatos
                conexion = basededatos.conectar_base()
                if conexion:
                    partido = basededatos.obtener_partido_por_id(conexion, id_partido)
                    conexion.close()
                    
                    if partido:
                        self.mostrar_detalles_partido(partido)
                    else:
                        QMessageBox.information(self, "No encontrado", 
                                            f"No se encontró ningún partido con ID {id_partido}")                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar partido: {str(e)}")

    def mostrar_detalles_partido(self, partido):
        detalles = f"""
        - DETALLES DEL PARTIDO ID: {partido['id_partido']}
        
        - PARTIDO: {partido['equipo_local']} vs {partido['equipo_visitante']}
        - FECHA: {partido['fecha_partido'].strftime('%Y-%m-%d %H:%M') if partido['fecha_partido'] else 'N/A'}
        
        - MARCADOR FINAL: {partido['marcador_local']} - {partido['marcador_visitante']}
        
        - PUNTUACIÓN POR CUARTO:
        1°C: {partido.get('puntos_q1_local', 0)} - {partido.get('puntos_q1_visitante', 0)}
        2°C: {partido.get('puntos_q2_local', 0)} - {partido.get('puntos_q2_visitante', 0)}
        3°C: {partido.get('puntos_q3_local', 0)} - {partido.get('puntos_q3_visitante', 0)}
        4°C: {partido.get('puntos_q4_local', 0)} - {partido.get('puntos_q4_visitante', 0)}
        T.E: {partido.get('puntos_te_local', 0)} - {partido.get('puntos_te_visitante', 0)}
        
        -  FALTAS: Local {partido['faltas_local']}/5 - Visitante {partido['faltas_visitante']}/5
        -  TIEMPOS MUERTOS: Local {partido['tiempo_muertos_local']}/7 - Visitante {partido['tiempo_muertos_visitante']}/7
        - DURACIÓN: {partido['duracion_partido']}
        """
        QMessageBox.information(self, "Detalles del Partido", detalles)

    def crear_pantalla_estadisticas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        titulo = QLabel("Estadísticas de Juego")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setFont(self.fuente_titulo)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #2a2a2a;")
        layout.addWidget(titulo)

        contenedor_estadisticas = QHBoxLayout()
        
        seccion_resumen = QVBoxLayout()
        
        grupo_equipos = QGroupBox("Información del Partido")
        grupo_equipos.setFont(self.fuente_titulo)
        layout_equipos = QHBoxLayout(grupo_equipos)
        
        contenedor_local = QVBoxLayout()
        self.logo_estadisticas_local = LogoLabel()
        self.logo_estadisticas_local.setFixedSize(120, 120)
        contenedor_local.addWidget(self.logo_estadisticas_local)
        
        self.label_nombre_local_est = QLabel("Equipo Local")
        self.label_nombre_local_est.setAlignment(Qt.AlignCenter)
        self.label_nombre_local_est.setStyleSheet("font-weight: bold; font-size: 16px; margin: 5px;")
        contenedor_local.addWidget(self.label_nombre_local_est)
        
        self.label_marcador_local_est = QLabel("0")
        self.label_marcador_local_est.setAlignment(Qt.AlignCenter)
        self.label_marcador_local_est.setStyleSheet("font-size: 24px; font-weight: bold; color: #1e90ff; background-color: #f0f8ff; padding: 10px; border-radius: 5px;")
        contenedor_local.addWidget(self.label_marcador_local_est)
        
        layout_equipos.addLayout(contenedor_local)
        
        label_vs = QLabel("VS")
        label_vs.setAlignment(Qt.AlignCenter)
        label_vs.setStyleSheet("font-size: 20px; font-weight: bold; margin: 20px;")
        layout_equipos.addWidget(label_vs)
        
        contenedor_visitante = QVBoxLayout()
        self.logo_estadisticas_visitante = LogoLabel()
        self.logo_estadisticas_visitante.setFixedSize(120, 120)
        contenedor_visitante.addWidget(self.logo_estadisticas_visitante)
        
        self.label_nombre_visitante_est = QLabel("Equipo Visitante")
        self.label_nombre_visitante_est.setAlignment(Qt.AlignCenter)
        self.label_nombre_visitante_est.setStyleSheet("font-weight: bold; font-size: 16px; margin: 5px;")
        contenedor_visitante.addWidget(self.label_nombre_visitante_est)
        
        self.label_marcador_visitante_est = QLabel("0")
        self.label_marcador_visitante_est.setAlignment(Qt.AlignCenter)
        self.label_marcador_visitante_est.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff69b4; background-color: #fff0f5; padding: 10px; border-radius: 5px;")
        contenedor_visitante.addWidget(self.label_marcador_visitante_est)
        
        layout_equipos.addLayout(contenedor_visitante)
        
        seccion_resumen.addWidget(grupo_equipos)
        
        grupo_cuartos = QGroupBox("Puntuación por Cuarto")
        grupo_cuartos.setFont(self.fuente_titulo)
        layout_cuartos = QGridLayout(grupo_cuartos) 
        
        # CORRECCIÓN AQUÍ: Usar layout_cuartos en lugar de grupo_cuartos
        layout_cuartos.addWidget(QLabel("Cuarto"), 0, 0)
        layout_cuartos.addWidget(QLabel("Local"), 0, 1)
        layout_cuartos.addWidget(QLabel("Visitante"), 0, 2)
        
        cuartos = ["1° Cuarto", "2° Cuarto", "3° Cuarto", "4° Cuarto", "Tiempo Extra"]
        self.labels_cuartos_local = []
        self.labels_cuartos_visitante = []
        
        for i, cuarto in enumerate(cuartos, 1):
            # CORRECCIÓN AQUÍ: Usar layout_cuartos en lugar de grupo_cuartos
            layout_cuartos.addWidget(QLabel(cuarto), i, 0)
            
            label_local = QLabel("0")
            label_local.setAlignment(Qt.AlignCenter)
            label_local.setStyleSheet("background-color: #f0f8ff; padding: 5px; border: 1px solid #ccc;")
            layout_cuartos.addWidget(label_local, i, 1)
            self.labels_cuartos_local.append(label_local)
            
            label_visitante = QLabel("0")
            label_visitante.setAlignment(Qt.AlignCenter)
            label_visitante.setStyleSheet("background-color: #fff0f5; padding: 5px; border: 1px solid #ccc;")
            layout_cuartos.addWidget(label_visitante, i, 2)
            self.labels_cuartos_visitante.append(label_visitante)
        
        # CORRECCIÓN AQUÍ: Usar layout_cuartos en lugar de grupo_cuartos
        layout_cuartos.addWidget(QLabel("TOTAL"), 6, 0)
        
        self.label_total_local_est = QLabel("0")
        self.label_total_local_est.setAlignment(Qt.AlignCenter)
        self.label_total_local_est.setStyleSheet("font-weight: bold; background-color: #e6f3ff; padding: 5px; border: 2px solid #1e90ff;")
        layout_cuartos.addWidget(self.label_total_local_est, 6, 1)
        
        self.label_total_visitante_est = QLabel("0")
        self.label_total_visitante_est.setAlignment(Qt.AlignCenter)
        self.label_total_visitante_est.setStyleSheet("font-weight: bold; background-color: #ffe6f2; padding: 5px; border: 2px solid #ff69b4;")
        layout_cuartos.addWidget(self.label_total_visitante_est, 6, 2)
        
        seccion_resumen.addWidget(grupo_cuartos)
        
        grupo_general = QGroupBox("Estadísticas Generales")
        grupo_general.setFont(self.fuente_titulo)
        layout_general = QGridLayout(grupo_general)
        
        layout_general.addWidget(QLabel("Faltas Totales:"), 0, 0)
        self.label_faltas_local_est = QLabel("0")
        self.label_faltas_local_est.setStyleSheet("font-weight: bold;")
        layout_general.addWidget(self.label_faltas_local_est, 0, 1)
        
        self.label_faltas_visitante_est = QLabel("0")
        self.label_faltas_visitante_est.setStyleSheet("font-weight: bold;")
        layout_general.addWidget(self.label_faltas_visitante_est, 0, 2)
        
        layout_general.addWidget(QLabel("Tiempos Muertos:"), 1, 0)
        self.label_tm_local_est = QLabel("0")
        layout_general.addWidget(self.label_tm_local_est, 1, 1)
        
        self.label_tm_visitante_est = QLabel("0")
        layout_general.addWidget(self.label_tm_visitante_est, 1, 2)
        
        layout_general.addWidget(QLabel("Cuarto Actual:"), 2, 0)
        self.label_cuarto_actual_est = QLabel("1°C")
        self.label_cuarto_actual_est.setStyleSheet("font-weight: bold;")
        layout_general.addWidget(self.label_cuarto_actual_est, 2, 1, 1, 2)
        
        seccion_resumen.addWidget(grupo_general)
        
        contenedor_estadisticas.addLayout(seccion_resumen, 60)
        
        seccion_derecha = QVBoxLayout()
        
        grupo_destacados = QGroupBox("Jugadores Destacados")
        grupo_destacados.setFont(self.fuente_titulo)
        layout_destacados = QVBoxLayout(grupo_destacados)
        
        self.area_destacados = QTextEdit()
        self.area_destacados.setReadOnly(True)
        self.area_destacados.setMaximumHeight(200)
        layout_destacados.addWidget(self.area_destacados)
        
        seccion_derecha.addWidget(grupo_destacados)
        
        grupo_resumen = QGroupBox("Resumen del Partido")
        grupo_resumen.setFont(self.fuente_titulo)
        layout_resumen = QVBoxLayout(grupo_resumen)
        
        self.area_resumen = QTextEdit()
        self.area_resumen.setReadOnly(True)
        layout_resumen.addWidget(self.area_resumen)
        
        seccion_derecha.addWidget(grupo_resumen)
        
        contenedor_estadisticas.addLayout(seccion_derecha, 40)
        
        layout.addLayout(contenedor_estadisticas)
        
        botones_layout = QHBoxLayout()
        
        btn_actualizar = QPushButton("Actualizar Estadísticas")
        btn_actualizar.clicked.connect(self.actualizar_estadisticas)
        botones_layout.addWidget(btn_actualizar)
        
        btn_guardar = QPushButton("Guardar Partido en Base de Datos")
        btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        btn_guardar.clicked.connect(self.guardar_partido_bd)
        botones_layout.addWidget(btn_guardar)
        
        btn_limpiar = QPushButton("Limpiar Estadísticas")
        btn_limpiar.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")
        btn_limpiar.clicked.connect(self.limpiar_estadisticas)
        botones_layout.addWidget(btn_limpiar)
        
        layout.addLayout(botones_layout)

        self.actualizar_estadisticas()
        
        return widget
    
    def actualizar_estadisticas(self):
        try:
            equipo_local = self.nombre_local_cb.currentText()
            equipo_visitante = self.nombre_visitante_cb.currentText()
            
            self.label_nombre_local_est.setText(equipo_local if not equipo_local.startswith("Seleccionar") else "Equipo Local")
            self.label_nombre_visitante_est.setText(equipo_visitante if not equipo_visitante.startswith("Seleccionar") else "Equipo Visitante")
            
            if not equipo_local.startswith("Seleccionar"):
                ruta_logo_local = self.obtener_ruta_logo(equipo_local)
                if ruta_logo_local:
                    self.logo_estadisticas_local.set_logo(ruta_logo_local)
            
            if not equipo_visitante.startswith("Seleccionar"):
                ruta_logo_visitante = self.obtener_ruta_logo(equipo_visitante)
                if ruta_logo_visitante:
                    self.logo_estadisticas_visitante.set_logo(ruta_logo_visitante)
            
            total_local = sum(self.puntos_local)
            total_visitante = sum(self.puntos_visitante)
            
            self.label_marcador_local_est.setText(str(total_local))
            self.label_marcador_visitante_est.setText(str(total_visitante))
            
            for i in range(5):
                self.labels_cuartos_local[i].setText(str(self.puntos_local[i]))
                self.labels_cuartos_visitante[i].setText(str(self.puntos_visitante[i]))
            
            self.label_total_local_est.setText(str(total_local))
            self.label_total_visitante_est.setText(str(total_visitante))
            
            self.label_faltas_local_est.setText(str(self.faltas_local))
            self.label_faltas_visitante_est.setText(str(self.faltas_visitante))
            
            tm_local = sum([
                self.tm_local_1.isChecked(), self.tm_local_2.isChecked(),
                self.tm_local_3.isChecked(), self.tm_local_4.isChecked(),
                self.tm_local_5.isChecked(), self.tm_local_extra.isChecked()
            ])
            tm_visitante = sum([
                self.tm_visitante_1.isChecked(), self.tm_visitante_2.isChecked(),
                self.tm_visitante_3.isChecked(), self.tm_visitante_4.isChecked(),
                self.tm_visitante_5.isChecked(), self.tm_visitante_extra.isChecked()
            ])
            
            self.label_tm_local_est.setText(f"{tm_local}/7")
            self.label_tm_visitante_est.setText(f"{tm_visitante}/7")
            
            nombres_cuartos = ["1°C", "2°C", "3°C", "4°C", "T.E."]
            if self.cuarto_actual < len(nombres_cuartos):
                self.label_cuarto_actual_est.setText(nombres_cuartos[self.cuarto_actual])
            
            self.actualizar_jugadores_destacados()
            
            self.actualizar_resumen_partido()

        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")

    def actualizar_jugadores_destacados(self):
        try:
            todas_estadisticas = {**self.estadisticas_local, **self.estadisticas_visitante}
            
            if not todas_estadisticas:
                self.area_destacados.setText("\n\n📊 Registra estadísticas para ver jugadores destacados")
                return
            
            destacados_texto = "\n\n"
            
            if todas_estadisticas:
                max_anotador = max(todas_estadisticas.items(), 
                                key=lambda x: x[1]['puntos'])
                destacados_texto += f"• 🏀 Máximo anotador: {max_anotador[0]} ({max_anotador[1]['puntos']} pts)\n"
                
                max_rebotes = max(todas_estadisticas.items(), 
                                key=lambda x: x[1]['rebotes'])
                if max_rebotes[1]['rebotes'] > 0:
                    destacados_texto += f"• 📊 Mejor reboteador: {max_rebotes[0]} ({max_rebotes[1]['rebotes']} reb)\n"
                
                max_asistencias = max(todas_estadisticas.items(), 
                                    key=lambda x: x[1]['asistencias'])
                if max_asistencias[1]['asistencias'] > 0:
                    destacados_texto += f"• 🎯 Líder en asistencias: {max_asistencias[0]} ({max_asistencias[1]['asistencias']} ast)\n"
                
                def valor_defensa(estadisticas):
                    return estadisticas['robos'] + estadisticas['tapones']
                
                mejor_defensor = max(todas_estadisticas.items(), 
                                    key=lambda x: valor_defensa(x[1]))
                if valor_defensa(mejor_defensor[1]) > 0:
                    destacados_texto += f"• 🛡️ Mejor defensor: {mejor_defensor[0]} ({mejor_defensor[1]['robos']} rob, {mejor_defensor[1]['tapones']} tap)\n"
            
            self.area_destacados.setText(destacados_texto)
            
        except Exception as e:
            print(f"Error al actualizar jugadores destacados: {e}")
            self.area_destacados.setText("Error al calcular jugadores destacados")   

    def actualizar_resumen_partido(self):
        try:
            equipo_local = self.nombre_local_cb.currentText()
            equipo_visitante = self.nombre_visitante_cb.currentText()
            total_local = sum(self.puntos_local)
            total_visitante = sum(self.puntos_visitante)
            
            resumen_texto = f"\n\n"
            resumen_texto += f"PARTIDO: {equipo_local} vs {equipo_visitante}\n"
            resumen_texto += f"MARCADOR FINAL: {total_local} - {total_visitante}\n"
            resumen_texto += f"CUARTO ACTUAL: {self.label_cuarto_actual_est.text()}\n\n"
            
            resumen_texto += f"--- Puntuación por Cuarto ---\n"
            cuartos = ["1°C", "2°C", "3°C", "4°C", "T.E."]
            for i in range(5):
                resumen_texto += f"{cuartos[i]}: {self.puntos_local[i]} - {self.puntos_visitante[i]}\n"
            
            resumen_texto += f"\n--- Estadísticas Generales ---\n"
            resumen_texto += f"Faltas: Local {self.faltas_local}/5 - Visitante {self.faltas_visitante}/5\n"
            
            tm_local = sum([self.tm_local_1.isChecked(), self.tm_local_2.isChecked(),
                        self.tm_local_3.isChecked(), self.tm_local_4.isChecked(),
                        self.tm_local_5.isChecked(), self.tm_local_extra.isChecked()])
            tm_visitante = sum([self.tm_visitante_1.isChecked(), self.tm_visitante_2.isChecked(),
                            self.tm_visitante_3.isChecked(), self.tm_visitante_4.isChecked(),
                            self.tm_visitante_5.isChecked(), self.tm_visitante_extra.isChecked()])
            
            resumen_texto += f"Tiempos Muertos: Local {tm_local}/7 - Visitante {tm_visitante}/7\n"
            
            if total_local > total_visitante:
                resumen_texto += f"\nVA GANANDO: {equipo_local}\n"
            elif total_visitante > total_local:
                resumen_texto += f"\nVA GANANDO: {equipo_visitante}\n"
            else:
                resumen_texto += f"\nPARTIDO EMPATADO\n"
            
            self.area_resumen.setText(resumen_texto)
            
        except Exception as e:
            print(f"Error al actualizar resumen del partido: {e}") 
    
    def guardar_partido_bd(self):
        try:
            import basededatos
            
            conexion = basededatos.conectar_base()
            if not conexion:
                QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
                return
            
            equipo_local = self.nombre_local_cb.currentText()
            equipo_visitante = self.nombre_visitante_cb.currentText()
            
            if equipo_local.startswith("Seleccionar") or equipo_visitante.startswith("Seleccionar"):
                QMessageBox.warning(self, "Advertencia", "Debes seleccionar ambos equipos antes de guardar")
                conexion.close()
                return
            
            marcador_local = sum(self.puntos_local)
            marcador_visitante = sum(self.puntos_visitante)
            
            faltas_local = self.faltas_local
            faltas_visitante = self.faltas_visitante
            
            tiempo_muertos_local = sum([
                self.tm_local_1.isChecked(), self.tm_local_2.isChecked(),
                self.tm_local_3.isChecked(), self.tm_local_4.isChecked(),
                self.tm_local_5.isChecked(), self.tm_local_extra.isChecked()
            ])
            tiempo_muertos_visitante = sum([
                self.tm_visitante_1.isChecked(), self.tm_visitante_2.isChecked(),
                self.tm_visitante_3.isChecked(), self.tm_visitante_4.isChecked(),
                self.tm_visitante_5.isChecked(), self.tm_visitante_extra.isChecked()
            ])
            
            nombres_cuartos = ["1°C", "2°C", "3°C", "4°C", "T.E."]
            duracion_partido = f"{nombres_cuartos[self.cuarto_actual]} - {self.minutos:02d}:{self.segundos:02d}"
            
            usuario_registro = "UsuarioActual" 
            
            partido_id = basededatos.guardar_partido(
                conexion, 
                equipo_local, 
                equipo_visitante, 
                marcador_local,
                marcador_visitante, 
                faltas_local, 
                faltas_visitante,
                tiempo_muertos_local, 
                tiempo_muertos_visitante,
                duracion_partido, 
                usuario_registro,
                puntos_q1_local=self.puntos_local[0],
                puntos_q2_local=self.puntos_local[1],
                puntos_q3_local=self.puntos_local[2],
                puntos_q4_local=self.puntos_local[3],
                puntos_te_local=self.puntos_local[4],
                puntos_q1_visitante=self.puntos_visitante[0],
                puntos_q2_visitante=self.puntos_visitante[1],
                puntos_q3_visitante=self.puntos_visitante[2],
                puntos_q4_visitante=self.puntos_visitante[3],
                puntos_te_visitante=self.puntos_visitante[4],
                cuarto_actual=nombres_cuartos[self.cuarto_actual]
            )
            
            if partido_id:
                QMessageBox.information(self, "Éxito", 
                                    f"- Partido guardado correctamente\n"
                                    f"- ID del partido: {partido_id}\n"
                                    f"- {equipo_local} {marcador_local} - {marcador_visitante} {equipo_visitante}\n"
                                    f"- {duracion_partido}")
            else:
                QMessageBox.critical(self, "Error", "❌ No se pudo guardar el partido en la base de datos")
            
            conexion.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Error al guardar el partido: {str(e)}")
            print(f"Error detallado: {e}")

    def limpiar_estadisticas(self):
        respuesta = QMessageBox.question(self, "Confirmar", 
                                    "¿Estás seguro de que quieres limpiar todas las estadísticas?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if respuesta == QMessageBox.Yes:
            self.puntos_local = [0, 0, 0, 0, 0]
            self.puntos_visitante = [0, 0, 0, 0, 0]
            
            self.faltas_local = 0
            self.faltas_visitante = 0
            
            self.cuarto_actual = 0
            
            self.tm_local_1.setChecked(False)
            self.tm_local_2.setChecked(False)
            self.tm_local_3.setChecked(False)
            self.tm_local_4.setChecked(False)
            self.tm_local_5.setChecked(False)
            self.tm_local_extra.setChecked(False)
            
            self.tm_visitante_1.setChecked(False)
            self.tm_visitante_2.setChecked(False)
            self.tm_visitante_3.setChecked(False)
            self.tm_visitante_4.setChecked(False)
            self.tm_visitante_5.setChecked(False)
            self.tm_visitante_extra.setChecked(False)
            
            self.estadisticas_local.clear()
            self.estadisticas_visitante.clear()
            
            self.limpiar_faltas_tablas()
            
            self.actualizar_totales()
            self.actualizar_tablero()
            self.actualizar_estadisticas()
            
            QMessageBox.information(self, "Estadísticas Limpiadas", 
                                "Todas las estadísticas han sido reiniciadas.")
 
    def actualizar_tabla_equipo(self, equipo: str):
        if equipo == "local":
            equipo_elegido = self.nombre_local_cb
            tabla = self.tabla_local
        else:
            equipo_elegido = self.nombre_visitante_cb
            tabla = self.tabla_visitante
        
        nombre_equipo = equipo_elegido.currentText()
    
        if nombre_equipo.startswith("Seleccionar"):
            return
    
        self.limpiar_tabla_equipo(tabla)
    
        datos_jugadores = self.extractor.get_jugadores_por_equipo(nombre_equipo)

        if datos_jugadores:
            for fila, jugador in enumerate(datos_jugadores):
                if fila >= tabla.rowCount():
                    break

                numero_jugador = tabla.cellWidget(fila, 0)
                if isinstance(numero_jugador, QLineEdit):
                    numero_texto = str(jugador.get("number", "N/A"))
                    numero_jugador.setText(numero_texto)

                nombre_jugador = tabla.cellWidget(fila, 1)
                if isinstance(nombre_jugador, QLineEdit):
                    nombre_jugador.setText(jugador.get("name", "Jugador Desconocido"))
        else:
            QMessageBox.warning(self, "Datos Faltantes", f"No se pudo cargar la planilla para {nombre_equipo}")
            self.actualizar_tablero()

    def limpiar_tabla_equipo(self, tabla: QTableWidget):
        for fila in range(tabla.rowCount()):
            numero_widget = tabla.cellWidget(fila, 0)
            if isinstance(numero_widget, QLineEdit):
                numero_widget.setText("")
            
            nombre_widget = tabla.cellWidget(fila, 1)
            if isinstance(nombre_widget, QLineEdit):
                nombre_widget.setText("")
            
            for col in range(2, 7):
                checkbox = tabla.cellWidget(fila, col)
                if isinstance(checkbox, QCheckBox):
                    checkbox.setChecked(False)
                    checkbox.setStyleSheet("margin-left:0px; margin-right:0px;")
                    checkbox.setEnabled(True)
            
            for col in range(13, 18):
                celda_widget = tabla.cellWidget(fila, col)
                if celda_widget:
                    for i in range(celda_widget.layout().count()):
                        widget = celda_widget.layout().itemAt(i).widget()
                        if isinstance(widget, QLabel):
                            widget.setText("0")
                            break
            
            for col in range(18, 21):
                label = tabla.cellWidget(fila, col)
                if isinstance(label, QLabel):
                    label.setText("0/0")
    
   
    #------------------------------------------------Faltas
   
    def verificar_faltas(self, fila, tabla, equipo):
        contador = 0
        for col in range(2, 7):
            checkbox = tabla.cellWidget(fila, col)
            if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                contador += 1
        if contador <= 2:
            color = "background-color: lightgreen"
        elif contador <= 4:
            color = "background-color: yellow"
        else:
            color = "background-color: red"
        for col in range(2, 7):
            checkbox = tabla.cellWidget(fila, col)
            if isinstance(checkbox, QCheckBox):
                checkbox.setStyleSheet(f"margin-left:0px; margin-right:0px; {color}")
                checkbox.setEnabled(contador < 5 or checkbox.isChecked())
        self.actualizar_faltas_totales(equipo)
        
    def actualizar_faltas_totales(self, equipo):
        tabla = self.tabla_local if equipo == "local" else self.tabla_visitante
        total = 0
        
        for fila in range(15):
            faltas_jugador = 0
            for col in range(2, 7):  # Columnas F1-F5
                widget = tabla.cellWidget(fila, col)
                if isinstance(widget, QCheckBox) and widget.isChecked():
                    faltas_jugador += 1
            total += faltas_jugador
        
        total = min(total, 5)
        
        if equipo == "local":
            self.faltas_local = total
            self.label_faltas_local.setText(f"F. Local: {self.faltas_local}/5")
        else:
            self.faltas_visitante = total
            self.label_faltas_visitante.setText(f"F. Visitante: {self.faltas_visitante}/5")

    def resetear_faltas_totales(self):
        self.faltas_local = 0
        self.faltas_visitante = 0
        self.label_faltas_local.setText(f"F. Local: 0/5")
        self.label_faltas_visitante.setText(f"F. Visitante: 0/5")

    def limpiar_faltas_tablas(self):
        for tabla in [self.tabla_local, self.tabla_visitante]:
            for fila in range(tabla.rowCount()):
                for col in range(2, 7):  # Columnas F1-F5
                    checkbox = tabla.cellWidget(fila, col)
                    if isinstance(checkbox, QCheckBox):
                        checkbox.setChecked(False)
                        checkbox.setStyleSheet("margin-left:0px; margin-right:0px;")
                        checkbox.setEnabled(True)   
   
    # -----------------------------------------------Marcador
   
    def actualizar_tablero(self):
        nombre_local_cb = self.nombre_local_cb.currentText()
        nombre_visitante_cb = self.nombre_visitante_cb.currentText()
        self.label_faltas_local.setText(f"F. Local: {self.faltas_local}/5")
        self.label_faltas_visitante.setText(f"F. Visitante: {self.faltas_visitante}/5")
   
    #------------------------------------------------Funciones botones del cronómetro
    def actualizar_cronometro(self):
        if self.segundos == 0:
            if self.minutos == 0:
                self.avanzar_cuarto()
                return
            else:
                self.minutos -= 1
                self.segundos = 59
        else:
            self.segundos -= 1
        self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")

    def avanzar_cuarto(self):
        self.timer.stop()
        self.timer_corriendo = False
        
        if self.cuarto_actual < 4:  
            self.cuarto_actual += 1
            self.actualizar_indicador_cuarto()
            
            self.minutos = 10
            self.segundos = 0
            self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")

            QMessageBox.information(self, "Cambio de Cuarto", 
                                f"¡Ha terminado el cuarto {self.cuarto_actual}!\nIniciando cuarto {self.cuarto_actual + 1}")
        else:
            QMessageBox.information(self, "Partido Terminado", 
                                "¡El partido ha concluido!")

    def actualizar_indicador_cuarto(self):
        nombres_cuartos = ["1°C", "2°C", "3°C", "4°C", "T.E."]
        if self.cuarto_actual < len(nombres_cuartos):
            self.label_cuarto_actual.setText(nombres_cuartos[self.cuarto_actual])

    def iniciar_cronometro(self):
        if not self.timer_corriendo:
            self.timer.start()
            self.timer_corriendo = True

    def pausar_cronometro(self):
        self.timer.stop()
        self.timer_corriendo = False

    def reiniciar_cronometro(self):
        self.timer.stop()
        self.minutos = 10
        self.segundos = 0
        self.timer_corriendo = False
        self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")

    def sumar_minuto(self):
        self.minutos += 1
        self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")

    def restar_minuto(self):
        self.minutos = max(self.minutos - 1, 0)
        self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())