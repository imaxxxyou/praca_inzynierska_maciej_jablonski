import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QGL
from PySide6.QtCore import Qt, QTimer
import pygame
from pygame.locals import *

class PygameOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(PygameOpenGLWidget, self).__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setFocus()

        # Inicjalizacja Pygame
        pygame.init()

        # Ustawienia Pygame
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)

        # Inne ustawienia
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGame)
        self.timer.start(16)  # Około 60 klatek na sekundę

    def initializeGL(self):
        pass

    def resizeGL(self, w, h):
        pass

    def paintGL(self):
        self.updateGame()

    def updateGame(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Tutaj umieść logikę aktualizacji gry

        self.clock.tick(60)  # Ograniczenie do około 60 klatek na sekundę
        self.swapBuffers()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("PyQt6 + Pygame + OpenGL Widget")

        # Dodaj OpenGL Widget do okna głównego
        self.openglWidget = PygameOpenGLWidget(self)
        self.setCentralWidget(self.openglWidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec())
