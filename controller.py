from PyQt5.QtWidgets import QApplication, QCheckBox
import sys

from view import AppWindow, CheckboxesWindow
from model import Database


def start_program():
    global db, win

    app = QApplication(sys.argv)
    win = AppWindow()

    db = Database()

    win.show()
    sys.exit(app.exec_())


def make_output_string(entries: list[tuple]) -> str:
    if not entries:
        return "The database is empty"

    max_lengths = find_max_lengths(entries)
    string = f"{"id":>{3}}| {"Name":>{max_lengths[0]}}| {"Telephone number":>{max_lengths[1]}}| {"Comment":>{max_lengths[2]}}\n"
    string += "=" * (3 + sum(max_lengths) + 6) + '\n'
    for entry in entries:
        string += f"{entry[0]:>{3}}| {entry[1]:>{max_lengths[0]}}| {entry[2]:>{max_lengths[1]}}| {entry[3]:>{max_lengths[2]}}\n"
    string += "=" * (3 + sum(max_lengths) + 6)
    return string


def show_contacts():
    entries = db.get_contacts()
    win.change_text_edit(make_output_string(entries))


def find_max_lengths(entries: list) -> list[int]:
    max_lengths = [0, 0, 0]
    header = (4, 16, 7)  # lengths of "name", "telephone number" and "comment"
    for entry in entries:
        # fields of "entry": id, name, ph_number, comment
        # hence, we iterate through 1-3 indexes in entry and 0-2 indexes in max_lengths
        for i in range(1, len(entry)):
            max_lengths[i - 1] = max(max_lengths[i - 1], len(entry[i]), header[i - 1])

    return max_lengths


def add_new_contact():
    information, aborted = [], False
    for entry in ("Enter a name: ", "Enter a phone number: ", "Enter a comment: "):
        while 1:
            user_input, ok_pressed = win.get_input_text(entry)
            if ok_pressed:
                if not user_input:
                    win.info_message_box("Can't be empty")
                else:
                    information.append(user_input)
                    break
            else:
                aborted = True
                win.info_message_box("Operation aborted")
                break

        if aborted:
            break

    if not aborted:
        db.add_entry(information[0], information[1], information[2])
        win.info_message_box("The contact was successfully added")


def search_telephone_book():
    while 1:
        key, ok_pressed = win.get_input_text("Keywords: ")
        if ok_pressed:
            if not key:
                win.info_message_box("You must provide keywords")
            else:
                results = db.search(key)
                win.change_text_edit(
                    "The search result:\n\n" + make_output_string(results) if results else "There's no such contacts"
                )
                break
        else:
            break


def delete_or_change_contacts(delete: bool):
    show_contacts()
    operation = "delete" if delete else "change"

    while 1:
        key, ok_pressed = win.get_input_text(f"Enter a name of a contact to {operation}: ")
        if ok_pressed:
            if not key:
                win.info_message_box("Can't be empty")
            else:
                results = db.search(key, name_only=True)
                if not results:
                    if not win.prompt_yes_no("Not found", "No such contacts found, try again?"):
                        win.info_message_box("Operation aborted")
                        break
                else:
                    list_names = [f"{str(item[0])}. {item[1]}" for item in results]

                    if delete:
                        ch_win = CheckboxesWindow(f"What contacts would you like to {operation}?",
                                                  "Delete", list_names, mode="delete")
                        ch_win.exec_()
                    else:
                        radio_win = CheckboxesWindow(f"What contact would you like to {operation}?",
                                                     "Change", list_names, mode="change")
                        radio_win.exec_()

                    break
        else:
            win.info_message_box("Operation aborted")
            break


def submit_clicked_checkboxes(list_widget, dialogue_window, delete: bool, id_to_change: int = None):
    checked_items = []

    # Iterate through items in the QListWidget
    for i in range(list_widget.count()):
        item = list_widget.item(i)
        item_widget = list_widget.itemWidget(item)

        # Get the checkbox from the item widget
        checkbox = item_widget.findChild(QCheckBox)

        # Check if the checkbox is checked
        if checkbox.isChecked():
            checked_items.append(checkbox.text())

    if delete:
        delete_items(checked_items, dialogue_window)
    else:
        change_contacts(checked_items, dialogue_window, id_to_change)

    dialogue_window.accept()


def submit_clicked_radio(checked_button, dialogue_window):
    if checked_button:
        id = checked_button.text().split(".")[0]
        dialogue_window.accept()
        ch_win = CheckboxesWindow("What would you like to change?", "Change",
                                  ["Name", "Telephone number", "Comment"], mode="choose", id_to_change=id)
        ch_win.exec_()
    else:
        win.info_message_box("No contacts were changed")
        dialogue_window.reject()


def change_contacts(fields_to_change: list[str], dialogue_window, id_to_change: int):
    database_fields = {"Name": "name", "Telephone number": "number", "Comment": "comment"}
    for field in fields_to_change:
        change_to, ok_pressed = win.get_input_text(f"Enter a new {field.lower()}: ")
        if not ok_pressed:
            win.info_message_box("Operation aborted")
            dialogue_window.reject()
        else:
            db.change_entry(id_to_change, database_fields[field], change_to)
    win.info_message_box("Information was successfully updated")


def delete_items(checked_items: list, dialogue_window):
    if checked_items:
        this, s = ("these", "s") if len(checked_items) > 1 else ("this", "")
        if not win.prompt_yes_no("Delete?", f"Delete {this} contact{s}?\n{"\n".join(checked_items)}"):
            win.info_message_box("Operation aborted")
            dialogue_window.reject()
        else:
            for contact in checked_items:
                db.delete_entry(int(contact.split(".")[0]))
            db.vacuum()
            win.info_message_box("Contacts were successfully deleted")
            dialogue_window.accept()
    else:
        win.info_message_box("No contacts were deleted")
        dialogue_window.reject()


def handle_button_click(button_text):
    match button_text:
        case "Show contacts":
            show_contacts()

        case "Add a new contact":
            add_new_contact()

        case "Search in the telephone book":
            search_telephone_book()

        case "Change a contact":
            delete_or_change_contacts(delete=False)

        case "Delete a contact":
            delete_or_change_contacts(delete=True)

        case "Exit program":
            db.close()
            QApplication.exit()
