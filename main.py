import os
import gzip
import json
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, \
    QVBoxLayout, QWidget, QHeaderView, QLabel, QMessageBox, QLineEdit, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from libs.simple_logger import log, exc
from libs.contentv2_util import contentv2
from datetime import datetime
import glob
import getpass

some_text = ('srepene Patcher is a program that allows you to modify any strings in the Fall Guys game, <br>'
             'and then save them to a content_v2 or .ptch file, using a PyQT5 GUI. <br>'
             'The content_v2 editing is used to change strings, and does not trigger EAC.<br><br>'
             'Content_v2 usually is located at the path '
             f'C:\\Users\\{getpass.getuser()}\\Appdata\\LocalLow\\Mediatonic\\FallGuys_client <br><br>'
             'A little information about the buttons: <br>'
             'Open - Open the .gdata file that stores all the strings <br>'
             'Save - Save all your changes <br>'
             'Save Patch - Creates a .ptch file with all your changes <br>'
             'Apply Patch - Applies all changes from the .ptch file <br>'
             'Open 2 - Open a second .gdata file, and adds the data from it to the third column, might be useful '
             '<br><br>'
             'Also you can use HTML text formatting, like:  <br>'
             'Color (<a href="https://floyzi.ru/color">Gradient you can create here</a>), Scale, <i>Italic</i>, '
             '<b>Bold</b> and more... <br><br>'
             'You can find out more on the '
             '<a href="https://github.com/repinek/srepene_patcher">Github page</a> & '
             '<a href="https://gamebanana.com/tools/15284">Gamebanana page</a> <br>'
             'If you have found a bug, please report it to me via these links, or directly in my DM Discord or '
             'Telegram - @repinek <br>')


def create_data_folder():
    abs_path_todata = os.getcwd() + "/Data"

    if os.path.isdir(abs_path_todata):
        log("/Data exist")
    else:
        os.mkdir("Data")
        log("Created /Data directory")


# global variables
decoded_json_file_path = ""  # path to decoded json file
localised_strings = ""
decoded_json_file_path2 = ""  # open 2
abs_path_executed_file_first = os.getcwd()


class MainWindow(QMainWindow):
    def __init__(self):

        super().__init__()
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()

        # set window in center screen
        width = int(screen_rect.width() * 0.45)  # 45%
        height = int(screen_rect.height() * 0.45)
        x = int((screen_rect.width() - width) / 2)  # set window in center screen
        y = int((screen_rect.height() - height) / 2)
        self.setGeometry(x, y, width, height)  # yes

        # create buttons
        self.open_button = QPushButton("Open", self)
        self.save_button = QPushButton("Save", self)
        self.open2_button = QPushButton("Open 2", self)
        self.save_patch_button = QPushButton("Save Patch", self)
        self.apply_patch_button = QPushButton("Apply Patch", self)
        self.search_id_field = QLineEdit(self)
        self.search_text_field = QLineEdit(self)
        self.search_text2_field = QLineEdit(self)

        # sizes
        self.open_button.setFixedSize(70, 23)
        self.open2_button.setFixedSize(70, 23)
        self.save_patch_button.setFixedSize(70, 23)
        self.apply_patch_button.setFixedSize(70, 23)

        # buttons assignment
        self.open_button.clicked.connect(self.open_button_clicked)
        self.save_button.clicked.connect(self.save_button_clicked)
        self.open2_button.clicked.connect(self.open2_button_clicked)
        self.save_patch_button.clicked.connect(self.save_patch_button_clicked)
        self.apply_patch_button.clicked.connect(self.apply_patch_button_clicked)
        self.search_id_field.returnPressed.connect(self.search_id_field_trigger)
        self.search_text_field.returnPressed.connect(self.search_text_field_trigger)
        self.search_text2_field.returnPressed.connect(self.search_text2_field_trigger)

        # horizontal layout / buttons
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.open_button)
        h_layout.addWidget(self.save_button)
        h_layout.addWidget(self.open2_button)
        h_layout.addWidget(self.save_patch_button)
        h_layout.addWidget(self.apply_patch_button)
        h_layout.addStretch()  # stretch to the button to be on the left

        # vertical layout / other
        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.search_id_field)
        v_layout.addWidget(self.search_text_field)
        v_layout.addWidget(self.search_text2_field)

        # help label
        self.label = QLabel(self)
        self.label.setTextFormat(Qt.TextFormat.RichText)  # rich text
        self.label.setText(some_text)
        self.label.setOpenExternalLinks(True)  # clickable links
        self.label.setStyleSheet("font-size: 16px;")
        self.label.setAlignment(QtCore.Qt.AlignLeft)  # alignment left
        v_layout.addWidget(self.label)  # add to vertical layout

        # table
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["ID", "Text"])
        v_layout.addWidget(self.table_widget)  # add to vertical layout

        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

        self.setWindowTitle("srepene Patcher [Release v1.1]")
        self.search_id_field.setPlaceholderText("ID Search")
        self.search_text_field.setPlaceholderText("Text Search")
        self.search_text2_field.setPlaceholderText("Text 2 Search")

        # Visible and Enable
        self.table_widget.setVisible(False)
        self.search_id_field.setVisible(False)
        self.search_text_field.setVisible(False)
        self.search_text2_field.setVisible(False)

        self.save_button.setEnabled(False)
        self.open2_button.setEnabled(False)
        self.save_patch_button.setEnabled(False)
        self.apply_patch_button.setEnabled(False)

    def open_button_clicked(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "", "", "GData Files (*.gdata)")  # select file dialog
        if file_path:
            log(f"Selected file: {file_path}")
            self.apply_code_to_file(file_path)  # process decode gdata

    def apply_code_to_file(self, file_path):
        global decoded_json_file_path
        global localised_strings
        global abs_path_executed_file_first

        decoded_to_gz_file_path = contentv2(file_path, "temp.gz")  # return temp.gz path
        current_time = datetime.now().strftime('%H-%M-%S')  # using for prevent duplicates
        decoded_json_file_path = abs_path_executed_file_first + "/Data/" + os.path.basename(
            file_path) + f"_decoded_{current_time}.json"  # path to unzipped gz file

        if os.path.isfile(decoded_json_file_path):
            exc(f"The file named {decoded_json_file_path} already exists")
            QMessageBox.warning(None, "Error", f"The file named {decoded_json_file_path} already exists")
            return

        duplicates = glob.glob("Data/" + os.path.basename(file_path) + "_decoded_**-**-**.json")
        for path in duplicates:
            if path != os.path.basename(decoded_json_file_path) or os.path.basename(decoded_json_file_path2):
                os.remove(path)
                log(f"Deleted {path}")

        # unzip gz
        with gzip.open(decoded_to_gz_file_path, 'rb') as archived_gz_json_file:
            with open(decoded_json_file_path, 'wb') as decoded_json_file:
                decoded_json_file.write(archived_gz_json_file.read())
        log(f"Unzipped to: {decoded_json_file_path}")

        os.remove(decoded_to_gz_file_path)
        log(f"Deleted {decoded_to_gz_file_path}")

        with open(decoded_json_file_path, 'r', encoding="utf-8") as json_file:
            try:
                decoded_file_json_data = json.load(json_file)
            except json.JSONDecodeError:
                exc("gdata file is corrupted")
                QMessageBox.warning(None, "Error", "Your gdata file is corrupted")
                return
            localised_strings = decoded_file_json_data.get(
                "localised_strings")  # get localised strings from _decoded.json
            if localised_strings:
                self.populate_table(localised_strings)

            else:  # blind code
                exc("File does not have a localized_strings subsection")
                QMessageBox.warning(None, "Error", "the selected file does not have a localized_strings subsection")
                return

    def populate_table(self, localised_strings_from_file):
        self.table_widget.setRowCount(len(localised_strings_from_file))  # set row count = strings count
        for row, item in enumerate(localised_strings_from_file):
            id_item = QTableWidgetItem(str(item.get("id", "")))
            text_item = QTableWidgetItem(str(item.get("text", "")))
            id_item.setFlags(id_item.flags() & ~QtCore.Qt.ItemIsEditable)  # prevent editing of id
            self.table_widget.setItem(row, 0, id_item)  # set id
            self.table_widget.setItem(row, 1, text_item)  # set text
            self.table_widget.setRowHeight(row, 6)

        self.table_widget.resizeColumnsToContents()  # stretching columns
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # do not allow resizing when the window is resized too
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # allow resizing when the window is resized too

        # set visible and enable
        self.search_id_field.setVisible(True)
        self.search_text_field.setVisible(True)
        self.table_widget.setVisible(True)
        self.label.setVisible(False)
        self.save_button.setEnabled(True)
        self.open2_button.setEnabled(True)
        self.save_patch_button.setEnabled(True)
        self.apply_patch_button.setEnabled(True)

        log("Table is completed")

    def populate_table2(self, localised_strings_from_file):
        self.table_widget.setColumnCount(3)  # add 3 column
        for row in range(self.table_widget.rowCount()):
            id_0_column = self.table_widget.item(row, 0).text()
            for item in localised_strings_from_file:
                if item["id"] == id_0_column:
                    text = item["text"]
                    self.table_widget.setItem(row, 2, QTableWidgetItem(text))
                    break  # stop searching after match

        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # allow resizing when the window is resized too
        self.table_widget.setHorizontalHeaderLabels(["ID", "Text", "Text 2"])
        self.search_text2_field.setVisible(True)
        log("The table is filled with second content")

    def save_button_clicked(self):
        global decoded_json_file_path
        QMessageBox.warning(None, "Warning", "NOTE:\n"
                                             "Once content_v2 is updated by the game all of your changes will be "
                                             "reset, so make a .ptch file before you save it.\n"
                                             "After content_v2 is updated by the game, do these steps:\n"
                                             "open the new content file, apply the patch and overwrite the new "
                                             "content file\n")
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, "", "", "GData Files (*.gdata)")
        if save_path:
            log(f"Selected save path: {save_path}")
            with open(decoded_json_file_path, "r", encoding="utf-8") as decoded_json_file:
                data = json.load(decoded_json_file)
            data["localised_strings"] = []  # clear localised strings

            for row in range(self.table_widget.rowCount()):
                id_item = self.table_widget.item(row, 0)  # id
                text_item = self.table_widget.item(row, 1)  # text
                id_value = id_item.text() if id_item else ""
                text_value = text_item.text() if text_item else ""
                data["localised_strings"].append({"id": id_value, "text": text_value})  # append to json

                # for real, I do not know how to clean code here
            with open(decoded_json_file_path, "w") as decoded_json_file:
                json.dump(data, decoded_json_file)
            log("Successful dump json file")

            with open(decoded_json_file_path, 'rb') as f_in:
                with gzip.open("temp.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            log("Created temp.gz file")

            contentv2("temp.gz", save_path)
            os.remove("temp.gz")
            log("Deleted temp.gz")
            QMessageBox.information(None, "Successfully", "Successfully Saved: " + save_path)

    def apply_patch_button_clicked(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "", "", "Patch Files (*.ptch)")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as patch_file:
                patch_data = patch_file.readlines()

            for patch_line in patch_data:
                patch_parts = patch_line.strip().split("|")  # split it to id and text
                patch_id = patch_parts[0]  # id
                patch_text = patch_parts[1]  # text

                for row in range(self.table_widget.rowCount()):
                    id_item = self.table_widget.item(row, 0)
                    if id_item.text() == patch_id:  # .text() because object
                        text_item = QTableWidgetItem(patch_text)  # object
                        self.table_widget.setItem(row, 1, text_item)  # set item
                        break
            log("Patch successfully applied")

    def save_patch_button_clicked(self):
        file_dialog = QFileDialog()
        save_path, _ = file_dialog.getSaveFileName(self, "", "", "Patch Files (*.ptch)")
        if save_path:
            patch_data = ""
            for row in range(self.table_widget.rowCount()):
                id_item = self.table_widget.item(row, 0)  # object
                text_item = self.table_widget.item(row, 1)
                id_value = id_item.text() if id_item else ""  # become string
                text_value = text_item.text() if text_item else ""
                if id_value and text_value:
                    for string in localised_strings:
                        if string['id'] == id_value and string['text'] != text_value:
                            patch_data += f"{id_value}|{text_value}\n"
                            break
                        elif string['id'] == id_value and string['text'] == text_value:
                            break
            with open(save_path, "w", encoding="utf-8") as file:
                file.write(patch_data)
            log("Patch successfully saved")
            QMessageBox.information(None, "Info", "Successfully Saved")

    # search fields
    def search_id_field_trigger(self):
        search_text = self.search_id_field.text().lower()
        rows = self.table_widget.rowCount()
        for row in range(rows):
            item = self.table_widget.item(row, 0)
            if item is not None:
                text = item.text().lower()
                if search_text in text:
                    self.table_widget.showRow(row)  # show if true
                else:
                    self.table_widget.hideRow(row)  # hide if false

    def search_text_field_trigger(self):
        search_text = self.search_text_field.text().lower()
        rows = self.table_widget.rowCount()
        for row in range(rows):
            item = self.table_widget.item(row, 1)
            if item is not None:
                text = item.text().lower()
                if search_text in text:
                    self.table_widget.showRow(row)
                else:
                    self.table_widget.hideRow(row)

    def search_text2_field_trigger(self):
        search_text = self.search_text2_field.text().lower()
        rows = self.table_widget.rowCount()
        for row in range(rows):
            item = self.table_widget.item(row, 2)
            if item is not None:
                text = item.text().lower()
                if search_text in text:
                    self.table_widget.showRow(row)
                else:
                    self.table_widget.hideRow(row)

    def open2_button_clicked(self):
        global decoded_json_file_path2
        # all code is literally open function, there will be no comments
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "", "", "GData Files (*.gdata)")
        if file_path:
            decoded_to_gz_file_path = contentv2(file_path, "temp.gz")
            current_time = datetime.now().strftime('%H-%M-%S')
            decoded_json_file_path2 = abs_path_executed_file_first + "/Data/" + os.path.basename(
                file_path) + f"_decoded_{current_time}.json"

            if os.path.isfile(decoded_json_file_path2):
                exc(f"The file named {decoded_json_file_path} already exists")
                QMessageBox.warning(None, "Error", f"The file named {decoded_json_file_path} already exists")
                return

            duplicates = glob.glob("Data/" + os.path.basename(file_path) + "_decoded_**-**-**.json")
            for path in duplicates:
                if path != os.path.basename(decoded_json_file_path) or os.path.basename(decoded_json_file_path2):
                    os.remove(path)
                    log(f"Deleted {path}")

            with gzip.open(decoded_to_gz_file_path, 'rb') as archived_gz_json_file:
                with open(decoded_json_file_path2, 'wb') as decoded_json_file:
                    decoded_json_file.write(archived_gz_json_file.read())
            log(f"Unzipped to: {decoded_json_file_path2}")

            os.remove(decoded_to_gz_file_path)
            log(f"Deleted {decoded_to_gz_file_path}")

            with open(decoded_json_file_path2, 'r', encoding="utf-8") as json_file:
                try:
                    decoded_file_json_data = json.load(json_file)
                except json.JSONDecodeError:
                    exc("gdata file is corrupted")
                    QMessageBox.warning(None, "Error", "Your gdata file is corrupted")
                    return
                localised_strings2 = decoded_file_json_data.get(
                    "localised_strings")
                if localised_strings2:
                    self.populate_table2(localised_strings2)
                    self.open_button.setEnabled(False)
                    self.open2_button.setEnabled(False)
                else:  # blind code
                    exc("File does not have a localized_strings subsection")
                    QMessageBox.warning(None, "Error", "the selected file does not have a localized_strings subsection")
                    return


if __name__ == "__main__":
    app = QApplication([])
    create_data_folder()
    window = MainWindow()
    window.show()
    app.exec_()
