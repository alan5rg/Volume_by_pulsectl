#040724.se implementa actualizacion de fuentes de audio, incluida verificación, mensajes y boton de actualizacion, realizar test qa
#040724.agrego qdial vinculado al qslider, se vinvulo tecla arriba y abajo para controlar los diales
#030724.corregido minimas funciones, evaluar
import sys, os
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QSlider, QLabel, QPushButton, QComboBox, QDial, QShortcut, QMessageBox
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
import pulsectl
#from pulsectl import Pulse, PulseVolumeInfo
from PyQt5.QtGui import QKeySequence
#para modo oscuro con toda la onda
import qdarkstyle
from qdarkstyle import load_stylesheet, LightPalette, DarkPalette


#class VolumenVentana(QWidget):
class VolumenVentana(QMainWindow):
    #def __init__(self):
    #    super().__init__()
    def __init__(self, parent=None):
        super().__init__(parent)
        versionado = "v.44.040724"

        # Configuración de la ventana UI
        self.setWindowTitle("Control de Volumen "+ versionado)
        self.resize(420, 380)

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
        self.mute_audio = QPushButton("Silencio")
        self.mute_audio.setCheckable(True)
        self.mute_audio.clicked.connect(self.mutefun)

        # Botón Actuzalizar Fuentes de Audio
        self.act_faudio = QPushButton("Actualizar Fuentes de Audio")
        self.act_faudio.clicked.connect(self.actualizar_fuentes_audio)

        # Conexión de la señal de valor cambiado a la función de actualización de volumen
        #self.slider_volumen.valueChanged.connect(self.actualizar_volumen(self,"slider"))
        self.slider_volumen.valueChanged.connect(lambda: self.actualizar_volumen('slider'))
        #self.dial_volumen.valueChanged.connect(self.actualizar_volumen(self,"dial"))
        self.dial_volumen.valueChanged.connect(lambda: self.actualizar_volumen('dial'))

        # Diseño de la interfaz de usuario mediante QWidget y Layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.addWidget(self.act_faudio)
        main_layout.addWidget(self.label_fuentes_de_audio)
        main_layout.addWidget(self.app_selector)
        
        #para centrar dial y slider
        potes_layout = QVBoxLayout()
        
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

        main_layout.addLayout(potes_layout)
        main_layout.addWidget(self.label_fuente_audio_selec)
        main_layout.addWidget(self.label_volumen)
        main_layout.addWidget(self.mute_audio)

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

    def get_brave_audio_streams(self):
        streams = self.pulse.sink_input_list()
        brave_streams = [stream for stream in streams if stream.proplist.get('application.name') == 'Brave']
        return brave_streams

    def actualizar_fuentes_audio(self):
        self.apps = self.pulse.sink_input_list()
        self.actualizar_interfaz()

    def actualizar_interfaz(self):
        self.app_selector.clear()
        if self.apps:
            self.app_selector.addItems([app.proplist.get('application.name', 'Unknown') + " - " + app.proplist.get('media.name', 'Unknown') for app in self.apps])
            self.current_app = self.apps[0]
            self.volumen = int(self.current_app.volume.value_flat * 100)
        else:
            self.current_app = None
            self.volumen = 0
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
        if self.mute_audio.isChecked():
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
