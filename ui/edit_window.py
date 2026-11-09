from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFormLayout, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QGroupBox, QMessageBox,
    QHeaderView
)


class EditWindow(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self._loading = False 
        self.setWindowTitle("Редактор данных диаграммы")
        self.setMinimumSize(520, 620)
        self._build_ui()
        self._sync_from_controller()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        params = QGroupBox("Параметры")
        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems(["bar", "line", "pie"])
        form.addRow("Название:", self.name_edit)
        form.addRow("Тип:", self.type_combo)
        params.setLayout(form)
        layout.addWidget(params)

        data_group = QGroupBox("Данные")
        data_layout = QVBoxLayout(data_group)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Метка", "Значение"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        data_layout.addWidget(self.table)

        btn_grid = QGridLayout()
        btn_add = QPushButton("+ Добавить строку")
        btn_del = QPushButton("− Удалить строку")
        btn_grid.addWidget(btn_add, 0, 0)
        btn_grid.addWidget(btn_del, 0, 1)
        data_layout.addLayout(btn_grid)
        layout.addWidget(data_group)

        settings_group = QGroupBox("Настройки отображения")
        sform = QFormLayout()
        self.title_edit = QLineEdit()
        self.xlabel_edit = QLineEdit()
        self.ylabel_edit = QLineEdit()
        sform.addRow("Заголовок:", self.title_edit)
        sform.addRow("Ось X:", self.xlabel_edit)
        sform.addRow("Ось Y:", self.ylabel_edit)
        settings_group.setLayout(sform)
        layout.addWidget(settings_group)

        save_row = QHBoxLayout()
        btn_save = QPushButton("Сохранить в БД")
        save_row.addStretch()
        save_row.addWidget(btn_save)
        layout.addLayout(save_row)

        self.name_edit.textChanged.connect(self._on_name)
        self.type_combo.currentTextChanged.connect(self._on_type)
        self.table.cellChanged.connect(self._on_cell)
        btn_add.clicked.connect(self._add_row)
        btn_del.clicked.connect(self._del_row)
        self.title_edit.textChanged.connect(self._on_title)
        self.xlabel_edit.textChanged.connect(self._on_xlabel)
        self.ylabel_edit.textChanged.connect(self._on_ylabel)
        btn_save.clicked.connect(self._on_save)

        self._loading = True
        for _ in range(3):
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(""))
            self.table.setItem(r, 1, QTableWidgetItem("0"))
        self._loading = False

    def _sync_from_controller(self):
        self._loading = True

        self.name_edit.blockSignals(True)
        self.type_combo.blockSignals(True)
        self.table.blockSignals(True)
        self.title_edit.blockSignals(True)
        self.xlabel_edit.blockSignals(True)
        self.ylabel_edit.blockSignals(True)

        self.name_edit.setText(self.controller.name)
        idx = self.type_combo.findText(self.controller.diagram_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)

        self.table.setRowCount(0)
        labels = self.controller.labels
        values = self.controller.values
        if labels and values:
            for lb, vl in zip(labels, values):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(str(lb)))
                self.table.setItem(r, 1, QTableWidgetItem(str(vl)))
        else:
            for _ in range(3):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.table.setItem(r, 0, QTableWidgetItem(""))
                self.table.setItem(r, 1, QTableWidgetItem("0"))

        self.title_edit.setText(self.controller.title)
        self.xlabel_edit.setText(self.controller.xlabel)
        self.ylabel_edit.setText(self.controller.ylabel)

        self.name_edit.blockSignals(False)
        self.type_combo.blockSignals(False)
        self.table.blockSignals(False)
        self.title_edit.blockSignals(False)
        self.xlabel_edit.blockSignals(False)
        self.ylabel_edit.blockSignals(False)

        self._loading = False

    def refresh(self):
        self._sync_from_controller()

    def _on_name(self, text):
        if not self._loading:
            self.controller.set_name(text)

    def _on_type(self, text):
        if not self._loading:
            self.controller.set_type(text)

    def _on_cell(self, row, col):
        if self._loading:
            return

        if col == 1:
            item = self.table.item(row, col)
            if item:
                text = item.text().strip()
                if text:
                    try:
                        float(text)
                    except ValueError:
                        self._loading = True
                        item.setText("")
                        self._loading = False
                        QMessageBox.warning(
                            self, "Ошибка ввода",
                            f"Некорректное значение в строке {row + 1}.\n"
                            f"Введите числовое значение."
                        )
                        return

        self._push_table_data()

    def _on_title(self, text):
        if not self._loading:
            self.controller.set_title(text)

    def _on_xlabel(self, text):
        if not self._loading:
            self.controller.set_xlabel(text)

    def _on_ylabel(self, text):
        if not self._loading:
            self.controller.set_ylabel(text)

    def _push_table_data(self):
        if self._loading:
            return
        labels, values = [], []
        for r in range(self.table.rowCount()):
            li = self.table.item(r, 0)
            vi = self.table.item(r, 1)
            if li and vi:
                lb = li.text().strip()
                try:
                    vl = float(vi.text().strip())
                    if lb:
                        labels.append(lb)
                        values.append(vl)
                except ValueError:
                    pass
        self.controller.set_data(labels, values)

    def _add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(""))
        self.table.setItem(r, 1, QTableWidgetItem("0"))
        self._push_table_data()

    def _del_row(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)
            self._push_table_data()

    def _on_save(self):
        self._push_table_data()
        try:
            self.controller.save_to_db()
            QMessageBox.information(self, "Успех", "Диаграмма сохранена в БД.")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")