import sqlite3
import sys

from PyQt5 import QtWidgets, QtMultimedia, QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QHeaderView

from form import Ui_MainWindow
from my_graph import WindowGraph
from my_media_player import NowPlaylist
from playlist import Playlist

class Window_Main(QMainWindow, Ui_MainWindow, Playlist, NowPlaylist):
    def __init__(self):
        super(Window_Main, self).__init__()

        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.media_now.hide()
        self.medias_now.hide()
        self.playlists_sp.hide()
        self.add_file.hide()
        self.create_playlist.hide()
        self.back.hide()
        self.in_playlist.hide()
        self.done.hide()
        self.lcdNumber.hide()
        self.delete_playlist.hide()
        self.label.hide()
        self.delete_directory.hide()
        self.update_playlist.hide()
        self.pause.hide()
        self.back_media.hide()
        self.next_media.hide()
        self.duration.hide()
        self.volume_slider.hide()

        self.setWindowIcon(QIcon("icon.ico"))

        self.item1 = None

        self.db = sqlite3.connect("playNS.db")
        self.player = QtMultimedia.QMediaPlayer()
        self.stop = True
        self.volume_slider.setMaximum(100)
        self.volume_slider.valueChanged.connect(self.volume_sound)
        self.volume_slider.setValue(100)
        self.medias_now.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.medias_now.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.duration.sliderMoved.connect(self.rewind)
        self.player.durationChanged.connect(self.change_duration)
        self.tmr = QTimer()
        self.tmr.timeout.connect(self.slider_move)

        self.setWindowTitle("NaiShiro-player")
        self.now.clicked.connect(self.now_play)
        self.playlists.clicked.connect(self.playlist_play)
        self.graph.clicked.connect(self.graph_show)
        self.playlists_sp.itemActivated.connect(self.select_playlist)
        self.add_file.clicked.connect(self.add_files)
        self.create_playlist.clicked.connect(self.create_playlists)
        self.back.clicked.connect(self.playlist_play)
        self.in_playlist.itemActivated.connect(self.select_media)
        self.done.clicked.connect(self.add_media_to_playlist)
        self.delete_playlist.clicked.connect(self.delete_playlists)
        self.delete_directory.clicked.connect(self.delete_directorys)
        self.update_playlist.clicked.connect(self.add_to_playlist)
        self.pause.clicked.connect(self.pause_or_play)
        self.back_media.clicked.connect(self.move_back)
        self.next_media.clicked.connect(self.move_to)
        self.medias_now.itemActivated.connect(self.mouse_change_item)

    def playlist_play(self):  # показ всех списков и того, что внутри их
        self.hello.hide()
        self.media_now.hide()
        self.medias_now.hide()
        self.back.hide()
        self.delete_playlist.hide()
        self.label.hide()
        self.update_playlist.hide()
        self.pause.hide()
        self.back_media.hide()
        self.next_media.hide()
        self.duration.hide()
        self.volume_slider.hide()

        self.playlists_sp.show()
        self.delete_directory.show()
        self.add_file.show()
        self.create_playlist.show()

        self.show_playlist()

    def now_play(self):  # показ играющего плейлиста
        self.media_now.show()
        self.medias_now.show()
        self.pause.show()
        self.back_media.show()
        self.next_media.show()
        self.volume_slider.show()

        self.label.hide()
        self.update_playlist.hide()
        self.delete_directory.hide()
        self.hello.hide()
        self.back.hide()
        self.delete_playlist.hide()
        self.playlists_sp.hide()
        self.add_file.hide()
        self.create_playlist.hide()
        self.in_playlist.hide()
        self.duration.show()

    def graph_show(self):  # Показ окна графика
        self.w2 = WindowGraph()
        self.w2.show()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    wnd = Window_Main()
    wnd.show()
    sys.exit(app.exec())
