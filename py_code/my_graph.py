import sqlite3

from PyQt5.QtWidgets import QWidget

from graph import Ui_Form


class WindowGraph(QWidget, Ui_Form):
    def __init__(self):
        super(WindowGraph, self).__init__()

        self.setupUi(self)
        self.initUi()

    def initUi(self):
        self.db = sqlite3.connect("playNS.db")
        self.create_graph()

    def create_graph(self):  # Создание графика длительности
        cnt = int(self.db.cursor().execute("select count"
                                           " from Playlists where name like ?", ("Общий плейлист",)).fetchone()[0])
        durations = [i[0] for i in self.db.cursor().execute("""select m.duration from Medias m
                        where m.idPlaylists = 1""").fetchall()]
        if durations:
            self.graphicsView.plot([i + 1 for i in range(cnt)], [i for i in durations], pen="purple")
            self.max_s.setText(f"{self.max_s.text()} {max(durations)}")
            self.avrg.setText(f"{self.avrg.text()} {sum(durations) // len(durations)}")
            self.min_s.setText(f"{self.min_s.text()} {min(durations)}")