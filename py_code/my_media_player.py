import csv

from PyQt5 import QtCore, QtMultimedia
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem


class NowPlaylist:
    def __init__(self):
        super().__init__()

    def write_play_media(self, item):  # Создание csv файлы и запус плеера с выбранной музыкой
        with open('list_media_now.csv', 'w', encoding="utf8", newline='') as csvfile:
            writer = csv.writer(
                csvfile, delimiter=';', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            for i in range(self.medias_now.rowCount()):
                row = []
                for j in range(self.medias_now.columnCount() - 1):
                    sitem = self.medias_now.item(i, j)
                    if sitem.text() == item.text():
                        row.append("start")
                        break
                    if sitem is not None:
                        row.append(sitem.text())
                writer.writerow(row)
        place = self.db.cursor().execute("""select m.name, p.place from Medias m
                    join Places p on p.id = m.idPlaces
                        where m.name like ?""", (item.text(),)).fetchone()
        fullpath = QtCore.QDir.current().absoluteFilePath(f"{place[1]}/{place[0]}.mp3")
        media = QtCore.QUrl.fromLocalFile(fullpath)
        content = QtMultimedia.QMediaContent(media)
        self.stop = False
        self.player.setMedia(content)
        self.media_now.setText(place[0])
        self.duration.setValue(0)
        self.player.play()
        self.tmr.start(1100)

    def rewind(self):  # Перемотка
        self.player.setPosition(self.duration.value())

    def slider_move(self):  # Автодвижение слайдера
        if self.duration.value() == self.duration.maximum():
            self.auto_move_media()
        else:
            self.duration.setValue(self.duration.value() + 1000)

    def change_duration(self):  # Сменя длительности(музыки)
        self.duration.setMaximum(self.player.duration())

    def pause_or_play(self):  # Пауза или игра
        if self.stop:
            self.player.play()
            self.tmr.start(1100)
            self.stop = False
        else:
            self.player.pause()
            self.tmr.stop()
            self.stop = True

    def auto_move_media(self):  # Автоматическая смена музыки при окончании предыдущей
        with open('list_media_now.csv', encoding="utf8") as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))
            reader = [x for i in reader for x in i]
            cnt = int(self.db.cursor().execute("select count"
                                               " from Playlists where name like ?", (self.name_playlist,)).fetchone()[
                          0])
            self.medias_now.item(reader.index("start"), 0).setBackground(QColor(255, 255, 255))
            if reader.index("start") + 1 < cnt:
                self.tmr.stop()
                self.medias_now.item(reader.index("start") + 1, 0).setBackground(QColor(150, 0, 255))
                self.write_play_media(QTableWidgetItem(reader[reader.index("start") + 1]))
            else:
                self.player.stop()

    def move_back(self):  # Движение по кнопке назад
        with open('list_media_now.csv', encoding="utf8") as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))
            reader = [x for i in reader for x in i]
            self.medias_now.item(reader.index("start"), 0).setBackground(QColor(255, 255, 255))
            if reader.index("start") - 1 >= 0:
                self.tmr.stop()
                self.medias_now.item(reader.index("start") - 1, 0).setBackground(QColor(150, 0, 255))
                self.write_play_media(QTableWidgetItem(reader[reader.index("start") - 1]))
            else:
                self.tmr.stop()
                self.player.stop()

    def move_to(self):  # Движение по кнопке вперед
        with open('list_media_now.csv', encoding="utf8") as csvfile:
            reader = list(csv.reader(csvfile, delimiter=';', quotechar='"'))
            reader = [x for i in reader for x in i]
            cnt = int(self.db.cursor().execute("select count"
                                               " from Playlists where name like ?", (self.name_playlist,)).fetchone()[
                          0])
            self.medias_now.item(reader.index("start"), 0).setBackground(QColor(255, 255, 255))
            if reader.index("start") + 1 < cnt:
                self.medias_now.item(reader.index("start") + 1, 0).setBackground(QColor(150, 0, 255))
                self.tmr.stop()
                self.write_play_media(QTableWidgetItem(reader[reader.index("start") + 1]))
            else:
                self.tmr.stop()
                self.player.stop()

    def mouse_change_item(self, item):  # Смена музыки при помощи мыши
        if not self.item1:
            self.item1 = item
        else:
            self.medias_now.item(self.item1.row(), 0).setBackground(QColor(255, 255, 255))
            self.item1 = item
        self.medias_now.item(item.row(), 0).setBackground(QColor(150, 0, 255))
        self.write_play_media(self.medias_now.item(item.row(), 0))

    def volume_sound(self):  # Изменение громкости
        if self.volume_slider.value() == 0:
            self.player.setMuted(True)
        else:
            self.player.setMuted(False)
            self.player.setVolume(self.volume_slider.value())
