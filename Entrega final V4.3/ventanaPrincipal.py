import sys
import os
from nba_extractor import NBADataExtractor
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QAction, QDesktopWidget, QTableWidget, QLineEdit,
    QCheckBox, QGroupBox, QTabWidget, QTextEdit, QComboBox, QMessageBox,
    QHeaderView, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont


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
    """QLabel personalizado para mostrar logos de equipos"""
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
        """Mostrar un placeholder cuando no hay logo"""
        self.setText("🏀")
        self.setStyleSheet("font-size: 60px; background-color: rgba(255,255,255,150); border-radius: 10px;")


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Planilla NBA-FIBA")
        # Centrar ventana en pantalla
        self.resize(1600, 900)
        self.centrar_ventana()
        
        # Establecer el icono de la ventana
        self.setWindowIcon(self.cargar_icono("imagenes/icono.png"))

        # ESTILO PARA LA BARRA DE TÍTULO - NEGRA CON LETRAS ROJAS
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

        # Marcadores por cuarto
        self.puntos_local = [0, 0, 0, 0, 0]  # [1C, 2C, 3C, 4C, TE]
        self.puntos_visitante = [0, 0, 0, 0, 0]
        self.marcador_local = 0
        self.marcador_visitante = 0
        
        # Control de cuarto actual
        self.cuarto_actual = 0  # 0: 1°C, 1: 2°C, 2: 3°C, 3: 4°C, 4: TE
        
        # Faltas
        self.faltas_local = 0
        self.faltas_visitante = 0

        # Cronómetro
        self.minutos = 10
        self.segundos = 0
        self.timer_corriendo = False
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.actualizar_cronometro)

        # Barra de menú
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

        # Pestañas
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.pestaña_principal = self.crear_pestaña_principal()
        self.tab_widget.addTab(self.pestaña_principal, "Planilla y Tablero")

        self.pestaña_estadisticas = self.crear_pantalla_estadisticas()
        self.tab_widget.addTab(self.pestaña_estadisticas, "Estadísticas de Jugadores")

        self.cargar_equipos()

    def centrar_ventana(self):
        """Centrar la ventana en la pantalla"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def cargar_icono(self, ruta_icono):
        """Método auxiliar para cargar íconos con manejo de errores"""
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
            # Crear un ícono simple como fallback
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

    # -------------------------------
    # Pantalla principal
    # -------------------------------
    def crear_pestaña_principal(self):
        widget = QWidget()
        layout_principal = QHBoxLayout(widget)

        # -------------------------------
        # Lado izquierdo: equipos y planillas (75%)
        # -------------------------------
        lado_izquierdo = QVBoxLayout()

        # Equipo Local
        grupo_local = QGroupBox("Equipo Local")
        layout_local = QVBoxLayout(grupo_local)
        
        # Layout superior para logo y combobox
        layout_superior_local = QHBoxLayout()
        
        # Logo del equipo local (lado izquierdo)
        self.logo_local_izquierdo = LogoLabel()
        self.logo_local_izquierdo.setFixedSize(60, 60)  # Más pequeño en el lado izquierdo
        layout_superior_local.addWidget(self.logo_local_izquierdo)
        
        # Combobox para equipo local
        self.nombre_local_cb = QComboBox()
        self.nombre_local_cb.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.nombre_local_cb.currentIndexChanged.connect(self.actualizar_tablero)
        layout_superior_local.addWidget(self.nombre_local_cb)
        
        layout_local.addLayout(layout_superior_local)

        # --- Tiempo Muerto Local Compacto y Alineado ---
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

        # Planilla local
        self.tabla_local = self.crear_planilla_equipo("local")
        layout_local.addWidget(self.tabla_local)
        lado_izquierdo.addWidget(grupo_local)

        # Equipo Visitante
        grupo_visitante = QGroupBox("Equipo Visitante")
        layout_visitante = QVBoxLayout(grupo_visitante)
        
        # Layout superior para logo y combobox
        layout_superior_visitante = QHBoxLayout()
        
        # Logo del equipo visitante (lado izquierdo)
        self.logo_visitante_izquierdo = LogoLabel()
        self.logo_visitante_izquierdo.setFixedSize(60, 60)  # Más pequeño en el lado izquierdo
        layout_superior_visitante.addWidget(self.logo_visitante_izquierdo)
        
        # Combobox para equipo visitante
        self.nombre_visitante_cb = QComboBox()
        self.nombre_visitante_cb.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.nombre_visitante_cb.currentIndexChanged.connect(self.actualizar_tablero)
        layout_superior_visitante.addWidget(self.nombre_visitante_cb)
        
        layout_visitante.addLayout(layout_superior_visitante)

        # --- Tiempo Muerto Visitante Compacto y Alineado ---
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

        # Planilla visitante
        self.tabla_visitante = self.crear_planilla_equipo("visitante")
        layout_visitante.addWidget(self.tabla_visitante)
        lado_izquierdo.addWidget(grupo_visitante)

        layout_principal.addLayout(lado_izquierdo, 75)  # 75% del espacio

        # -------------------------------
        # Lado derecho: tablero virtual (25%) - TODO EN ROJO
        # -------------------------------
        lado_derecho_widget = BackgroundWidget("imagenes/fondo.png")
        lado_derecho = QVBoxLayout(lado_derecho_widget)
        
        # =======================
        # SECCIÓN SUPERIOR: TIEMPO - TODO ROJO
        # =======================
        grupo_tiempo = QGroupBox("TIEMPO")
        grupo_tiempo.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: red; }")
        layout_tiempo = QVBoxLayout(grupo_tiempo)
        
        # Cronómetro principal - MÁS GRANDE Y ROJO
        self.label_cronometro = QLabel(f"{self.minutos:02d}:{self.segundos:02d}")
        self.label_cronometro.setAlignment(Qt.AlignCenter)
        self.label_cronometro.setStyleSheet("font-size: 64px; font-weight: bold; color: red; margin: 15px;")
        layout_tiempo.addWidget(self.label_cronometro)
        
        # Indicador de cuarto actual - ROJO
        self.label_cuarto_actual = QLabel("1°C")
        self.label_cuarto_actual.setAlignment(Qt.AlignCenter)
        self.label_cuarto_actual.setStyleSheet("font-size: 20px; font-weight: bold; color: red; background-color: rgba(255,255,255,150); padding: 5px; border-radius: 5px;")
        layout_tiempo.addWidget(self.label_cuarto_actual)
        
        # Botones del cronómetro
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
        
        # Faltas debajo del tiempo - ROJO
        layout_faltas = QHBoxLayout()
        
        self.label_faltas_local = QLabel(f"F. Local: {self.faltas_local}/5")
        self.label_faltas_local.setAlignment(Qt.AlignCenter)
        self.label_faltas_local.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(255,255,255,150); padding: 5px; border-radius: 5px;")
        layout_faltas.addWidget(self.label_faltas_local)
        
        self.label_faltas_visitante = QLabel(f"F. Visitante: {self.faltas_visitante}/5")
        self.label_faltas_visitante.setAlignment(Qt.AlignCenter)
        self.label_faltas_visitante.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(255,255,255,150); padding: 5px; border-radius: 5px;")
        layout_faltas.addWidget(self.label_faltas_visitante)
        
        layout_tiempo.addLayout(layout_faltas)
        
        lado_derecho.addWidget(grupo_tiempo)
        
        # =============================
        # SECCIÓN INFERIOR: PUNTUACIONES - TODO ROJO
        # =============================
        grupo_puntuaciones = QGroupBox("PUNTUACIÓN POR CUARTO")
        grupo_puntuaciones.setStyleSheet("QGroupBox { font-weight: bold; font-size: 16px; color: red; }")
        layout_puntuaciones = QGridLayout(grupo_puntuaciones)
        
        # Configurar columnas
        layout_puntuaciones.setColumnStretch(0, 2)
        layout_puntuaciones.setColumnStretch(1, 3)
        layout_puntuaciones.setColumnStretch(2, 3)
        
        # Encabezados con LOGOS
        layout_puntuaciones.addWidget(QLabel(""), 0, 0)
        
        # Logo del equipo local (lado derecho)
        self.logo_local_derecho = LogoLabel()
        self.logo_local_derecho.setFixedSize(150, 150)
        layout_puntuaciones.addWidget(self.logo_local_derecho, 0, 1)
        
        # Logo del equipo visitante (lado derecho)
        self.logo_visitante_derecho = LogoLabel()
        self.logo_visitante_derecho.setFixedSize(150, 150)
        layout_puntuaciones.addWidget(self.logo_visitante_derecho, 0, 2)
        
        # Filas para cada cuarto - TODO ROJO
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
            # Etiqueta del cuarto - ROJO
            lbl_cuarto = QLabel(nombre_cuarto)
            lbl_cuarto.setStyleSheet("font-weight: bold; font-size: 12px; color: red; background-color: rgba(255,255,255,150); padding: 8px; margin: 2px; border-radius: 5px;")
            lbl_cuarto.setAlignment(Qt.AlignCenter)
            lbl_cuarto.setMinimumWidth(80)
            layout_puntuaciones.addWidget(lbl_cuarto, fila, 0)
            
            # Puntos local - ROJO
            lbl_puntos_local = QLabel("0")
            lbl_puntos_local.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(173,216,230,150); padding: 10px; margin: 2px; border-radius: 5px;")
            lbl_puntos_local.setAlignment(Qt.AlignCenter)
            layout_puntuaciones.addWidget(lbl_puntos_local, fila, 1)
            self.labels_puntos_local.append(lbl_puntos_local)
            
            # Puntos visitante - ROJO
            lbl_puntos_visitante = QLabel("0")
            lbl_puntos_visitante.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: rgba(255,182,193,150); padding: 10px; margin: 2px; border-radius: 5px;")
            lbl_puntos_visitante.setAlignment(Qt.AlignCenter)
            layout_puntuaciones.addWidget(lbl_puntos_visitante, fila, 2)
            self.labels_puntos_visitante.append(lbl_puntos_visitante)
        
        # TOTAL - ROJO
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
        layout_principal.addWidget(lado_derecho_widget, 25)  # 25% del espacio

        return widget

    # -------------------------------
    # Planilla de jugadores con TAP y porcentajes
    # -------------------------------
    def crear_planilla_equipo(self, equipo="local"):
        # Columnas actualizadas: AST, REB, PER, ROB, TAP + porcentajes
        tabla = QTableWidget(15, 21)  # Más columnas para TAP y porcentajes
        tabla.setHorizontalHeaderLabels([
            "N°", "Jugador", "F1", "F2", "F3", "F4", "F5", 
            "1P✓", "1P✗", "2P✓", "2P✗", "3P✓", "3P✗",
            "AST", "REB", "PER", "ROB", "TAP",  # Agregada TAP
            "%1P", "%2P", "%3P"  # Porcentajes al final
        ])
        
        # Configurar anchos de columnas
        tabla.setColumnWidth(0, 40)   # N°
        tabla.setColumnWidth(1, 120)  # Jugador
        for col in range(2, 7):       # Faltas F1-F5
            tabla.setColumnWidth(col, 30)
        for col in range(7, 13):      # Sistema de puntos
            tabla.setColumnWidth(col, 40)
        for col in range(13, 18):     # Estadísticas AST, REB, PER, ROB, TAP
            tabla.setColumnWidth(col, 45)
        for col in range(18, 21):     # Porcentajes
            tabla.setColumnWidth(col, 50)
        
        # Aumentar el alto de las filas
        tabla.verticalHeader().setDefaultSectionSize(60)
        
        # Tamaño de íconos para los botones de puntos
        icon_size = QSize(25, 25)
        
        for fila in range(15):
            # Columna 0: Número de jugador
            tabla.setCellWidget(fila, 0, QLineEdit())
            
            # Columna 1: Nombre de jugador
            tabla.setCellWidget(fila, 1, QLineEdit())
            
            # Columnas 2-6: Faltas (F1-F5) con control secuencial
            checkboxes_faltas = []
            for col in range(2, 7):
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left:0px; margin-right:0px;")
                checkbox.stateChanged.connect(partial(self.controlar_faltas_secuencial, fila, col-2, tabla, equipo))
                tabla.setCellWidget(fila, col, checkbox)
                checkboxes_faltas.append(checkbox)
            
            # Columnas 7-12: Sistema de puntos con botones de pelotas
            # 1 Punto - Check y Cruz
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
            
            # 2 Puntos - Check y Cruz
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
            
            # 3 Puntos - Check y Cruz
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
            
            # Columnas 13-17: Estadísticas AST, REB, PER, ROB, TAP
            # Asistencias (AST)
            tabla.setCellWidget(fila, 13, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 13, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 13, -1, equipo)))
            
            # Rebotes (REB)
            tabla.setCellWidget(fila, 14, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 14, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 14, -1, equipo)))
            
            # Pérdidas (PER)
            tabla.setCellWidget(fila, 15, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 15, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 15, -1, equipo)))
            
            # Robos (ROB)
            tabla.setCellWidget(fila, 16, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 16, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 16, -1, equipo)))
            
            # Tapas (TAP) - NUEVA COLUMNA
            tabla.setCellWidget(fila, 17, self.crear_celda_contador(0, partial(self.actualizar_estadistica, fila, 17, 1, equipo), 
                                                                   partial(self.actualizar_estadistica, fila, 17, -1, equipo)))
            
            # Columnas 18-20: Porcentajes de tiros (%1P, %2P, %3P)
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
        """Controlar que las faltas se marquen en orden secuencial"""
        if estado == Qt.Checked:
            # Verificar que todas las faltas anteriores estén marcadas
            for i in range(indice_falta):
                checkbox_anterior = tabla.cellWidget(fila, 2 + i)
                if isinstance(checkbox_anterior, QCheckBox) and not checkbox_anterior.isChecked():
                    # Si una falta anterior no está marcada, desmarcar esta
                    checkbox_actual = tabla.cellWidget(fila, 2 + indice_falta)
                    if isinstance(checkbox_actual, QCheckBox):
                        checkbox_actual.setChecked(False)
                        QMessageBox.warning(self, "Faltas Secuenciales", 
                                          "Debes marcar las faltas en orden. Primero marca la falta 1, luego la 2, etc.")
                    return
        
        # Si se desmarca una falta, desmarcar todas las siguientes
        if estado == Qt.Unchecked:
            for i in range(indice_falta + 1, 5):  # 5 faltas totales (0-4)
                checkbox_siguiente = tabla.cellWidget(fila, 2 + i)
                if isinstance(checkbox_siguiente, QCheckBox) and checkbox_siguiente.isChecked():
                    checkbox_siguiente.setChecked(False)
        
        # Actualizar el contador de faltas totales
        self.verificar_faltas(fila, tabla, equipo)

    def crear_celda_contador(self, valor_inicial, funcion_mas, funcion_menos):
        """Crear una celda con contador funcional"""
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
        """Actualizar las estadísticas AST, REB, PER, ROB, TAP"""
        if equipo == "local":
            tabla = self.tabla_local
        else:
            tabla = self.tabla_visitante
        
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
        """Método para manejar los puntos de cada jugador"""
        # Actualizar porcentajes (columnas 18-20)
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
        
        # Sumar puntos al marcador si encestó
        if encesto:
            # Usar el cuarto actual
            if equipo == "local":
                self.puntos_local[self.cuarto_actual] += puntos
                self.labels_puntos_local[self.cuarto_actual].setText(str(self.puntos_local[self.cuarto_actual]))
            else:
                self.puntos_visitante[self.cuarto_actual] += puntos
                self.labels_puntos_visitante[self.cuarto_actual].setText(str(self.puntos_visitante[self.cuarto_actual]))
            
            self.actualizar_totales()

    def actualizar_totales(self):
        """Actualizar los totales de ambos equipos"""
        total_local = sum(self.puntos_local)
        total_visitante = sum(self.puntos_visitante)
        
        self.label_total_local.setText(str(total_local))
        self.label_total_visitante.setText(str(total_visitante))

    def crear_pantalla_estadisticas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        titulo = QLabel("Estadísticas de Jugadores")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(titulo)

        self.area_estadisticas = QTextEdit()
        self.area_estadisticas.setReadOnly(True)
        self.area_estadisticas.setText("En este Q text edit voy a probar meter datos de la api")
        layout.addWidget(self.area_estadisticas)
        
        btn_actualizar = QPushButton("Actualizar Estadísticas (Simulado)")
        layout.addWidget(btn_actualizar)

        return widget
    
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
        """Limpiar todos los datos de una tabla de equipo"""
        for fila in range(tabla.rowCount()):
            # Limpiar número de jugador
            numero_widget = tabla.cellWidget(fila, 0)
            if isinstance(numero_widget, QLineEdit):
                numero_widget.setText("")
            
            # Limpiar nombre de jugador
            nombre_widget = tabla.cellWidget(fila, 1)
            if isinstance(nombre_widget, QLineEdit):
                nombre_widget.setText("")
            
            # Limpiar checkboxes de faltas
            for col in range(2, 7):
                checkbox = tabla.cellWidget(fila, col)
                if isinstance(checkbox, QCheckBox):
                    checkbox.setChecked(False)
                    checkbox.setStyleSheet("margin-left:0px; margin-right:0px;")
                    checkbox.setEnabled(True)
            
            # Resetear contadores de estadísticas (incluyendo TAP)
            for col in range(13, 18):  # AST, REB, PER, ROB, TAP
                celda_widget = tabla.cellWidget(fila, col)
                if celda_widget:
                    for i in range(celda_widget.layout().count()):
                        widget = celda_widget.layout().itemAt(i).widget()
                        if isinstance(widget, QLabel):
                            widget.setText("0")
                            break
            
            # Resetear porcentajes
            for col in range(18, 21):  # %1P, %2P, %3P
                label = tabla.cellWidget(fila, col)
                if isinstance(label, QLabel):
                    label.setText("0/0")
    
    # -------------------------------
    # Faltas
    # -------------------------------
    def verificar_faltas(self, fila, tabla, equipo):
        contador = sum(1 for col in range(2,7) if isinstance(tabla.cellWidget(fila,col), QCheckBox) and tabla.cellWidget(fila,col).isChecked())
        if contador <= 2:
            color = "background-color: lightgreen"
        elif contador <= 4:
            color = "background-color: yellow"
        else:
            color = "background-color: red"
        for col in range(2,7):
            checkbox = tabla.cellWidget(fila,col)
            if isinstance(checkbox, QCheckBox):
                checkbox.setStyleSheet(f"margin-left:0px; margin-right:0px; {color}")
                checkbox.setEnabled(contador<5 or checkbox.isChecked())
        self.actualizar_faltas_totales(equipo)

    def actualizar_faltas_totales(self, equipo):
        tabla = self.tabla_local if equipo=="local" else self.tabla_visitante
        total = 0
        for fila in range(15):
            for col in range(2,7):
                widget = tabla.cellWidget(fila, col)
                if isinstance(widget, QCheckBox) and widget.isChecked():
                    total += 1
        total = min(total, 5)
        nombre_local_cb = self.nombre_local_cb.currentText()
        nombre_visitante_cb = self.nombre_visitante_cb.currentText()
        if equipo=="local":
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

    # -------------------------------
    # Marcador
    # -------------------------------
    def actualizar_tablero(self):
        nombre_local_cb = self.nombre_local_cb.currentText()
        nombre_visitante_cb = self.nombre_visitante_cb.currentText()
        self.label_faltas_local.setText(f"F. Local: {self.faltas_local}/5")
        self.label_faltas_visitante.setText(f"F. Visitante: {self.faltas_visitante}/5")
   
    # -------------------------------
    # Cronómetro y control de cuartos
    # -------------------------------
    def actualizar_cronometro(self):
        if self.segundos == 0:
            if self.minutos == 0:
                # Tiempo terminado - avanzar al siguiente cuarto
                self.avanzar_cuarto()
                return
            else:
                self.minutos -= 1
                self.segundos = 59
        else:
            self.segundos -= 1
        self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")

    def avanzar_cuarto(self):
        """Avanzar al siguiente cuarto cuando el tiempo termina"""
        self.timer.stop()
        self.timer_corriendo = False
        
        # Solo avanzar si no estamos en tiempo extra
        if self.cuarto_actual < 4:  # 0-3 son cuartos normales, 4 es tiempo extra
            self.cuarto_actual += 1
            self.actualizar_indicador_cuarto()
            
            # Reiniciar el cronómetro para el nuevo cuarto
            self.minutos = 10
            self.segundos = 0
            self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")
            
            # RESETEAR FALTAS al cambiar de cuarto
            self.resetear_faltas_totales()
            
            # Mostrar mensaje informativo
            QMessageBox.information(self, "Cambio de Cuarto", 
                                  f"¡Ha terminado el cuarto {self.cuarto_actual}!\nIniciando cuarto {self.cuarto_actual + 1}")
        else:
            # Si estamos en tiempo extra, solo parar el cronómetro
            QMessageBox.information(self, "Partido Terminado", 
                                  "¡El partido ha concluido!")

    def actualizar_indicador_cuarto(self):
        """Actualizar el indicador del cuarto actual"""
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