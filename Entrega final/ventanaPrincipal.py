import sys
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QAction, QDesktopWidget,
    QTableWidget, QLineEdit, QCheckBox, QGroupBox, QTabWidget,
    QTextEdit
)
from PyQt5.QtCore import Qt, QTimer

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Planilla NBA-FIBA")
        self.resize(1400, 900)
        self.centrar_ventana()

        # Marcadores y faltas
        self.marcador_local = 0
        self.marcador_visitante = 0
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
        menu_archivo = barra_menu.addMenu("Archivo")
        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.close)
        menu_archivo.addAction(accion_salir)

        # Pestañas
        self.tab_widget = QTabWidget() 
        self.setCentralWidget(self.tab_widget)

        self.pestaña_principal = self.crear_pestaña_principal()
        self.tab_widget.addTab(self.pantalla_principal, "Planilla y Tablero")

        self.pestaña_estadisticas = self.crear_pantalla_estadisticas()
        self.tab_widget.addTab(self.pantalla_estadisticas, "Estadísticas de Jugadores")

    # -------------------------------
    # Pantalla principal
    # -------------------------------
    def crear_pestaña_principal(self):
        widget = QWidget()
        layout_principal = QHBoxLayout(widget)

        # -------------------------------
        # Lado izquierdo: equipos y planillas
        # -------------------------------
        lado_izquierdo = QVBoxLayout()

        # Equipo Local
        grupo_local = QGroupBox("Equipo Local")
        layout_local = QVBoxLayout(grupo_local)
        self.nombre_local = QLineEdit("Equipo Local")
        self.nombre_local.setAlignment(Qt.AlignCenter)
        self.nombre_local.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout_local.addWidget(self.nombre_local)

        # --- Tiempo Muerto Local Compacto y Alineado ---
        grupo_tm_local = QGroupBox("Tiempo Muerto")
        layout_tm_local = QVBoxLayout(grupo_tm_local)
        layout_tm_local.setContentsMargins(2,2,2,2)
        layout_tm_local.setSpacing(2)

        # Función auxiliar para fila de Tiempo Muerto
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
        self.nombre_visitante = QLineEdit("Equipo Visitante")
        self.nombre_visitante.setAlignment(Qt.AlignCenter)
        self.nombre_visitante.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout_visitante.addWidget(self.nombre_visitante)

        # --- Tiempo Muerto Visitante Compacto y Alineado ---
        grupo_tm_visitante = QGroupBox("Tiempo Muerto")
        layout_tm_visitante = QVBoxLayout(grupo_tm_visitante)
        layout_tm_visitante.setContentsMargins(2,2,2,2)
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

        layout_principal.addLayout(lado_izquierdo, 2)

        # -------------------------------
        # Lado derecho: tablero virtual
        # -------------------------------
        lado_derecho = QVBoxLayout()

        # Tablero Local
        self.tablero_local = QLabel(f"{self.nombre_local.text()}: {self.marcador_local}")
        self.tablero_local.setAlignment(Qt.AlignCenter)
        self.tablero_local.setStyleSheet(
            "font-size: 48px; font-weight: bold; color: black; padding: 20px;"
        )
        lado_derecho.addWidget(self.tablero_local)

        # Botones marcador local
        botones_local = QHBoxLayout()
        for val in [1,2,3]:
            btn = QPushButton(f"+{val}")
            btn.clicked.connect(partial(self.sumar_marcador, "local", val))
            botones_local.addWidget(btn)
        btn_restar_local = QPushButton("-1")
        btn_restar_local.clicked.connect(partial(self.sumar_marcador, "local", -1))
        botones_local.addWidget(btn_restar_local)
        lado_derecho.addLayout(botones_local)

        # Tablero Visitante
        self.tablero_visitante = QLabel(f"{self.nombre_visitante.text()}: {self.marcador_visitante}")
        self.tablero_visitante.setAlignment(Qt.AlignCenter)
        self.tablero_visitante.setStyleSheet(
            "font-size: 48px; font-weight: bold; color: black; padding: 20px;"
        )
        lado_derecho.addWidget(self.tablero_visitante)

        # Botones marcador visitante
        botones_visitante = QHBoxLayout()
        for val in [1,2,3]:
            btn = QPushButton(f"+{val}")
            btn.clicked.connect(partial(self.sumar_marcador, "visitante", val))
            botones_visitante.addWidget(btn)
        btn_restar_visitante = QPushButton("-1")
        btn_restar_visitante.clicked.connect(partial(self.sumar_marcador, "visitante", -1))
        botones_visitante.addWidget(btn_restar_visitante)
        lado_derecho.addLayout(botones_visitante)

        # Cronómetro
        self.label_cronometro = QLabel(f"{self.minutos:02d}:{self.segundos:02d}")
        self.label_cronometro.setAlignment(Qt.AlignCenter)
        self.label_cronometro.setStyleSheet("font-size: 32px; font-weight: bold; margin-top:20px;")
        lado_derecho.addWidget(self.label_cronometro)

        botones_crono = QHBoxLayout()
        btn_iniciar = QPushButton("Comenzar")
        btn_iniciar.clicked.connect(self.iniciar_cronometro)
        botones_crono.addWidget(btn_iniciar)

        btn_pausar = QPushButton("Pausar")
        btn_pausar.clicked.connect(self.pausar_cronometro)
        botones_crono.addWidget(btn_pausar)

        btn_reiniciar = QPushButton("Reiniciar")
        btn_reiniciar.clicked.connect(self.reiniciar_cronometro)
        botones_crono.addWidget(btn_reiniciar)

        btn_sumar_min = QPushButton("+1 Min")
        btn_sumar_min.clicked.connect(self.sumar_minuto)
        botones_crono.addWidget(btn_sumar_min)

        btn_restar_min = QPushButton("-1 Min")
        btn_restar_min.clicked.connect(self.restar_minuto)
        botones_crono.addWidget(btn_restar_min)

        lado_derecho.addLayout(botones_crono)

        # Faltas
        self.label_faltas_local = QLabel(f"Faltas {self.nombre_local.text()}: {self.faltas_local}/5")
        self.label_faltas_local.setAlignment(Qt.AlignCenter)
        self.label_faltas_local.setStyleSheet("font-size: 22px; font-weight: bold;")
        lado_derecho.addWidget(self.label_faltas_local)

        self.label_faltas_visitante = QLabel(f"Faltas {self.nombre_visitante.text()}: {self.faltas_visitante}/5")
        self.label_faltas_visitante.setAlignment(Qt.AlignCenter)
        self.label_faltas_visitante.setStyleSheet("font-size: 22px; font-weight: bold;")
        lado_derecho.addWidget(self.label_faltas_visitante)

        btn_reset_faltas = QPushButton("Resetear Faltas Totales")
        btn_reset_faltas.clicked.connect(self.resetear_faltas_totales)
        lado_derecho.addWidget(btn_reset_faltas)

        lado_derecho.addStretch()
        layout_principal.addLayout(lado_derecho, 1)

        return widget

    # -------------------------------
    # Planilla de jugadores
    # -------------------------------
    def crear_planilla_equipo(self, equipo="local"):
        tabla = QTableWidget(15, 7)
        tabla.setHorizontalHeaderLabels(["N°", "Jugador", "F1", "F2", "F3", "F4", "F5"])
        tabla.setColumnWidth(0, 50)
        tabla.setColumnWidth(1, 200)
        for col in range(2,7):
            tabla.setColumnWidth(col, 35)

        for fila in range(15):
            tabla.setCellWidget(fila, 0, QLineEdit())
            tabla.setCellWidget(fila, 1, QLineEdit())
            for col in range(2,7):
                checkbox = QCheckBox()
                checkbox.setStyleSheet("margin-left:0px; margin-right:0px;")
                checkbox.stateChanged.connect(partial(self.verificar_faltas, fila, tabla, equipo))
                tabla.setCellWidget(fila, col, checkbox)
        return tabla

    def crear_pantalla_estadisticas(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        titulo = QLabel("Estadísticas de Jugadores")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(titulo)
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
        if equipo=="local":
            self.faltas_local = total
            self.label_faltas_local.setText(f"Faltas {self.nombre_local.text()}: {self.faltas_local}/5")
        else:
            self.faltas_visitante = total
            self.label_faltas_visitante.setText(f"Faltas {self.nombre_visitante.text()}: {self.faltas_visitante}/5")

    def resetear_faltas_totales(self):
        self.faltas_local = 0
        self.faltas_visitante = 0
        self.label_faltas_local.setText(f"Faltas {self.nombre_local.text()}: 0/5")
        self.label_faltas_visitante.setText(f"Faltas {self.nombre_visitante.text()}: 0/5")

    # -------------------------------
    # Marcador
    # -------------------------------
    def sumar_marcador(self, equipo, valor):
        if equipo=="local":
            self.marcador_local = max(self.marcador_local + valor, 0)
        else:
            self.marcador_visitante = max(self.marcador_visitante + valor, 0)
        self.actualizar_tablero()

    def actualizar_tablero(self):
        self.tablero_local.setText(f"{self.nombre_local.text()}: {self.marcador_local}")
        self.tablero_visitante.setText(f"{self.nombre_visitante.text()}: {self.marcador_visitante}")
        self.label_faltas_local.setText(f"Faltas {self.nombre_local.text()}: {self.faltas_local}/5")
        self.label_faltas_visitante.setText(f"Faltas {self.nombre_visitante.text()}: {self.faltas_visitante}/5")

    # -------------------------------
    # Cronómetro
    # -------------------------------
    def actualizar_cronometro(self):
        if self.segundos == 0:
            if self.minutos == 0:
                self.timer.stop()
                self.timer_corriendo = False
                return
            else:
                self.minutos -= 1
                self.segundos = 59
        else:
            self.segundos -= 1
        self.label_cronometro.setText(f"{self.minutos:02d}:{self.segundos:02d}")

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

    # -------------------------------
    # Centrar ventana
    # -------------------------------
    def centrar_ventana(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec_())