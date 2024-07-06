#060724.v448 se implementa otra forma no ortodoxa de vincular los cambios del canal seleccionable con los canales individuales
#que corresponda y viceversa, tanto en el volumen de diales y slides como de botones de silencio y aspectos visuales.  depurar +++ codigo!
#050724.v446 se implementa forma no ortodoxa de redibujar la ui ante cambios en la cantidad de fuentes de audio.
#050724.v445 se implementa hoja de estilos para crear diales y sliders de forma personalida y minimalista.
#050724.v445 se ajustan textos de botones ui en funcion de los estados y se implementa una barra de menu.
#040724.v444 se corrigen aspectos viasuales, se centran los controles y se agregan luces de estado.
#040724.v444 se itera sobre una lista de fuentes de sonido para crear los paneles de volumen de cada uno de ellos.
#040724.se implementa actualizacion de fuentes de audio, incluida verificación, mensajes y boton de actualizacion, realizar test qa.
#040724.agrego qdial vinculado al qslider, se vinvulo tecla arriba y abajo para controlar los diales.
#030724.corregido minimas funciones, evaluar.
import sys, os
from functools import partial
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QMessageBox, QMenuBar
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QSlider,  QDial, QAction
from PyQt5.QtCore import Qt, QTimer
import pulsectl
from PyQt5.QtGui import QKeySequence
#para modo oscuro con toda la onda
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette

class VolumenVentana(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        versionado = "v.448.060724"
        self.usdtdir = "0x104948b1A1AaD3437328aDDcc0A2E5A2679D4192" #USDT ADDRESS FOR DONATIONS BEP20, POLYGON OR OPTIMISM NETWORKS

        # Configuración de la ventana UI
        self.setWindowTitle("Control de Volumen "+ versionado)
        self.setMinimumSize(380,640)
        #self.resize(720, 640)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.IconPath = os.path.join(scriptDir, 'icons')   
        self.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))

        # Conexión a PulseAudio
        self.pulse = pulsectl.Pulse('Control de Volumen')
        
        # Obtener lista de aplicaciones
        self.apps = self.pulse.sink_input_list()
        # para debugear
        '''
        print("apps sink_input_list: ", self.apps)
        for app in self.apps:
            print("lista de propiedades de las apps", app.proplist)
        for app in self.apps:
            print(f"Properties for app index {app.index}:")
            for key, value in app.proplist.items():
                print(f"  {key}: {value}")
        '''     
        # Crear una lista desplegable para seleccionar la aplicación
        self.app_selector = QComboBox()
        self.app_selector.addItems([app.proplist.get('application.name', 'Unknown') + " - " + app.proplist.get('media.name', 'Unknown') for app in self.apps])
        self.appfa = [i for i in range(self.app_selector.count())]
        self.appsl = [self.app_selector.itemText(i) for i in range(self.app_selector.count())]
        self.app_selector.currentIndexChanged.connect(self.cambiar_app_select)

        # Inicializar el control de volumen para la primera aplicación
        if self.apps:
            QMessageBox.information(self, f"Fuentes de Audio {versionado}", f"Fuentes de Audio: {self.apps}")
            self.current_app = self.apps[0]
            self.volumen = int(self.current_app.volume.value_flat * 100)
        else:
            self.current_app = None
            self.volumen = 0
            QMessageBox.warning(self, "Sin Fuentes de Audio Detectadas", "No se Detectaron Aplicaciones de Audio Activas. Reproduce Audio para Controlar su Volumen.")
        
        # Creación de etiquetas de volumen
        self.label_fuentes_de_audio = QLabel("Seleccionar Fuente de Audio")

        # Creación del slider vertical de volumen
        self.slider_volumen = QSlider(Qt.Vertical)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setMinimumWidth(100)
        self.slider_volumen.setValue(self.volumen)
        self.slider_estilo_minimalista_on = ("""
            QSlider::groove:vertical {
                background: #f0f0f0;
                width: 40px;
            }
            QSlider::handle:vertical {
                background: #9da9b5;
                border: 1px solid #19232d;
                height: 10px;
                margin: 0 -5px; /* Expand handle width outside the groove */
                border-radius: 4px; /* Half of the width/height to make it circular */
            }
            QSlider::sub-page:vertical {
                background: #455364;
            }
            QSlider::add-page:vertical {
                background: #346792;
            }
            QSlider::tick:vertical {
                background: black; /* Color de los ticks */
                width: 2px;
                height: 2px;
            }
        """)
        self.slider_volumen.setStyleSheet(self.slider_estilo_minimalista_on)

        # Creación suena a Dios y en el principio habia un Slider y vio que quedaba mejor un Dial
        self.dial_volumen = QDial()
        self.dial_volumen.setFixedSize(70,70)
        self.dial_volumen.setRange(0, 100)
        self.dial_volumen.setValue(self.volumen)
        self.dial_estilo_minimalista_on = ("""
            QDial {
                background-color: #346792;
                border: 2px solid #5c5c5c;
                border-radius: 30px; /* Ajusta este valor según el tamaño del dial para hacerlo circular */
            }
            QDial::handle {
                background-color: blue;
                border: 1px solid #5c5c5c;
                width: 16px; /* Ajusta el tamaño del handle */
                height: 16px;
                border-radius: 8px; /* Para hacer el handle circular */
                margin: -8px; /* Asegúrate de centrar el handle */
            }
            QDial::groove {
                background: green;
                border: 1px solid #5c5c5c;
                border-radius: 30px; /* Ajusta este valor según el tamaño del dial para hacerlo circular */
            }
            QDial::chunk {
                background: red;
                border-radius: 30px; /* Ajusta este valor según el tamaño del dial para hacerlo circular */
            }
        """)
        self.slider_estilo_minimalista_off = ("""
            QSlider::groove:vertical {
                background: #f0f0f0;
                width: 40px;
            }
            QSlider::handle:vertical {
                background: #455364;
                border: 1px solid #5c5c5c;
                height: 10px;
                margin: 0 -5px; /* Expand handle width outside the groove */
                border-radius: 4px; /* Half of the width/height to make it circular */
            }
            QSlider::sub-page:vertical {
                background: #455364;
            }
            QSlider::add-page:vertical {
                background: #455364;
            }
            QSlider::tick:vertical {
                background: black; /* Color de los ticks */
                width: 2px;
                height: 2px;
            }
        """)

        self.dial_volumen.setStyleSheet(self.dial_estilo_minimalista_on)

        # Creación de la etiqueta de fuente y volumen
        self.label_fuente_audio_selec = QLabel(f"Index: {self.current_app.index}, Fuente de Audio: {self.current_app.name}")
        self.label_volumen = QLabel(f"Volumen: {self.slider_volumen.value()}")

        # Botón de silencio
        self.btn_mute_audio = QPushButton("Silencio")
        self.btn_mute_audio.setCheckable(True)
        self.btn_mute_audio.setStyleSheet("color: black; background-color: lightgray;")
        self.btn_mute_audio.clicked.connect(self.mutefun)

        # Botón Actuzalizar Fuentes de Audio
        self.btn_act_faudio = QPushButton("Actualizar Fuentes de Audio")
        self.btn_act_faudio.clicked.connect(self.actualizar_fuentes_audio)

        # Conexión de la señal de valor cambiado a la función de actualización de volumen
        self.slider_volumen.valueChanged.connect(lambda: self.actualizar_volumen('slider'))
        self.dial_volumen.valueChanged.connect(lambda: self.actualizar_volumen('dial'))

        self.crear_barra_menu()

        # Diseño de la interfaz de usuario mediante QWidget y Layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.btn_act_faudio)

        # nivel panel horizontal para los canales de fuente de audio
        self.panel_layout = QHBoxLayout()

        # seleccion de fuente de audio layout
        self.fuenteselec_layout = QVBoxLayout()
        self.fuenteselec_layout.addWidget(self.label_fuentes_de_audio)
        self.fuenteselec_layout.addWidget(self.app_selector)
        
        # crea nivel donde habita el pote con fuente de audio seleccionable
        potes_widget = QWidget()
        potes_widget.setMinimumWidth(200)
        potes_widget.setMaximumWidth(250)
        potes_widget.setStyleSheet(f"background-color: {'#455364'};")
        potes_layout = QVBoxLayout(potes_widget)
        potes_layout.addLayout(self.fuenteselec_layout)

        # para centrar dial y slider
        dial_layout = QHBoxLayout()
        spacer_left_dial = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right_dial = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        dial_layout.addItem(spacer_left_dial)
        dial_layout.addWidget(self.dial_volumen)
        dial_layout.addItem(spacer_right_dial)
        
        slider_layout = QHBoxLayout()
        spacer_left_slider = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right_slider = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        slider_layout.addItem(spacer_left_slider)
        slider_layout.addWidget(self.slider_volumen)
        slider_layout.addItem(spacer_right_slider)

        potes_layout.addLayout(dial_layout)
        potes_layout.addLayout(slider_layout)
        potes_layout.addWidget(self.label_fuente_audio_selec)
        potes_layout.addWidget(self.label_volumen)
        potes_layout.addWidget(self.btn_mute_audio)

        self.panel_layout.addWidget(potes_widget)

        # Crea paneles de audio para cada fuente de audio disponible
        self.panel_widget = {}
        self.canal_layout = {}
        self.lbl_canal_layout = {}
        self.lbl_canal_sup1 = {}
        self.lbl_canal_sup2 = {}
        self.fuente_audio = {}
        self.dial_canal = {}
        self.slide_canal = {}
        self.volumen_canal = {}
        self.lbl_volumen_canal = {}
        self.btn_mute_canal = {}

        for appfa in self.appfa:
            colors = ['#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#FFCCFF', '#CCFFFF']  # Colores para los paneles
            self.panel_widget[appfa] = self.crear_panel_de_audio(appfa, colors[appfa % len(colors)])
            self.panel_layout.addWidget(self.panel_widget[appfa])
        
        main_layout.addLayout(self.panel_layout)

        # Shortcuts for increasing and decreasing the value
        self.increase_shortcut = QShortcut(QKeySequence("Up"), self)
        self.increase_shortcut.activated.connect(self.increaseValue)

        self.decrease_shortcut = QShortcut(QKeySequence("Down"), self)
        self.decrease_shortcut.activated.connect(self.decreaseValue)

        # Actualizar dinamicamente la lista de fuentes de audio cada 5 segundos 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_dinamicamente_fuentes_audio)
        self.timer.start(5000)

    def crear_panel_de_audio(self, appfa, color):
        """ Crea un panel de audio 

        Args:
            appfa (_type_): indice de la fuente de audio
            color (_type_): color de fondo del panel

        Returns:
            retorna un widget que contine un conjunto de layouts
            con los elementos del panel de audio
        """
        current_app = self.apps[appfa]
        self.volumen_canal[appfa] = int(current_app.volume.value_flat * 100)

        # Crea un widget para el panel de la fuente de audio
        self.panel_widget[appfa] = QWidget()
        self.panel_widget[appfa].setMaximumWidth(150)
        self.panel_widget[appfa].setStyleSheet(f"background-color: {color};")
        self.canal_layout[appfa] = QVBoxLayout(self.panel_widget[appfa])
        self.lbl_canal_layout[appfa] = QVBoxLayout()

        self.lbl_canal_sup1[appfa] = QLabel("",self)
        self.lbl_canal_sup1[appfa].setFixedSize(30,30)
        self.lbl_canal_sup1[appfa].setText("")
        self.lbl_canal_sup1[appfa].setStyleSheet("color: black; background-color: lightgreen;")

        self.lbl_canal_sup2[appfa] = QLabel("",self)
        self.lbl_canal_sup2[appfa].setText(self.appsl[appfa])
        self.lbl_canal_sup2[appfa].setStyleSheet("color: black")

        self.lbl_canal_layout[appfa].addWidget(self.lbl_canal_sup1[appfa])
        self.lbl_canal_layout[appfa].addWidget(self.lbl_canal_sup2[appfa])

        self.fuente_audio[appfa] = QLabel("fuente de audio",self)
        self.fuente_audio[appfa].setText("Index: "+ str(appfa))
        self.fuente_audio[appfa].setStyleSheet("color: black;")
            
        self.dial_canal[appfa] = QDial()
        self.dial_canal[appfa].setFixedSize(70,70)
        self.dial_canal[appfa].setStyleSheet(self.dial_estilo_minimalista_on)
        self.dial_canal[appfa].setValue(self.volumen_canal[appfa])
            
        self.slide_canal[appfa] = QSlider(Qt.Vertical)
        self.slide_canal[appfa].setMinimumWidth(100)
        self.slide_canal[appfa].setStyleSheet(self.slider_estilo_minimalista_on)
        self.slide_canal[appfa].setValue(self.volumen_canal[appfa])

        # Conexión de la señal de valor cambiado a la función de actualización de volumen
        self.dial_canal[appfa].valueChanged.connect(partial(self.actualizar_volumen_canal, 'dial', appfa))
        self.slide_canal[appfa].valueChanged.connect(partial(self.actualizar_volumen_canal, 'slider', appfa))
            
        self.lbl_volumen_canal[appfa] = QLabel(f"Volumen: {self.dial_canal[appfa].value()}")
        self.lbl_volumen_canal[appfa].setStyleSheet("color: black;")
        self.btn_mute_canal[appfa] = QPushButton("Silenciar")
        self.btn_mute_canal[appfa].setCheckable(True)
        self.btn_mute_canal[appfa].setStyleSheet("color: black; background-color: lightgray;")
        self.btn_mute_canal[appfa].clicked.connect(partial(self.mutefun_canal, appfa))

        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        dial_layout_centering = QHBoxLayout()
        dial_layout_centering.addItem(spacer)
        dial_layout_centering.addWidget(self.dial_canal[appfa])
        dial_layout_centering.addItem(spacer)
        slide_layout_centering = QHBoxLayout()
        slide_layout_centering.addItem(spacer)
        slide_layout_centering.addWidget(self.slide_canal[appfa])
        slide_layout_centering.addItem(spacer)

        self.canal_layout[appfa].addLayout(self.lbl_canal_layout[appfa])
        self.canal_layout[appfa].addLayout(dial_layout_centering)
        self.canal_layout[appfa].addLayout(slide_layout_centering)
        self.canal_layout[appfa].addWidget(self.fuente_audio[appfa])
        self.canal_layout[appfa].addWidget(self.lbl_volumen_canal[appfa])
        self.canal_layout[appfa].addWidget(self.btn_mute_canal[appfa])

        return self.panel_widget[appfa]
    
    def crear_barra_menu(self):
        """ Crea la barra de menú. """
        # Barra de menú 
        self.menuBar = QMenuBar(self)   
        self.layout().setMenuBar(self.menuBar)
        # Establecer estilo para la barra de menú
        self.menuBar.setStyleSheet("background-color: black; color: white;") # Ajusta el color de fondo y el color del texto de la barra de menú
        # Menú aplicación
        self.aplicacion = self.menuBar.addMenu('Aplicación')
        self.opcionayuda = QAction('Ayuda', self)
        self.opcionayuda.triggered.connect(self.en_construccion)
        self.aplicacion.addAction(self.opcionayuda)
        self.opciondonar = QAction('Donar', self)
        self.opciondonar.triggered.connect(self.donar)
        self.aplicacion.addAction(self.opciondonar)
        self.opcionreiniciar = QAction('Reiniciar', self)
        self.opcionreiniciar.triggered.connect(self.reiniciar_app)
        self.aplicacion.addAction(self.opcionreiniciar)
        self.opcionsalir = QAction('Salir', self)
        self.opcionsalir.triggered.connect(self.salir)
        self.aplicacion.addAction(self.opcionsalir)
        # Menú Configuración
        self.menuConfiguracion = self.menuBar.addMenu('Configuración')
           # Opción para configurar las horas de apertura y cierre de cada mercado
        self.opcionHorarios = QAction('Configurar Escala de Volúmen', self)
        self.opcionHorarios.triggered.connect(self.en_construccion)
        self.menuConfiguracion.addAction(self.opcionHorarios)
           # Opción para configurar los colores de los elementos de la aplicación
        self.opcionColores = QAction('Configurar Colores de la Aplicación', self)
        self.opcionColores.triggered.connect(self.en_construccion)
        self.menuConfiguracion.addAction(self.opcionColores)

    def donar(self):
        """ Crea la Ventana de Donación. """
        QMessageBox.information(self, "Donar...", f"""                    Ayude al software libre!!!                          
        
        Apoye a los programadores
        enviando su donación:
            # En Argentina via transferencia bancaria
              por app o billetera virtual al alias:
              buzos.hay.domar.mp
            # En Argentina y Resto del Mundo
              USDT por redes BEP20,  Polygon o Optimism
              {self.usdtdir}

        """)

    def en_construccion(self):
        """ Crea la Ventana que indica que la app esta en construcción. """
        QMessageBox.information(self, "en construcción", f"""                    Paciencia!!!                          
        
        Implementando Metodos y Clases

        """)
    
    def actualizar_volumen_canal(self, origen, appfa):
        """ Actualiza el volumen del canal especifico de entrada de audio
            a la vez copia el valor en el control en tandem en el canal
            especifico y en el canal seleccionable si estuviera seleccionado

        Args:
            origen (_type_): desde donde viene la señal (dial o slider)
            appfa (_type_): indice de la fuente de audio
        """
        if origen == "dial":
            nuevo_valor = self.dial_canal[appfa].value() / 100.0
            self.slide_canal[appfa].setValue(self.dial_canal[appfa].value())
        if origen == "slider":
            nuevo_valor = self.slide_canal[appfa].value() / 100.0
            self.dial_canal[appfa].setValue(self.slide_canal[appfa].value())
        if origen != "selector" and appfa == self.app_selector.currentIndex():
            self.slider_volumen.setValue(self.slide_canal[appfa].value())
            self.dial_volumen.setValue(self.slide_canal[appfa].value())
        if origen == "selector":
            nuevo_valor = self.slider_volumen.value() / 100.0
            self.slide_canal[appfa].setValue(self.slider_volumen.value())
            self.dial_canal[appfa].setValue(self.slider_volumen.value())
        current_volume = self.apps[appfa].volume
        for i in range(len(current_volume.values)):
            current_volume.values[i] = nuevo_valor
        # Aplicar el nuevo volumen
        self.pulse.volume_set(self.apps[appfa], current_volume)
        self.lbl_volumen_canal[appfa].setText(f"Volumen: {int(nuevo_valor * 100)}")

    def actualizar_volumen(self, origen):
        """ Actualiza el volumen del canal seleccionable
        a la vez copia el valor en el control en tandem del
        canal seleccionable y en el canal individual que 
        corresponde a dicha fuente de audio

        Args:
            origen (_type_): de donde viene la señal (dial o slider)
        """
        if origen == "dial":
            nuevo_valor = self.dial_volumen.value() / 100.0
            self.slider_volumen.setValue(self.dial_volumen.value())
        if origen == "slider":
            nuevo_valor = self.slider_volumen.value() / 100.0
            self.dial_volumen.setValue(self.slider_volumen.value())
        # tomo el indice seleccionado para actualizar el canal que corresponda
        appfa = self.app_selector.currentIndex()
        self.actualizar_volumen_canal("selector", appfa)

        current_volume = self.current_app.volume
        # ajusta el volumen en ambos canales de la fuente de audio
        for i in range(len(current_volume.values)):
            current_volume.values[i] = nuevo_valor

        # Aplicar el nuevo volumen
        self.pulse.volume_set(self.current_app, current_volume)
        self.label_volumen.setText(f"Volumen: {int(nuevo_valor * 100)}")

    def mutefun_canal(self, appfa):
        """ Silencia el canal especifico de la fuente de audio
        a su vez modifica los aspectos visuales 

        Args:
            appfa (_type_): indice de la fuente de audio
        """
        if self.btn_mute_canal[appfa].isChecked():
            self.pulse.sink_input_mute(self.apps[appfa].index, 1)
            self.lbl_volumen_canal[appfa].setText("Volumen Silenciado")
            self.lbl_canal_sup1[appfa].setStyleSheet("color: black; background-color: red;")
            self.btn_mute_canal[appfa].setStyleSheet("color: white; background-color: darkgray;")
            self.btn_mute_canal[appfa].setText("Restaurar")
            self.slide_canal[appfa].setStyleSheet(self.slider_estilo_minimalista_off)
            self.slide_canal[appfa].setDisabled(True)
            self.dial_canal[appfa].setDisabled(True)
            self.lbl_volumen_canal[appfa].setDisabled(True)
        else:
            self.pulse.sink_input_mute(self.apps[appfa].index, 0)
            self.lbl_volumen_canal[appfa].setText(f"Volumen: {self.volumen}")
            self.lbl_canal_sup1[appfa].setStyleSheet("color: black; background-color: lightgreen;")
            self.btn_mute_canal[appfa].setStyleSheet("color: black; background-color: lightgray;")
            self.btn_mute_canal[appfa].setText("Silenciar")
            self.slide_canal[appfa].setStyleSheet(self.slider_estilo_minimalista_on)
            self.slide_canal[appfa].setEnabled(True)
            self.dial_canal[appfa].setEnabled(True)
            self.lbl_volumen_canal[appfa].setEnabled(True)
            if appfa == self.app_selector.currentIndex():
                self.btn_mute_audio.setChecked(False)
        if appfa == self.app_selector.currentIndex():
            if self.btn_mute_canal[appfa].isChecked():
                self.btn_mute_audio.setChecked(True)
            else:
                self.btn_mute_audio.setChecked(False)
            self.mutefun("vengodelcanalynoquierofuncionesrecursivas")

    def mutefun(self, cucu):
        """ Silencia el canal seleccionable 
        a la vez modifica los aspectos visuales de dicho canal
        """
        appfa = self.app_selector.currentIndex()
        if self.btn_mute_audio.isChecked():
            self.pulse.sink_input_mute(self.current_app.index, 1)
            self.label_volumen.setText("Volumen Silenciado")
            self.btn_mute_audio.setStyleSheet("color: white; background-color: darkgray;")
            self.btn_mute_audio.setText("Restaurar")
            self.slider_volumen.setStyleSheet(self.slider_estilo_minimalista_off)
            self.slider_volumen.setDisabled(True)
            self.dial_volumen.setDisabled(True)
            self.label_volumen.setDisabled(True)
            self.btn_mute_canal[appfa].setChecked(True)
        else:
            self.pulse.sink_input_mute(self.current_app.index, 0)
            self.label_volumen.setText(f"Volumen: {self.volumen}")
            self.btn_mute_audio.setStyleSheet("color: black; background-color: lightgray;")
            self.btn_mute_audio.setText("Silencio")
            self.slider_volumen.setStyleSheet(self.slider_estilo_minimalista_on)
            self.slider_volumen.setEnabled(True)
            self.dial_volumen.setEnabled(True)
            self.label_volumen.setEnabled(True)
            self.btn_mute_canal[appfa].setChecked(False)
        if cucu != "vengodelcanalynoquierofuncionesrecursivas":
            self.mutefun_canal(appfa)

    def actualizar_dinamicamente_fuentes_audio(self):
        """ Evalua cambios en las fuentes de audio y
        las actualiza dinamicamente... por ahora reiniciando la app 
        """
        self.apps = self.pulse.sink_input_list() 
        #print("len(self.appfa): ",len(self.appfa), "contenido: ",self.appfa)
        #print(" len(self.apps): ",len(self.apps) , "contenido: ",self.apps)
        if len(self.appfa) != len(self.apps):
            QMessageBox.information(self, "Aviso", f""" Se detectaron cambios en las fuentes de audio!
                Se debe reiniciar la applicación
                para conectar controladores
                de sonido en funcion de los
                cambios
                                    
            """)
            self.reiniciar_app()
    
    def actualizar_fuentes_audio(self):
        """ Actualiza las fuentes de audio a pedido 
        al presionar el boton... no tiene mucho sentido ahora
        """
        self.apps = self.pulse.sink_input_list() 
        self.actualizar_dinamicamente_fuentes_audio()
   
    def increaseValue(self):
        """ Sube el volumen al conectar con la tecla arriba. """
        current_value = self.dial_volumen.value()
        if current_value < self.dial_volumen.maximum():
            self.dial_volumen.setValue(current_value + 1)
    
    def decreaseValue(self):
        """ Baja el volumen al conectar con la tecla abajo. """
        current_value = self.dial_volumen.value()
        if current_value > self.dial_volumen.minimum():
            self.dial_volumen.setValue(current_value - 1)

    def cambiar_app_select(self, index):
        """ selecciona al canal la fuente de audio indicada por el combobox

        Args:
            index (_type_): Indice del combobox, mismo de la fuente de audio
        """
        if index < len(self.apps):
            self.current_app = self.apps[index]
            self.volumen = int(self.current_app.volume.value_flat * 100)
            self.slider_volumen.setValue(self.volumen)
            self.label_fuente_audio_selec.setText(f"Index: {self.current_app.index}, Fuente de Audio: {self.current_app.name}")
            self.label_volumen.setText(f"Volumen: {self.volumen}")

    def reiniciar_app(self):
        """Reinicia la Aplicación."""
        # Flush the stdout to ensure all logs are printed before the app restarts
        print("reiniciando")
        sys.stdout.flush()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def salir(self):
        """ Sale de la Aplicación. """
        print("saliendo")
        sys.stdout.flush()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
    #app.setStyleSheet(qdarkstyle.load_stylesheet(LightPalette))
    ventana = VolumenVentana()
    ventana.show()
    sys.exit(app.exec_())
