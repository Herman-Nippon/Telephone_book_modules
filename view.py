from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget, QHBoxLayout, QInputDialog, \
    QMessageBox, QListWidget, QCheckBox, QListWidgetItem, QDialog, QLabel, QButtonGroup, QRadioButton

import controller


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telephone Book")
        self.setGeometry(200, 200, 500, 500)  # ax, ay, width, height
        self.init_layout()

    def init_layout(self):
        main_layout = QVBoxLayout()

        buttons_layout = [
            ("Show contacts", "Add a new contact", "Change a contact", "Delete a contact"),
            ("Search in the telephone book", "Exit program")
        ]

        for row_buttons in buttons_layout:
            row_layout = QHBoxLayout()
            for button_text in row_buttons:
                button = QPushButton(button_text)
                row_layout.addWidget(button)

                # for some reason in this specific case you need to use
                # lambda with an anonymous variable
                # it doesn't work otherwise
                button.clicked.connect(lambda _, text=button_text: controller.handle_button_click(text))

            main_layout.addLayout(row_layout)

        # add and configure the text box inside the main window
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFontFamily("Consolas")
        self.text_edit.setFontPointSize(11)
        main_layout.addWidget(self.text_edit)

        # setting up a "central widget" with all the elements
        # because otherwise nothing is shown in the window
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def change_text_edit(self, new_text: str):
        self.text_edit.setText(new_text)

    def get_input_text(self, label_text: str) -> tuple[str, bool]:
        # getText returns a tuple (text, bool)
        # bool indicates if "Cancel" button was pressed: False if pressed, True otherwise
        return QInputDialog.getText(self, "Input", label_text)

    def prompt_yes_no(self, title: str, message: str) -> bool:
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg_box.setDefaultButton(QMessageBox.Ok)

        # method returns either True or False, depending on the user answer
        return msg_box.exec() == QMessageBox.Ok

    def info_message_box(self, message: str):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Info")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


class CheckboxesWindow(QDialog):
    def __init__(self, label_text: str, window_title: str, items: list[str], mode: str, id_to_change: int = None):
        super().__init__()
        if id_to_change:
            self.id = id_to_change
        self.label_text = label_text
        self.mode = mode
        self.setWindowTitle(window_title)
        self.init_ui(items)

    def init_ui(self, items: list[str]):
        main_layout = QVBoxLayout(self)
        layout = QVBoxLayout()

        label = QLabel(self.label_text)
        main_layout.addWidget(label)

        # create QListWidget
        self.list_widget = QListWidget(self)

        if self.mode == "change":
            # create a button group for radio buttons
            self.radio_group = QButtonGroup()

        # add items with checkboxes
        for index, item_text in enumerate(items):
            item_widget = QWidget(self)
            item_layout = QHBoxLayout(item_widget)

            if self.mode in ("delete", "choose"):
                # create a checkbox
                checkbox = QCheckBox()
                checkbox.setText(item_text)

            else:
                # create a radio button
                checkbox = QRadioButton()
                checkbox.setText(item_text)

            # add the radio button or checkbox to the layout
            item_layout.addWidget(checkbox)

            # create a QListWidgetItem and set its widget
            item = QListWidgetItem(self.list_widget)
            item.setSizeHint(item_widget.sizeHint())  # set the size hint for correct layout
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, item_widget)

            if self.mode == "change":
                # add the radio button to the radio group
                self.radio_group.addButton(checkbox, index)

        layout.addWidget(self.list_widget)

        # add a submit button
        submit_button = QPushButton("Submit", self)

        if self.mode == "delete":
            submit_button.clicked.connect(
                lambda: controller.submit_clicked_checkboxes(self.list_widget, self, delete=True)
            )
        elif self.mode == "change":
            submit_button.clicked.connect(
                lambda: controller.submit_clicked_radio(self.radio_group.checkedButton(), self)
            )
        else:
            submit_button.clicked.connect(
                lambda: controller.submit_clicked_checkboxes(self.list_widget, self, delete=False, id_to_change=self.id)
            )

        layout.addWidget(submit_button)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)
