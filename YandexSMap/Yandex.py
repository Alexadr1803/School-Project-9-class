# 9А Гаврилюк Александр
import requests
import sys
import datetime
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPixmap

    
class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.z = 15 #стандартное значение маштаба карты
        uic.loadUi('pyqt_design.ui', self) # загрузка шаблона расположения кнопок
        self.coord12 = 36.241424 # значение широты в данный момент
        self.coord22 = 51.730848 # значение долготы в данный момент
        self.map_type = "map" # тип слоев карты
        self.searcht = None # текст поиска
        self.pixmap = None # изображение карты
        self.setWindowTitle('Static Maps work') # заголовок окна
        self.coord1.setText(str(self.coord12)) # текст поля широты
        self.coord2.setText(str(self.coord22)) # текст поля долготы
        self.start.clicked.connect(self.button) # отслеживание нажатия кнопки поиска
        self.on_b.clicked.connect(self.button)
        self.save.clicked.connect(self.save_map) # отслеживание нажатий кнопки активации слоя карты

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_PageUp:
            if self.z < 18:
                self.z += 1
        if event.key() == QtCore.Qt.Key_PageDown:
            if self.z > 1:
                self.z -= 1
        if event.key() == QtCore.Qt.Key_D:
            if self.coord12 <= 179.95:
                self.coord1.setText(str(round(self.coord12 + 0.001, 5)))
        if event.key() == QtCore.Qt.Key_S:
            if self.coord22 >= -88.95:
                self.coord2.setText(str(round(self.coord22 - 0.001, 5)))
        if event.key() == QtCore.Qt.Key_A:
            if self.coord12 >= -179.95:
                self.coord1.setText(str(round(self.coord12 - 0.001, 5)))
        if event.key() == QtCore.Qt.Key_W:
            if self.coord22 <= 88.95:
                self.coord2.setText(str(round(self.coord22 + 0.001, 5)))
        self.button()
        self.tart()
        event.accept()

    def button(self):
        try:
            self.coord12 = float(self.coord1.text())
        except ValueError:
            self.coord12 = 0.0
        try:
            self.coord22 = float(self.coord2.text())
        except ValueError:
            self.coord22 = 0.0
        if self.coord12 >= 179.95:
            self.coord12 = 180
        if self.coord12 <= -179.95:
            self.coord12 = -180
        if self.coord22 <= -88.95:
            self.coord22 = -85
        if self.coord22 >= 88.95:
            self.coord22 = 85
        self.coord1.setText(str(self.coord12))
        self.coord2.setText(str(self.coord22))
        self.tart()

    def tart(self):
        coord1 = self.coord1.text()
        coord2 = self.coord2.text()
        if self.r1.isChecked():
            self.map_type = "map"
        if self.r2.isChecked():
            self.map_type = "sat"
        if self.r3.isChecked():
            self.map_type = "sat,skl"
        try:
            float(self.search.text())
            self.label_3.setText("Поиск : Некорректный запрос")
        except ValueError:
            print(self.searcht)
            if self.search.text() != self.searcht:
                response = requests.get(f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode={self.search.text()}&format=json")
                if response:
                    json_response = response.json()
                    try:
                        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                        toponym_coodrinates = toponym["Point"]["pos"]
                        coords = list(map(float, toponym_coodrinates.split()))
                        image = requests.get(
                            f"https://static-maps.yandex.ru/1.x/?ll={coords[0]},{coords[1]}&z={self.z}&size=450,450&l={self.map_type}")
                        self.coord1.setText(str(coords[0]))
                        self.coord2.setText(str(coords[1]))
                        self.label_3.setText(f'Поиск : {toponym["metaDataProperty"]["GeocoderMetaData"]["text"]}')
                        self.searcht = self.search.text()
                    except:
                        self.label_3.setText("Поиск : Некорректный запрос")
                        image = requests.get(
                                            f"https://static-maps.yandex.ru/1.x/?ll={coord1},{coord2}&z={self.z}&size=450,450&l={self.map_type}")
                else:
                    self.label_3.setText("Поиск : Ничего не найдено")
                    image = requests.get(
                        f"https://static-maps.yandex.ru/1.x/?ll={coord1},{coord2}&z={self.z}&size=450,450&l={self.map_type}")
            else:
                print(coord1, coord2)
                image = requests.get(f"https://static-maps.yandex.ru/1.x/?ll={coord1},{coord2}&z={self.z}&size=450,450&l={self.map_type}")
            out = open("Map.png", "wb")
            out.write(image.content)
            self.pixmap = image.content
            out.close()
            pixmap = QPixmap("Map.png")
            self.map.setPixmap(pixmap)
            self.map.resize(pixmap.width(), pixmap.height())
    
    def save_map(self):
        with open(f"map_saves\\map_save{str(datetime.datetime.now()).replace(':', '_')}.png", "wb") as map:
            map.write(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.button()
    ex.show()
    sys.exit(app.exec_())