#040724.v444 se itera sobre una lista de fuentes de sonido para crear los paneles de volumen de cada uno de ellos.
#040724.se implementa actualizacion de fuentes de audio, incluida verificación, mensajes y boton de actualizacion, realizar test qa.
#040724.agrego qdial vinculado al qslider, se vinvulo tecla arriba y abajo para controlar los diales.
#030724.corregido minimas funciones, evaluar.
import sys, os
from functools import partial
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QMessageBox
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QSlider,  QDial
from PyQt5.QtCore import Qt, QTimer
import pulsectl
from PyQt5.QtGui import QKeySequence
#para modo oscuro con toda la onda
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette

class VolumenVentana(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        versionado = "v.444.040724"

        # Configuración de la ventana UI
        self.setWindowTitle("Control de Volumen "+ versionado)
        self.setMinimumSize(720,640)
        #self.resize(720, 640)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        self.IconPath = os.path.join(scriptDir, 'icons')   
        self.setWindowIcon(QtGui.QIcon(self.IconPath + os.path.sep + 'volume.png'))

        # Conexión a PulseAudio
        self.pulse = pulsectl.Pulse('Control de Volumen')
        
        # Obtener lista de aplicaciones
        self.apps = self.pulse.sink_input_list()
        #print("apps sink_input_list: ", self.apps)
        #for app in self.apps:
        #    print("lista de propiedades de las apps", app.proplist)

        for app in self.apps:
            print(f"Properties for app index {app.index}:")
            for key, value in app.proplist.items():
                print(f"  {key}: {value}")
                
        # Crear una lista desplegable para seleccionar la aplicación
        self.app_selector = QComboBox()
        self.app_selector.addItems([app.proplist.get('application.name', 'Unknown') + " - " + app.proplist.get('media.name', 'Unknown') for app in self.apps])
        self.appfa = [i for i in range(self.app_selector.count())] #self.app_selector.itemText(i)
        #self.app_selector.addItems([app.proplist.get('application.name', 'Unknown') for app in self.apps]) #Viejo Metodo
        self.app_selector.currentIndexChanged.connect(self.cambiar_app)

        # Inicializar el control de volumen para la primera aplicación
        if self.apps:
            QMessageBox.information(self, "Fuentes de Audio", f"Fuentes de Audio: {self.apps}")
            self.current_app = self.apps[0]
            self.volumen = int(self.current_app.volume.value_flat * 100)
        else:
            self.current_app = None
            self.volumen = 0
            #QMessageBox.warning(self, "Sin Fuentes de Audio Detectadas", "No se detectaron aplicaciones de Audio activas. Reproduce Audio para controlar el Volumen.")
        
        # Creación de etiquetas de volumen
        self.label_fuentes_de_audio = QLabel("Seleccionar Fuente de Audio")

        # Creación del slider vertical de volumen
        self.slider_volumen = QSlider(Qt.Vertical)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(self.volumen)

        # Creación suena a Dios y en el principio habia un Slider y vio que quedaba mejor un Dial
        self.dial_volumen = QDial()
        self.dial_volumen.setFixedSize(50,50)
        self.dial_volumen.setRange(0, 100)
        self.dial_volumen.setValue(self.volumen)

        # Creación de la etiqueta de fuente y volumen
        print("self.current_app: ",self.current_app)
        self.label_fuente_audio_selec = QLabel(f"Index: {self.current_app.index}, Fuente de Audio: {self.current_app.name}")
        self.label_volumen = QLabel(f"Volumen: {self.slider_volumen.value()}")

        # Botón de silencio
        self.btn_mute_audio = QPushButton("Silencio")
        self.btn_mute_audio.setCheckable(True)
        self.btn_mute_audio.clicked.connect(self.mutefun)

        # Botón Actuzalizar Fuentes de Audio
        self.btn_act_faudio = QPushButton("Actualizar Fuentes de Audio")
        self.btn_act_faudio.clicked.connect(self.actualizar_fuentes_audio)

        # Conexión de la señal de valor cambiado a la función de actualización de volumen
        #self.slider_volumen.valueChanged.connect(self.actualizar_volumen(self,"slider"))
        self.slider_volumen.valueChanged.connect(lambda: self.actualizar_volumen('slider'))
        #self.dial_volumen.valueChanged.connect(self.actualizar_volumen(self,"dial"))
        self.dial_volumen.valueChanged.connect(lambda: self.actualizar_volumen('dial'))

        # Diseño de la interfaz de usuario mediante QWidget y Layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.btn_act_faudio)
        
        # nivel seleccion de fuente de audio layout
        self.fuenteselec_layout = QVBoxLayout()
        self.fuenteselec_layout.addWidget(self.label_fuentes_de_audio)
        self.fuenteselec_layout.addWidget(self.app_selector)
        
        # nivel horizontal para los canales de fuente de audio
        self.panel_layout = QHBoxLayout()
        
        # nivel donde habita el pote seleccionable
        potes_widget = QWidget()
        potes_widget.setMinimumWidth(200)
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

        #self.panel_layout.addLayout(potes_layout)
        self.panel_layout.addWidget(potes_widget)

        # implementacion de canales para cada fuente de audio disponible
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

        colors = ['#FFCCCC', '#CCFFCC', '#CCCCFF', '#FFFFCC', '#FFCCFF', '#CCFFFF']  # Colores para los paneles

        for appfa in self.appfa:
            current_app = self.apps[appfa]
            self.volumen_canal[appfa] = int(current_app.volume.value_flat * 100)

            # Crear un widget para el panel de cada canal de fuente de audio
            panel_widget = QWidget()
            self.canal_layout[appfa] = QVBoxLayout(panel_widget)
            self.lbl_canal_layout[appfa] = QVBoxLayout()

            self.lbl_canal_sup1[appfa] = QLabel("self.lbl_canal_sup1",self)
            self.lbl_canal_sup1[appfa].setText("self.lbl_canal_sup1")
            self.lbl_canal_sup1[appfa].setStyleSheet("color: black;")

            self.lbl_canal_sup2[appfa] = QLabel("self.lbl_canal_sup2",self)
            self.lbl_canal_sup2[appfa].setText("self.lbl_canal_sup2")
            self.lbl_canal_sup2[appfa].setStyleSheet("color: black;")

            self.lbl_canal_layout[appfa].addWidget(self.lbl_canal_sup1[appfa])
            self.lbl_canal_layout[appfa].addWidget(self.lbl_canal_sup2[appfa])

            self.fuente_audio[appfa] = QLabel("fuente de audio",self)
            self.fuente_audio[appfa].setText("Index: "+ str(appfa))
            self.fuente_audio[appfa].setStyleSheet("color: black;")
            
            self.dial_canal[appfa] = QDial()
            self.dial_canal[appfa].setFixedSize(50,50)
            self.dial_canal[appfa].setValue(self.volumen_canal[appfa])
            
            self.slide_canal[appfa] = QSlider(Qt.Vertical)
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

            self.canal_layout[appfa].addLayout(self.lbl_canal_layout[appfa])
            self.canal_layout[appfa].addWidget(self.dial_canal[appfa])
            self.canal_layout[appfa].addWidget(self.slide_canal[appfa])
            self.canal_layout[appfa].addWidget(self.fuente_audio[appfa])
            self.canal_layout[appfa].addWidget(self.lbl_volumen_canal[appfa])
            self.canal_layout[appfa].addWidget(self.btn_mute_canal[appfa])

            # Aplicar color al panel
            panel_widget.setStyleSheet(f"background-color: {colors[appfa % len(colors)]};")

            self.panel_layout.addWidget(panel_widget)

        main_layout.addLayout(self.panel_layout)
        
        # Shortcuts for increasing and decreasing the value
        self.increase_shortcut = QShortcut(QKeySequence("Up"), self)
        self.increase_shortcut.activated.connect(self.increaseValue)

        self.decrease_shortcut = QShortcut(QKeySequence("Down"), self)
        self.decrease_shortcut.activated.connect(self.decreaseValue)

        # Actualizar la lista de fuentes de audio cada 10 segundos, no tiene sentido 040724
        '''
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_fuentes_audio)
        self.timer.start(10000)
        '''

        # Actualizar la interfaz en inicio
        self.actualizar_interfaz()

    def actualizar_volumen_canal(self, origen, appfa):
        current_app = self.apps[appfa]
        if origen == "dial":
            nuevo_valor = self.dial_canal[appfa].value() / 100.0
            self.slide_canal[appfa].setValue(self.dial_canal[appfa].value())
        if origen == "slider":
            nuevo_valor = self.slide_canal[appfa].value() / 100.0
            self.dial_canal[appfa].setValue(self.slide_canal[appfa].value())
        
        current_volume = current_app.volume

        for i in range(len(current_volume.values)):
            current_volume.values[i] = nuevo_valor

        # Aplicar el nuevo volumen
        self.pulse.volume_set(current_app, current_volume)

        #chequear si cambia el volumen 
        #self.volumen = int(self.current_app.volume.value_flat * 100)
        #print("volumen seteado app:",self.current_app,": ", self.volumen)

        self.lbl_volumen_canal[appfa].setText(f"Volumen: {int(nuevo_valor * 100)}")

    def mutefun_canal(self, appfa):
        current_app = self.apps[appfa]
        if self.btn_mute_canal[appfa].isChecked():
            self.pulse.sink_input_mute(current_app.index, 1)
            #print(self.current_app, "Silenciada")
            self.lbl_volumen_canal[appfa].setText("Volumen Silenciado")
            self.slide_canal[appfa].setDisabled(True)
            self.dial_canal[appfa].setDisabled(True)
            self.lbl_volumen_canal[appfa].setDisabled(True)
        else:
            self.pulse.sink_input_mute(current_app.index, 0)
            #print(self.current_app, "Volumen Restaurado")
            self.lbl_volumen_canal[appfa].setText(f"Volumen: {self.volumen}")
            self.slide_canal[appfa].setEnabled(True)
            self.dial_canal[appfa].setEnabled(True)
            self.lbl_volumen_canal[appfa].setEnabled(True)

    def get_brave_audio_streams(self):
        streams = self.pulse.sink_input_list()
        brave_streams = [stream for stream in streams if stream.proplist.get('application.name') == 'Brave']
        return brave_streams

    def actualizar_fuentes_audio(self):
        self.apps = self.pulse.sink_input_list()
        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        self.app_selector.clear()
        self.appfa.clear()
        if self.apps:
            self.app_selector.addItems([app.proplist.get('application.name', 'Unknown') + " - " + app.proplist.get('media.name', 'Unknown') for app in self.apps])
            self.appfa = [i for i in range(self.app_selector.count())]
            self.current_app = self.apps[0]
            self.volumen = int(self.current_app.volume.value_flat * 100)
        else:
            self.current_app = None
            self.volumen = 0
            #self.appfa = [self.app_selector.itemText(i) for i in range(self.app_selector.count())]
            QMessageBox.warning(self, "Sin Fuentes de Audio Detectadas", "No se detectaron aplicaciones de Audio activas. Reproduce Audio para controlar el Volumen.")
        self.slider_volumen.setValue(self.volumen)
        self.label_volumen.setText(f"Volumen: {self.volumen}")

    def increaseValue(self):
        current_value = self.dial_volumen.value()
        if current_value < self.dial_volumen.maximum():
            self.dial_volumen.setValue(current_value + 1)
    
    def decreaseValue(self):
        current_value = self.dial_volumen.value()
        if current_value > self.dial_volumen.minimum():
            self.dial_volumen.setValue(current_value - 1)

    def cambiar_app(self, index):
        if index < len(self.apps):
            self.current_app = self.apps[index]
            self.volumen = int(self.current_app.volume.value_flat * 100)
            #print("volumen app select: ", self.current_app,": ",self.volumen) # para debug
            self.slider_volumen.setValue(self.volumen)
            self.label_fuente_audio_selec.setText(f"Index: {self.current_app.index}, Fuente de Audio: {self.current_app.name}")
            self.label_volumen.setText(f"Volumen: {self.volumen}")

    def mutefun(self):
        if self.btn_mute_audio.isChecked():
            self.pulse.sink_input_mute(self.current_app.index, 1)
            #print(self.current_app, "Silenciada")
            self.label_volumen.setText("Volumen Silenciado")
            self.slider_volumen.setDisabled(True)
            self.dial_volumen.setDisabled(True)
            self.label_volumen.setDisabled(True)
        else:
            self.pulse.sink_input_mute(self.current_app.index, 0)
            #print(self.current_app, "Volumen Restaurado")
            self.label_volumen.setText(f"Volumen: {self.volumen}")
            self.slider_volumen.setEnabled(True)
            self.dial_volumen.setEnabled(True)
            self.label_volumen.setEnabled(True)

    def actualizar_volumen(self, origen):
        if origen == "dial":
            nuevo_valor = self.dial_volumen.value() / 100.0
            self.slider_volumen.setValue(self.dial_volumen.value())
        if origen == "slider":
            nuevo_valor = self.slider_volumen.value() / 100.0
            self.dial_volumen.setValue(self.slider_volumen.value())
        
        current_volume = self.current_app.volume

        for i in range(len(current_volume.values)):
            current_volume.values[i] = nuevo_valor

        # Aplicar el nuevo volumen
        self.pulse.volume_set(self.current_app, current_volume)

        #chequear si cambia el volumen 
        #self.volumen = int(self.current_app.volume.value_flat * 100)
        #print("volumen seteado app:",self.current_app,": ", self.volumen)

        self.label_volumen.setText(f"Volumen: {int(nuevo_valor * 100)}")

        #evaluar mute + seleccion + volumen
        #print("self.pulse.sink_info: ",self.pulse.sink_info(self.current_app.index))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(DarkPalette))
    #app.setStyleSheet(qdarkstyle.load_stylesheet(LightPalette))
    ventana = VolumenVentana()
    ventana.show()
    sys.exit(app.exec_())
