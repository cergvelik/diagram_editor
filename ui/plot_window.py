import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QMessageBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class PlotWindow(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowTitle("Просмотр диаграммы")
        self.setMinimumSize(650, 520)

        layout = QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        btn_row = QHBoxLayout()
        btn_save = QPushButton("Сохранить изображение")
        btn_save.clicked.connect(self._save_image)
        btn_row.addStretch()
        btn_row.addWidget(btn_save)
        layout.addLayout(btn_row)

        self.controller.data_changed.connect(self._redraw)
        self._redraw()

    def _redraw(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        labels = self.controller.labels
        values = self.controller.values
        dtype = self.controller.diagram_type

        if not labels or not values:
            ax.text(0.5, 0.5, "Нет данных для отображения",
                    ha="center", va="center", fontsize=16,
                    transform=ax.transAxes)
            ax.axis("off")
            self.canvas.draw()
            return

        values = [float(v) for v in values]

        if all(v == 0 for v in values):
            ax.text(0.5, 0.5, "Все значения равны нулю.\nВведите ненулевые данные.",
                    ha="center", va="center", fontsize=14,
                    transform=ax.transAxes)
            ax.axis("off")
            self.canvas.draw()
            return

        if dtype == "pie" and any(v <= 0 for v in values):
            ax.text(0.5, 0.5, "Для круговой диаграммы все значения должны быть > 0",
                    ha="center", va="center", fontsize=14,
                    transform=ax.transAxes)
            ax.axis("off")
            self.canvas.draw()
            return

        try:
            if dtype == "bar":
                x = np.arange(len(labels))
                bars = ax.bar(x, values, width=0.6, color="steelblue", edgecolor="white")
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=45, ha="right")
                for bar, val in zip(bars, values):
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                            f"{val:g}", ha="center", va="bottom", fontsize=9)

            elif dtype == "line":
                x = np.arange(len(labels))
                ax.plot(x, values, marker="o", color="steelblue", linewidth=2, markersize=6)
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=45, ha="right")
                ax.grid(True, alpha=0.3)

            elif dtype == "pie":
                ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
                ax.axis("equal")

        except ValueError as e:
            ax.clear()
            ax.text(0.5, 0.5, f"Ошибка построения:\n{str(e)}",
                    ha="center", va="center", fontsize=12,
                    transform=ax.transAxes)
            ax.axis("off")

        # Настройки
        title = self.controller.title or self.controller.name
        if title:
            ax.set_title(title, fontsize=13, fontweight="bold")
        if dtype != "pie":
            if self.controller.xlabel:
                ax.set_xlabel(self.controller.xlabel)
            if self.controller.ylabel:
                ax.set_ylabel(self.controller.ylabel)

        self.figure.tight_layout()
        self.canvas.draw()

    def _save_image(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "",
            "PNG (*.png);;SVG (*.svg)"
        )
        if path:
            self.figure.savefig(path, dpi=150, bbox_inches="tight")
            QMessageBox.information(self, "Успех", f"Сохранено: {path}")