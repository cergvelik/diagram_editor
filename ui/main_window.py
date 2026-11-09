from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QComboBox, QLabel
)
from controllers.diagram_controller import DiagramController, export_diagram_to_excel
from ui.edit_window import EditWindow
from ui.plot_window import PlotWindow
import database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Визуальный редактор диаграмм")
        self.setMinimumSize(900, 600)

        self.opened_windows = []

        self._build_menu()
        self._build_ui()
        self._refresh_table()

    def _build_menu(self):
        mb = self.menuBar()

        fm = mb.addMenu("Файл")
        fm.addAction("Создать диаграмму", self._on_create)
        fm.addSeparator()
        fm.addAction("Экспорт", self._on_export)
        fm.addSeparator()
        fm.addAction("Выход", self.close)

        tm = mb.addMenu("Тип диаграммы")
        for t in ["bar", "line", "pie"]:
            tm.addAction(t, lambda checked, dt=t: self._create_with_type(dt))

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        btns = QHBoxLayout()
        b_create = QPushButton("Создать диаграмму")
        b_edit = QPushButton("Редактировать")
        b_plot = QPushButton("Просмотр")
        b_export = QPushButton("Экспорт")
        b_delete = QPushButton("Удалить")

        b_create.clicked.connect(self._on_create)
        b_edit.clicked.connect(self._on_open_edit)
        b_plot.clicked.connect(self._on_open_plot)
        b_export.clicked.connect(self._on_export)
        b_delete.clicked.connect(self._on_delete)

        btns.addWidget(b_create)
        btns.addWidget(b_edit)
        btns.addWidget(b_plot)
        btns.addWidget(b_export)
        btns.addWidget(b_delete)
        btns.addStretch()
        layout.addLayout(btns)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Фильтр по типу:")
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Все типы", "bar", "line", "pie"])
        self.filter_combo.currentIndexChanged.connect(self._refresh_table)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Тип", "Дата создания"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self.table)

    def _refresh_table(self):
        diagrams = database.get_all_diagrams()
        filter_type = self.filter_combo.currentText()
        if filter_type != "Все типы":
            diagrams = [d for d in diagrams if d.diagram_type == filter_type]

        self.table.setRowCount(len(diagrams))
        for i, d in enumerate(diagrams):
            self.table.setItem(i, 0, QTableWidgetItem(str(d.id)))
            self.table.setItem(i, 1, QTableWidgetItem(d.name))
            self.table.setItem(i, 2, QTableWidgetItem(d.diagram_type))
            dt = d.created_at.strftime("%Y-%m-%d %H:%M") if d.created_at else ""
            self.table.setItem(i, 3, QTableWidgetItem(dt))

    def _selected_id(self):
        sel = self.table.selectedItems()
        if sel:
            row = sel[0].row()
            id_item = self.table.item(row, 0)
            if id_item:
                return int(id_item.text())
        return None

    def _find_opened(self, diagram_id):
        for w in self.opened_windows:
            if w["controller"].diagram_id == diagram_id:
                return w
        return None

    def _on_create(self):
        controller = DiagramController()
        controller.reset()
        edit = EditWindow(controller)
        plot = PlotWindow(controller)
        controller.diagram_saved.connect(self._refresh_table)
        self.opened_windows.append({
            "controller": controller,
            "edit": edit,
            "plot": plot
        })
        edit.show()
        plot.show()

    def _create_with_type(self, dtype):
        controller = DiagramController()
        controller.reset()
        controller.set_type(dtype)
        edit = EditWindow(controller)
        plot = PlotWindow(controller)
        controller.diagram_saved.connect(self._refresh_table)
        self.opened_windows.append({
            "controller": controller,
            "edit": edit,
            "plot": plot
        })
        edit.show()
        plot.show()

    def _on_open_edit(self):
        did = self._selected_id()
        if did is None:
            QMessageBox.warning(self, "Внимание", "Выберите диаграмму из таблицы.")
            return
        self._open_edit_for(did)

    def _open_edit_for(self, did):
        opened = self._find_opened(did)
        if opened:
            if opened["edit"] is None:
                opened["edit"] = EditWindow(opened["controller"])
            opened["edit"].refresh()
            opened["edit"].show()
            opened["edit"].raise_()
            opened["edit"].activateWindow()
        else:
            controller = DiagramController()
            if not controller.load_from_db(did):
                QMessageBox.warning(self, "Ошибка", "Диаграмма не найдена.")
                return
            edit = EditWindow(controller)
            controller.diagram_saved.connect(self._refresh_table)
            self.opened_windows.append({
                "controller": controller,
                "edit": edit,
                "plot": None
            })
            edit.show()

    def _on_open_plot(self):
        did = self._selected_id()
        if did is None:
            QMessageBox.warning(self, "Внимание", "Выберите диаграмму из таблицы.")
            return
        self._open_plot_for(did)

    def _open_plot_for(self, did):
        opened = self._find_opened(did)
        if opened:
            if opened["plot"] is None:
                opened["plot"] = PlotWindow(opened["controller"])
            opened["plot"].show()
            opened["plot"].raise_()
            opened["plot"].activateWindow()
        else:
            controller = DiagramController()
            if not controller.load_from_db(did):
                QMessageBox.warning(self, "Ошибка", "Диаграмма не найдена.")
                return
            plot = PlotWindow(controller)
            controller.diagram_saved.connect(self._refresh_table)
            self.opened_windows.append({
                "controller": controller,
                "edit": None,
                "plot": plot
            })
            plot.show()

    def _on_double_click(self, index):
        row = index.row()
        id_item = self.table.item(row, 0)
        if id_item:
            did = int(id_item.text())
            self._open_edit_for(did)
            self._open_plot_for(did)

    def _on_export(self):
        did = self._selected_id()
        if did is None:
            QMessageBox.warning(self, "Внимание", "Выберите диаграмму для экспорта.")
            return
        diagram = database.get_diagram_by_id(did)
        if not diagram:
            QMessageBox.warning(self, "Ошибка", "Диаграмма не найдена.")
            return
        labels, values = database.get_diagram_data(did)
        try:
            path = export_diagram_to_excel(diagram, labels, values, parent=self)
            if path:
                QMessageBox.information(self, "Успех", f"Экспортировано в:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {e}")

    def _on_delete(self):
        did = self._selected_id()
        if did is None:
            QMessageBox.warning(self, "Внимание", "Выберите диаграмму для удаления.")
            return
        reply = QMessageBox.question(
            self, "Подтверждение", "Удалить выбранную диаграмму?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            database.delete_diagram(did)
            self._refresh_table()

    def closeEvent(self, event):
        for w in self.opened_windows:
            if w["edit"]:
                w["edit"].close()
            if w["plot"]:
                w["plot"].close()
        event.accept()