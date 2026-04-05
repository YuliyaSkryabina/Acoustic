"""
QGIS плагин Акустик.
Загружает данные из API http://localhost:8765 и создаёт слои QGIS.
"""
from __future__ import annotations

import json
import urllib.request
import urllib.error

try:
    from qgis.PyQt.QtWidgets import (
        QAction, QDialog, QVBoxLayout, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QMessageBox,
        QGroupBox, QCheckBox,
    )
    from qgis.PyQt.QtGui import QIcon, QColor
    from qgis.PyQt.QtCore import Qt
    from qgis.core import (
        QgsProject, QgsVectorLayer, QgsFeature,
        QgsGeometry, QgsPointXY, QgsField, QgsFields,
        QgsSymbol, QgsSingleSymbolRenderer,
        QgsGraduatedSymbolRenderer, QgsRendererRange,
        QgsMarkerSymbol, QgsLineSymbol,
        QgsSimpleMarkerSymbolLayer, QgsSimpleLineSymbolLayer,
    )
    from qgis.core import QgsWkbTypes
    from PyQt5.QtCore import QVariant
    QGIS_AVAILABLE = True
except ImportError:
    QGIS_AVAILABLE = False


API_BASE = "http://127.0.0.1:8765"

# Цветовая схема изолиний: уровень дБА → цвет
ISOLINE_COLORS = {
    30: "#2196F3",
    35: "#42A5F5",
    40: "#4CAF50",
    45: "#8BC34A",
    50: "#CDDC39",
    55: "#FFC107",   # граница жилой нормы днём
    60: "#FF7043",
    65: "#F44336",
    70: "#B71C1C",
    75: "#880E4F",
    80: "#4A148C",   # граница промышленной нормы
}


def _api_get(endpoint: str) -> dict:
    """HTTP GET к API Акустик."""
    url = f"{API_BASE}{endpoint}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _api_post(endpoint: str, data: dict) -> dict:
    """HTTP POST к API Акустик."""
    url = f"{API_BASE}{endpoint}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


class AcoustikPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.actions: list = []
        self.menu = "Акустик"
        self.toolbar = None

    def initGui(self):
        """Инициализация UI плагина."""
        self.action_load = QAction("Загрузить данные Акустик", self.iface.mainWindow())
        self.action_load.triggered.connect(self.show_dialog)
        self.iface.addToolBarIcon(self.action_load)
        self.iface.addPluginToMenu(self.menu, self.action_load)
        self.actions.append(self.action_load)

    def unload(self):
        """Удаление UI плагина."""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)

    def show_dialog(self):
        """Показать диалог загрузки данных."""
        dlg = AcoustikDialog(self.iface)
        dlg.exec_()


class AcoustikDialog(QDialog):
    def __init__(self, iface):
        super().__init__(iface.mainWindow())
        self.iface = iface
        self.setWindowTitle("Акустик — загрузка данных")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Проект ID
        project_group = QGroupBox("Проект")
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Project ID:"))
        self.project_id_edit = QLineEdit("default_project")
        project_layout.addWidget(self.project_id_edit)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)

        # Слои для загрузки
        layers_group = QGroupBox("Загрузить слои")
        layers_layout = QVBoxLayout()
        self.cb_sources = QCheckBox("Источники шума (точки)")
        self.cb_sources.setChecked(True)
        self.cb_points = QCheckBox("Расчётные точки с результатами")
        self.cb_points.setChecked(True)
        self.cb_isolines = QCheckBox("Изолинии уровней шума")
        self.cb_isolines.setChecked(True)
        layers_layout.addWidget(self.cb_sources)
        layers_layout.addWidget(self.cb_points)
        layers_layout.addWidget(self.cb_isolines)
        layers_group.setLayout(layers_layout)
        layout.addWidget(layers_group)

        # Статус подключения
        self.status_label = QLabel("Не подключено")
        self.status_label.setStyleSheet("color: gray;")
        layout.addWidget(self.status_label)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_check = QPushButton("Проверить подключение")
        btn_check.clicked.connect(self.check_connection)
        btn_load = QPushButton("Загрузить")
        btn_load.clicked.connect(self.load_layers)
        btn_load.setDefault(True)
        btn_cancel = QPushButton("Отмена")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_check)
        btn_layout.addWidget(btn_load)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def check_connection(self):
        try:
            result = _api_get("/health")
            self.status_label.setText(f"✓ Подключено: {result.get('service', 'API')}")
            self.status_label.setStyleSheet("color: green;")
        except Exception as e:
            self.status_label.setText(f"✗ Ошибка: {e}")
            self.status_label.setStyleSheet("color: red;")

    def load_layers(self):
        project_id = self.project_id_edit.text().strip()
        if not project_id:
            QMessageBox.warning(self, "Ошибка", "Введите Project ID")
            return

        errors = []

        if self.cb_sources.isChecked():
            try:
                self._load_sources_layer(project_id)
            except Exception as e:
                errors.append(f"Источники: {e}")

        if self.cb_points.isChecked():
            try:
                self._load_points_layer(project_id)
            except Exception as e:
                errors.append(f"Расчётные точки: {e}")

        if self.cb_isolines.isChecked():
            try:
                self._load_isolines_layer(project_id)
            except Exception as e:
                errors.append(f"Изолинии: {e}")

        if errors:
            QMessageBox.warning(self, "Ошибки загрузки", "\n".join(errors))
        else:
            QMessageBox.information(self, "Готово", "Слои загружены успешно!")
            self.accept()

    def _load_sources_layer(self, project_id: str):
        """Загрузить источники шума как точечный слой."""
        data = _api_get(f"/sources/?project_id={project_id}")

        layer = QgsVectorLayer("Point?crs=EPSG:4326", "ИШ — Источники шума", "memory")
        pr = layer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        fields.append(QgsField("description", QVariant.String))
        fields.append(QgsField("source_type", QVariant.String))
        fields.append(QgsField("x", QVariant.Double))
        fields.append(QgsField("y", QVariant.Double))
        pr.addAttributes(fields)
        layer.updateFields()

        features = []
        for src in data:
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(src["x"], src["y"])))
            feat.setAttributes([
                src.get("id", ""),
                src.get("description", ""),
                src.get("source_type", "point"),
                src.get("x", 0),
                src.get("y", 0),
            ])
            features.append(feat)

        pr.addFeatures(features)
        layer.updateExtents()

        # Символ: красный кружок
        symbol = QgsMarkerSymbol.createSimple({
            "color": "#E53935",
            "size": "6",
            "outline_color": "white",
            "outline_width": "0.5",
        })
        layer.setRenderer(QgsSingleSymbolRenderer(symbol))

        QgsProject.instance().addMapLayer(layer)

    def _load_points_layer(self, project_id: str):
        """Загрузить расчётные точки с результатами."""
        export_data = _api_post(f"/export_to_qgis/?project_id={project_id}", {})
        features_data = export_data.get("results_geojson", {}).get("features", [])

        layer = QgsVectorLayer("Point?crs=EPSG:4326", "РТ — Расчётные точки", "memory")
        pr = layer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("id", QVariant.String))
        fields.append(QgsField("l_a_eq_day", QVariant.Double))
        fields.append(QgsField("l_a_eq_night", QVariant.Double))
        fields.append(QgsField("exceeded_day", QVariant.Bool))
        pr.addAttributes(fields)
        layer.updateFields()

        for f in features_data:
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [0, 0])
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coords[0], coords[1])))
            feat.setAttributes([
                props.get("id", ""),
                props.get("l_a_eq_day"),
                props.get("l_a_eq_night"),
                props.get("exceeded_day", False),
            ])
            pr.addFeature(feat)

        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer)

    def _load_isolines_layer(self, project_id: str):
        """Загрузить изолинии уровней шума как линейный слой."""
        export_data = _api_post(f"/export_to_qgis/?project_id={project_id}", {})
        sources_data = export_data.get("sources_geojson", {}).get("features", [])

        # Изолинии нужно пересчитать через API
        # Пока создаём пустой слой как заглушку
        layer = QgsVectorLayer("LineString?crs=EPSG:4326", "Изолинии уровней шума", "memory")
        pr = layer.dataProvider()

        fields = QgsFields()
        fields.append(QgsField("level_dba", QVariant.Double))
        pr.addAttributes(fields)
        layer.updateFields()
        layer.updateExtents()

        QgsProject.instance().addMapLayer(layer)
