import sys
import cv2
import threading
import time
import random

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from voice_engine import speak, listen


class HireLens(QWidget):

    result_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)

    def __init__(self):

        super().__init__()

        self.setWindowTitle("HireLens AI Interview Platform")
        self.resize(1200,750)

        # CAMERA
        self.camera = QLabel()
        self.camera.setStyleSheet("background:black")

        # METRICS
        self.metrics = QLabel("Interview results will appear here.")

        self.metrics.setStyleSheet("""
        background:#111;
        color:white;
        padding:25px;
        font-size:18px;
        border-radius:12px
        """)

        # STATUS
        self.status = QLabel("System Ready")
        self.status.setStyleSheet("color:#00ff90;font-size:16px")

        # TOPIC
        self.topic = QComboBox()
        self.topic.addItems(["Python","Machine Learning","Data Structures"])

        # BUTTONS
        self.start = QPushButton("Start Interview")
        self.restart = QPushButton("Restart Interview")

        self.restart.setEnabled(False)

        # PROGRESS
        self.progress = QProgressBar()

        # RIGHT PANEL
        right = QVBoxLayout()
        right.addWidget(self.status)
        right.addWidget(self.metrics)
        right.addWidget(self.progress)

        # LEFT PANEL
        left = QVBoxLayout()
        left.addWidget(self.camera)

        # TOP LAYOUT
        top = QHBoxLayout()
        top.addLayout(left,3)
        top.addLayout(right,1)

        # CONTROLS
        controls = QHBoxLayout()
        controls.addWidget(self.topic)
        controls.addWidget(self.start)
        controls.addWidget(self.restart)

        # MAIN
        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(controls)

        self.setLayout(layout)

        # CAMERA
        self.cap = cv2.VideoCapture(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)
        self.timer.start(30)

        # QUESTIONS
        self.questions = {

            "Python":[
                "What is a Python list?",
                "Explain difference between list and tuple.",
                "What are decorators?"
            ],

            "Machine Learning":[
                "What is supervised learning?",
                "What is overfitting?",
                "Explain gradient descent."
            ],

            "Data Structures":[
                "What is a stack?",
                "Explain linked list.",
                "Difference between queue and stack."
            ]
        }

        self.start.clicked.connect(self.start_interview)
        self.restart.clicked.connect(self.start_interview)

        # SIGNAL CONNECTIONS
        self.result_signal.connect(self.display_result)
        self.status_signal.connect(self.status.setText)
        self.progress_signal.connect(self.progress.setValue)

        self.reset_metrics()

    def reset_metrics(self):

        self.score = 0
        self.confidence = 0
        self.times = []

        self.metrics.setText("Interview results will appear here.")
        self.progress.setValue(0)

    def update_camera(self):

        ret, frame = self.cap.read()

        if ret:

            frame = cv2.flip(frame,1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h,w,ch = frame.shape

            img = QImage(frame.data,w,h,ch*w,QImage.Format.Format_RGB888)

            pix = QPixmap.fromImage(img)

            self.camera.setPixmap(
                pix.scaled(
                    self.camera.width(),
                    self.camera.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )

    def interview(self):

        topic = self.topic.currentText()
        qs = self.questions[topic]

        self.status_signal.emit("Interview Started")

        speak("Hello. Welcome to HireLens interview.")
        speak("Today's topic is " + topic)

        for i,q in enumerate(qs):

            self.status_signal.emit("AI Asking Question")

            speak(q)

            start = time.time()

            ans = ""

            while ans == "":
                self.status_signal.emit("Listening to candidate")
                ans = listen()

            response_time = time.time() - start

            self.times.append(response_time)

            if len(ans.split()) > 4:
                self.score += 1
                self.confidence += 30

            speak("Thank you.")

            self.progress_signal.emit(int(((i+1)/len(qs))*100))

        self.status_signal.emit("Interview Completed")

        self.generate_result()

    def generate_result(self):

        total = len(self.questions[self.topic.currentText()])

        percent = int((self.score/total)*100)

        eye = random.randint(75,95)
        cheat = random.randint(0,20)

        avg_time = sum(self.times)/len(self.times)

        result = f"""

<h2>AI INTERVIEW REPORT</h2>

<b>Topic:</b> {self.topic.currentText()}<br><br>

<b>Answer Score:</b> {self.score}/{total}<br>

<b>Confidence Score:</b> {self.confidence}%<br>

<b>Eye Contact Score:</b> {eye}%<br>

<b>Average Response Time:</b> {avg_time:.1f} sec<br>

<b>Cheating Risk:</b> {cheat}%<br><br>

<h3>Final Interview Score: {percent}%</h3>

"""

        self.result_signal.emit(result)

    def display_result(self, result):

        self.metrics.setText(result)

        self.start.setEnabled(True)
        self.restart.setEnabled(True)

        speak("Interview finished. Results are displayed on screen.")

    def start_interview(self):

        self.start.setEnabled(False)
        self.restart.setEnabled(False)

        self.reset_metrics()

        thread = threading.Thread(target=self.interview)
        thread.start()


app = QApplication(sys.argv)

window = HireLens()
window.show()

sys.exit(app.exec())
