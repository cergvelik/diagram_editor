from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog
import pandas as pd
import database


class DiagramController(QObject):
    data_changed = pyqtSignal()
    diagram_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._diagram_id = None
        self._name = ""
        self._diagram_type = "bar"
        self._labels = []
        self._values = []
        self._title = ""
        self._xlabel = ""
        self._ylabel = ""

    @property
    def diagram_id(self):
        return self._diagram_id

    @property
    def name(self):
        return self._name

    @property
    def diagram_type(self):
        return self._diagram_type

    @property
    def labels(self):
        return list(self._labels)

    @property
    def values(self):
        return list(self._values)

    @property
    def title(self):
        return self._title

    @property
    def xlabel(self):
        return self._xlabel

    @property
    def ylabel(self):
        return self._ylabel

    def set_name(self, name):
        self._name = name
        self.data_changed.emit()

    def set_type(self, dtype):
        self._diagram_type = dtype
        self.data_changed.emit()

    def set_data(self, labels, values):
        self._labels = list(labels)
        self._values = list(values)
        self.data_changed.emit()

    def set_title(self, t):
        self._title = t
        self.data_changed.emit()

    def set_xlabel(self, t):
        self._xlabel = t
        self.data_changed.emit()

    def set_ylabel(self, t):
        self._ylabel = t
        self.data_changed.emit()

    def reset(self):
        self._diagram_id = None
        self._name = ""
        self._diagram_type = "bar"
        self._labels = []
        self._values = []
        self._title = ""
        self._xlabel = ""
        self._ylabel = ""
        self.data_changed.emit()

    def load_from_db(self, diagram_id):
        diagram = database.get_diagram_by_id(diagram_id)
        if not diagram:
            return False
        self._diagram_id = diagram.id
        self._name = diagram.name
        self._diagram_type = diagram.diagram_type
        self._title = diagram.title or ""
        self._xlabel = diagram.xlabel or ""
        self._ylabel = diagram.ylabel or ""
        self._labels, self._values = database.get_diagram_data(diagram_id)
        self.data_changed.emit()
        return True

    def save_to_db(self):
        if not self._name.strip():
            raise ValueError("Название диаграммы не может быть пустым.")
        if not self._labels or not self._values:
            raise ValueError("Данные не могут быть пустыми.")
        if len(self._labels) != len(self._values):
            raise ValueError("Количество меток и значений не совпадает.")

        if self._diagram_id:
            database.update_diagram(
                self._diagram_id, self._name, self._diagram_type,
                self._labels, self._values,
                self._title, self._xlabel, self._ylabel
            )
        else:
            new = database.create_diagram(
                self._name, self._diagram_type,
                self._labels, self._values,
                self._title, self._xlabel, self._ylabel
            )
            self._diagram_id = new.id
        self.diagram_saved.emit()


def export_diagram_to_excel(diagram, labels, values, parent=None):
    default_name = f"{diagram.name}.xlsx" if diagram.name else "diagram.xlsx"
    path, _ = QFileDialog.getSaveFileName(
        parent, "Сохранить данные диаграммы", default_name,
        "Excel Files (*.xlsx)"
    )
    if not path:
        return None

    diagram_df = pd.DataFrame([{
        "ID": diagram.id,
        "Название": diagram.name,
        "Тип": diagram.diagram_type,
        "Заголовок": diagram.title or "",
        "Ось X": diagram.xlabel or "",
        "Ось Y": diagram.ylabel or ""
    }])

    data_df = pd.DataFrame({
        "Позиция": list(range(1, len(labels) + 1)),
        "Метка": labels,
        "Значение": values
    })

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        diagram_df.to_excel(writer, sheet_name="Диаграмма", index=False)
        data_df.to_excel(writer, sheet_name="Данные", index=False)

    return path