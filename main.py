import sys
from PyQt5 import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import (Qt, pyqtSignal, QThread, pyqtSlot, QCoreApplication)
from dashboard import *
import numpy as np
from threading import *
from sensor import *
import settings as form_settings


class Main(QMainWindow, Ui_MainWindow):

    process_pool = []

    def __init__(self):
        super(Main, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.showFullScreen()
        self.btn_settings.clicked.connect(self.show_Settings)
        self.gv_pressure.setLabels(title='Pressure', left='Magnitude', bottom='Time (t)')
        self.gv_pressure.setAntialiasing(True)
        self.gv_flow.setLabels(title='Flow', left='Magnitude', bottom='Time (t)')
        self.gv_volume.setLabels(title='Volume', left='Magnitude', bottom='Time (t)')
        self.refresh_display()
        
        pressure_sensor = Sensor(self)
        pressure_sensor.setup()
        pressure_sensor.set_path("temp/pressure.txt")
        pressure_sensor.result_callback.connect(self.pressure_listener)
        pressure_sensor.start()
        self.process_pool.append(pressure_sensor)

        flow_sensor = Sensor(self)
        flow_sensor.setup()
        flow_sensor.set_path("temp/flow.txt")
        flow_sensor.result_callback.connect(self.flow_listener)
        flow_sensor.start()
        self.process_pool.append(flow_sensor)

        volume_sensor = Sensor(self)
        volume_sensor.setup()
        volume_sensor.set_path("temp/volume.txt")
        volume_sensor.result_callback.connect(self.volume_listener)
        volume_sensor.start()
        self.process_pool.append(volume_sensor)

    def show_Settings(self):
        self.window = QMainWindow()
        self.form_settingsProperties = form_settings.Ui_MainWindow()
        self.ui = self.form_settingsProperties.setupUi(self.window)
        self.window.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.window.showFullScreen()
        self.form_settingsProperties.btn_save_changes.clicked.connect(self.save_settings)
        self.window.show()

    def save_settings(self):
        mode = str(self.form_settingsProperties.cmb_mode.currentText()).lower()
        volume = str(self.form_settingsProperties.txt_volume.text()).replace('mL', '')
        resp_rate = str(self.form_settingsProperties.txt_resp_rate.text()).replace(' Breath/min', '')
        ieratio = str(self.form_settingsProperties.txt_ieratio.text())
        flow = str(self.form_settingsProperties.txt_flow.text()).replace(' Lpm', '')
        peep = str(self.form_settingsProperties.txt_peep.text())
        fio2 = str(self.form_settingsProperties.txt_fio2.text()).replace('%', '')

        with open('temp/mode.txt', 'w') as f: f.write(mode)

        with open('temp/tidal_volume.txt', 'w') as f: f.write(volume)

        with open('temp/resp_rate.txt', 'w') as f: f.write(resp_rate)

        with open('temp/ie_ratio.txt', 'w') as f: f.write(ieratio)

        with open('temp/peak_flow.txt', 'w') as f: f.write(flow)

        with open('temp/peep.txt', 'w') as f: f.write(peep)

        with open('temp/fio2.txt', 'w') as f: f.write(fio2)

        self.refresh_display()
        self.window.close()

    def refresh_display(self):
        with open('temp/mode.txt', 'r') as f: self.lbl_mode.setText(f.read().title())

        with open('temp/tidal_volume.txt', 'r') as f: self.lbl_tidal_volume.setText(f'{f.read()} mL')

        with open('temp/resp_rate.txt', 'r') as f: self.lbl_resp_rate.setText(f'{f.read()} BPM')

        with open('temp/ie_ratio.txt', 'r') as f: self.lbl_ieratio.setText(f'1:{f.read()}')

        with open('temp/peak_flow.txt', 'r') as f: self.lbl_flow.setText(f'{f.read()} Lpm')

        with open('temp/peep.txt', 'r') as f: self.lbl_peep.setText(f'{f.read()} cmH2O')

        with open('temp/fio2.txt', 'r') as f: self.lbl_fio2.setText(f'{f.read()}%')

        with open('temp/pressure_peak.txt', 'r') as f: self.lbl_pressure_peak.setText(f'{f.read()} cmH2O')

        with open('temp/p_plateau.txt', 'r') as f: self.lbl_p_plateau.setText(f'{f.read()} cmH2O')
        
    @pyqtSlot(list)
    def pressure_listener(self, pressure_stack):
        self.gv_pressure.clear()
        self.gv_pressure.plot(pressure_stack)

    @pyqtSlot(list)
    def flow_listener(self, flow_stack):
        self.gv_flow.clear()
        self.gv_flow.plot(flow_stack)

    @pyqtSlot(list)
    def volume_listener(self, volume_stack):
        self.gv_volume.clear()
        self.gv_volume.plot(volume_stack)

    def closeEvent(self, event):
        for process in self.process_pool:
            process.stop()
            time.sleep(1)
        
        time.sleep(1)

app = QtWidgets.QApplication([])
application = Main()
application.show()
sys.exit(app.exec_())