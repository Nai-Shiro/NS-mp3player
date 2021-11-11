import os

import mutagen
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QTableWidgetItem


class Playlist:
    def __init__(self):
        super().__init__()

    def select_playlist(self, item):  # Отображение выбранного плейлиста
        self.back.show()
        self.in_playlist.show()
        self.update_playlist.show()

        self.delete_directory.hide()
        self.playlists_sp.hide()
        self.in_playlist.clear()
        self.item = item
        if self.item is None:
            self.done.show()
            self.select = 0
        else:
            self.name_playlist = self.item.text()
            self.db.commit()
            self.delete_playlist.show()
            self.select = 1

        sql = """
                    select m.name from Medias m
                    join Playlists p on p.id = m.idPlaylists
                    where p.name like ?
                          """
        for j in self.db.cursor().execute(sql, (self.item.text() if self.item is not None
                                                else "Общий плейлист",)).fetchall():
            self.in_playlist.addItem(j[0])

    def add_files(self):  # Добавление файлов в общий плейслилст
        directory = QFileDialog.getExistingDirectory()
        self.label.hide()
        if directory != "":
            if self.db.cursor().execute("select place from Places\
                             where place like ?", (directory,)).fetchone() is None:
                self.db.cursor().execute("insert into Places(place) values(?)", (directory,))
            id_directory = self.db.cursor().execute("""select id from Places
                where place like ?""", (directory,)).fetchone()
            cnt = 0
            for i in os.listdir(directory):
                if i[-3:] == "mp3":
                    file = mutagen.File(f"{directory}/{i}")
                    sql = f"""insert into Medias(name, duration, idPlaylists, idPlaces) values(?,
        {round(int(file.info.length) / 60, 2)}, 1, ?) """
                    pr1 = self.db.cursor().execute("""select name, idPlayLists from Medias where name
                                                  like ? and idPlaylists = 1 """, (i[:-4],)).fetchone()
                    if pr1 is not None:
                        continue
                    cnt += 1
                    self.db.cursor().execute(sql, (i[:-4], id_directory[0]))
            cnt += int(self.db.cursor().execute("select count"
                                                " from Playlists where name like ?", ("Общий плейлист",)).fetchone()[0])
            self.db.cursor().execute("update Playlists set count = ?", (cnt,))
            self.db.commit()

    def create_playlists(self):  # Создание плейлиста
        self.delete_playlist.hide()
        self.selected_media = []
        self.name_playlist = QInputDialog.getText(self, "Введите название плейлиста",
                                                  "Введите название плейлиста")[0]
        if self.name_playlist != "":
            if not self.db.cursor().execute("select name from Playlists\
                                     where name like ?", (self.name_playlist,)).fetchone():  # Условие, что нет
                # такого же названия
                self.db.cursor().execute("insert into Playlists(name, count)\
                                         values(?, 0)", (self.name_playlist,))
                self.lcdNumber.display(0)
                self.select_playlist(None)

    def show_playlist(self):  # Показ всех плейлистов
        self.db.rollback()
        self.playlists_sp.show()
        self.delete_playlist.show()

        self.back.hide()
        self.update_playlist.hide()
        self.in_playlist.hide()
        self.done.hide()
        self.delete_playlist.hide()
        self.lcdNumber.hide()
        if self.playlists_sp.item(0) is not None:
            self.playlists_sp.clear()
        self.in_playlist.clear()
        sql = """
        select p.name from Playlists p
              """
        self.all_playlists = []
        for j in self.db.cursor().execute(sql).fetchall():
            if j[0] not in self.all_playlists:
                self.all_playlists.append(j[0])
                self.playlists_sp.addItem(j[0])

    def select_media(self, item):  # Выбор медии из списка
        if self.select == 0:
            self.delete_playlist.hide()
            self.lcdNumber.show()
            if item.text() not in self.selected_media:
                self.selected_media.append(item.text())
                self.lcdNumber.display(int(self.lcdNumber.value()) + 1)
        else:
            a = QInputDialog.getItem(self, "Выбор", "Что сделать?", ("Проиграть", "Удалить"),
                                     editable=False)[0]
            if a == "Удалить":  # Удаление медии из программы
                self.db.cursor().execute("""delete from Medias
                    where name like ? and idPlaylists like
                     (select id from Playlists where name like ?)""",
                                         (item.text(), self.item.text()))

                if not self.db.cursor().execute("""select m.name from Medias m
                    join Playlists p on p.id = m.idPlaylists
                        where p.name like ?""", (
                self.item.text(),)).fetchall() and self.item.text() != "Общий плейлист":
                    self.db.cursor().execute("delete from Playlists where name like ?", (self.item.text(),))
                    # Удаление плейлиста, с условием, что он пустой и не общий
                    self.db.commit()
                    self.show_playlist()
                else:
                    self.select_playlist(self.item)
            elif a == "Проиграть":  # проигрывание медии
                self.show_medias_now()
                self.write_play_media(item)

    def add_media_to_playlist(self):  # добавление файлов плейлист
        self.done.hide()
        self.in_playlist.hide()
        self.back.hide()
        self.lcdNumber.hide()
        self.delete_playlist.hide()
        self.update_playlist.hide()

        self.playlists_sp.show()

        if self.selected_media:
            id_playlist = self.db.cursor().execute("select id from Playlists\
                                                       where name like ?", (self.name_playlist,)).fetchone()[0]
            cnt = 0
            for i in self.selected_media:
                id_place = self.db.cursor().execute("""
                          select idPlaces from Medias m
                          where name like ?
                          """, (i,)).fetchone()[0]
                duration = self.db.cursor().execute("""
                          select duration from Medias m
                          where name like ?
                          """, (i,)).fetchone()[0]
                if not self.db.cursor().execute("select name from Medias\
                                                where name like ? and idPlaylists = ?", (i, id_playlist)).fetchone():
                    cnt += 1
                    self.db.cursor().execute("""
                        insert into Medias(name, duration, idPlaylists, idPlaces) values(?, ?, ?, ?)""",
                                             (i, duration, id_playlist, id_place))
            cnt += int(self.db.cursor().execute("select count"
                                                " from Playlists where name like ?", (self.name_playlist,)).fetchone()[
                           0])
            self.db.cursor().execute("""update Playlists set count = ?
            where name like ?""", (cnt, self.name_playlist))
            self.db.commit()
            self.show_playlist()
        else:
            self.db.rollback()

    def delete_playlists(self):  # Удаление плейлиста
        if self.item.text() == "Общий плейлист":
            self.label.show()
        else:
            if QInputDialog.getItem(self, "Вы уверены", "Удалить плейлист?", ("Да", "Нет"),
                                    editable=False)[0] == "Да":
                id_playlist = self.db.cursor().execute("""
                          select id from Playlists p
                          where name like ?
                          """, (self.item.text(),)).fetchone()[0]
                sql = """
                delete from Medias where idPlaylists = ?
                      """
                self.db.cursor().execute(sql, (id_playlist,))
                self.db.cursor().execute("delete from Playlists where id = ?", (id_playlist,))
                self.db.commit()
                self.show_playlist()

    def delete_directorys(self):  # удаление директории
        directory = QFileDialog.getExistingDirectory()
        self.label.hide()
        if directory != "":
            if self.db.cursor().execute("select place from Places\
                                         where place like ?", (directory,)).fetchone() is not None:
                id_directory = self.db.cursor().execute("""select id from Places
                                where place like ?""", (directory,)).fetchone()[0]
                self.db.cursor().execute(f"delete from Medias where idPlaces = {id_directory}")
                self.db.cursor().execute("delete from Places where place like ?", (directory,))
                self.db.cursor().execute("""update Playlists set count = ?
                                            where id = ?""", (len(self.db.cursor().execute("""select id from Medias
                            where idPlaylists = 1""").fetchall()[0]) if self.db.cursor().execute("""select id from Medias
                            where idPlaylists = 1""").fetchall() else 0, '1'))
                self.db.commit()

    def add_to_playlist(self):  # добавление в плейлист
        self.selected_media = []
        self.lcdNumber.display(0)
        self.select_playlist(None)

    def show_medias_now(self):  # показывание медии выбранного плейлиста при проигрывании плейлиста
        all_media_in = self.db.cursor().execute("""select m.name, m.duration from Medias m
                    join Playlists p on p.id = m.idPlaylists
                        where p.name like ?""", (self.item.text(),)).fetchall()
        self.medias_now.setRowCount(len(all_media_in))
        self.medias_now.setColumnCount(2)
        for i in range(len(all_media_in)):
            for j in range(2):
                self.medias_now.setItem(i, j, QTableWidgetItem(str(all_media_in[i][j])))
        self.medias_now.setHorizontalHeaderLabels(["name", "duration"])
