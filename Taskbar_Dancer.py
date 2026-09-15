import sys
import math
import random
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QTimer, QPointF
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioMeterInformation

class TaskbarDancer(QWidget):
    def __init__(self):
        super().__init__()

        # Masaüstünde şeffaf ve çerçevesiz katman
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.Tool | 
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.w = 120
        self.h = 110
        self.setFixedSize(self.w, self.h)

        self.snap_to_taskbar()

        self.is_playing = False
        self.dance_frame = 0.0
        self.notes = []
        self.drag_position = None

        # Doğrudan ana hoparlör ses ibresini başlat
        self.meter = None
        self.init_master_audio_meter()

        # Saniyede yaklaşık 16 kez hoparlörün anlık tepe değerini yokla
        self.audio_check_timer = QTimer(self)
        self.audio_check_timer.timeout.connect(self.check_audio)
        self.audio_check_timer.start(60)

        # 60 FPS çizim döngüsü
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

    def snap_to_taskbar(self):
        screen = QApplication.primaryScreen()
        work_area = screen.availableGeometry()
        pos_x = work_area.right() - 220
        pos_y = work_area.bottom() - self.h + 2
        self.move(pos_x, pos_y)

    def init_master_audio_meter(self):
        try:
            device = AudioUtilities.GetSpeakers()
            
            # Yeni pycaw sürümlerinde COM arayüzü _dev altında bulunur
            raw_dev = getattr(device, '_dev', device)
            interface = raw_dev.Activate(IAudioMeterInformation._iid_, CLSCTX_ALL, None)
            self.meter = cast(interface, POINTER(IAudioMeterInformation))
            print("Windows Ana Hoparlör Çıkışına başarıyla bağlandı!")
        except Exception as e:
            print(f"Hoparlör bağlantı hatası: {e}")

    def check_audio(self):
        if self.meter:
            try:
                # 0.0 ile 1.0 arasında anlık ses tepe değeri
                peak = self.meter.GetPeakValue()
                
                # Çok ufak bir ses çıksa bile şarkı çalıyor kabul et
                if peak > 0.003:
                    self.is_playing = True
                else:
                    self.is_playing = False
            except Exception:
                pass

    def update_animation(self):
        if self.is_playing:
            self.dance_frame += 0.22
            # Müzik vurdukça uçuşan notalar
            if random.random() < 0.12:
                self.notes.append({
                    'x': 60 + random.uniform(-15, 15),
                    'y': 45,
                    'sym': random.choice(['♪', '♫', '♬']),
                    'alpha': 255,
                    'color': random.choice([QColor(255, 90, 150), QColor(0, 220, 255), QColor(255, 215, 0)])
                })
        else:
            self.dance_frame += 0.03

        # Uçuşan notaların hareketi
        for n in self.notes:
            n['y'] -= 1.3
            n['alpha'] -= 5
        self.notes = [n for n in self.notes if n['alpha'] > 0]

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Şeffaflık zemin koruması
        painter.setBrush(QColor(0, 0, 0, 1))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        cx = 60
        cy = 65

        # --- Şarkı Yokken: Uyuma ---
        if not self.is_playing:
            breath = math.sin(self.dance_frame) * 2

            painter.setBrush(QColor(40, 40, 40))
            painter.drawRect(cx - 16, cy + 22, 9, 20)
            painter.drawRect(cx + 7, cy + 22, 9, 20)
            painter.setBrush(QColor(220, 60, 60))
            painter.drawEllipse(cx - 18, cy + 38, 12, 7)
            painter.drawEllipse(cx + 6, cy + 38, 12, 7)

            painter.setBrush(QColor(70, 130, 240))
            painter.drawRoundedRect(cx - 20, int(cy - 5 + breath), 40, 30, 8, 8)

            painter.setBrush(QColor(255, 220, 185))
            painter.drawEllipse(QPointF(cx, cy - 20 + breath), 16, 16)

            painter.setPen(QPen(QColor(30, 30, 30), 3))
            painter.setBrush(QColor(255, 140, 0))
            painter.drawEllipse(cx - 20, int(cy - 8 + breath), 8, 11)
            painter.drawEllipse(cx + 12, int(cy - 8 + breath), 8, 11)

            painter.setPen(QPen(QColor(50, 50, 50), 2))
            painter.drawArc(cx - 11, int(cy - 23 + breath), 7, 5, 0, 180 * 16)
            painter.drawArc(cx + 4, int(cy - 23 + breath), 7, 5, 0, 180 * 16)

            painter.setFont(QFont("Arial", 8, QFont.Bold))
            painter.setPen(QColor(180, 180, 180, 180))
            zzz_y = int((self.dance_frame * 10) % 25)
            painter.drawText(cx + 18, cy - 28 - zzz_y, "z")

        # --- Şarkı Varken: Dans ---
        else:
            bounce = abs(math.sin(self.dance_frame * 1.5)) * 14
            tilt = math.sin(self.dance_frame) * 14

            painter.save()
            painter.translate(cx, cy + 25)
            painter.rotate(tilt)

            leg_kick = math.sin(self.dance_frame * 2) * 6
            painter.setBrush(QColor(40, 40, 40))
            painter.drawRect(-16, int(-bounce), 9, 18)
            painter.drawRect(7, int(-bounce + leg_kick), 9, 18)
            painter.setBrush(QColor(220, 60, 60))
            painter.drawEllipse(-18, int(15 - bounce), 12, 7)
            painter.drawEllipse(6, int(15 - bounce + leg_kick), 12, 7)

            painter.setBrush(QColor(70, 130, 240))
            painter.drawRoundedRect(-20, int(-30 - bounce), 40, 30, 8, 8)

            arm_swing = math.cos(self.dance_frame * 1.5) * 10
            painter.setBrush(QColor(70, 130, 240))
            painter.drawRoundedRect(-28, int(-30 - bounce + arm_swing), 9, 20, 4, 4)
            painter.drawRoundedRect(19, int(-30 - bounce - arm_swing), 9, 20, 4, 4)

            painter.setBrush(QColor(255, 220, 185))
            painter.drawEllipse(QPointF(0, -45 - bounce), 16, 16)

            painter.setPen(QPen(QColor(30, 30, 30), 3))
            painter.drawArc(-14, int(-63 - bounce), 28, 20, 0, 180 * 16)
            painter.setBrush(QColor(255, 140, 0))
            painter.drawEllipse(-18, int(-51 - bounce), 7, 12)
            painter.drawEllipse(11, int(-51 - bounce), 7, 12)

            painter.setPen(QPen(QColor(50, 50, 50), 2))
            painter.drawLine(-9, int(-47 - bounce), -5, int(-44 - bounce))
            painter.drawLine(-5, int(-44 - bounce), -9, int(-41 - bounce))
            painter.drawLine(9, int(-47 - bounce), 5, int(-44 - bounce))
            painter.drawLine(5, int(-44 - bounce), 9, int(-41 - bounce))

            painter.setBrush(QColor(200, 50, 50))
            painter.drawChord(-4, int(-42 - bounce), 8, 6, 0, -180 * 16)

            painter.restore()

        for n in self.notes:
            painter.setFont(QFont("Arial", 12, QFont.Bold))
            col = QColor(n['color'])
            col.setAlpha(max(0, int(n['alpha'])))
            painter.setPen(col)
            painter.drawText(int(n['x']), int(n['y']), n['sym'])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            new_pos = event.globalPos() - self.drag_position
            screen = QApplication.primaryScreen()
            work_area = screen.availableGeometry()

            fixed_y = work_area.bottom() - self.h + 2
            clamped_x = max(work_area.left(), min(new_pos.x(), work_area.right() - self.w))

            self.move(clamped_x, fixed_y)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        status = "Dans Ediyor" if self.is_playing else "Uykuda"
        info = QAction(status, self)
        info.setEnabled(False)
        menu.addAction(info)
        menu.addSeparator()

        exit_btn = QAction("Kapat", self)
        exit_btn.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_btn)
        menu.exec_(event.globalPos())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dancer = TaskbarDancer()
    dancer.show()
    sys.exit(app.exec_())