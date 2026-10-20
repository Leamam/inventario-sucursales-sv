import sys
import os
import random
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont



def generar_inventario_csv(nombre_archivo="datos.csv"):
    random.seed(42)  
    sucursales = ["San Salvador", "Santa Ana", "San Miguel", "La Libertad", "Sonsonate"]

    catalogo = [
        ("Laptop Corporativa 15\"", "Tecnología", 650.00),
        ("Monitor LED 24\"", "Tecnología", 145.50),
        ("Teclado Mecánico USB", "Tecnología", 45.00),
        ("Impresora Multifuncional", "Oficina", 180.00),
        ("Silla Ergonómica Ejecutiva", "Mobiliario", 120.00),
        ("Escritorio Metálico", "Mobiliario", 195.00),
        ("Resma Papel Bond Carta", "Papelería", 4.75),
        ("Caja Bolígrafos Negros", "Papelería", 3.50),
        ("Router Inalámbrico Doble Banda", "Redes", 55.00),
        ("Switch Gigabit 8 Puertos", "Redes", 38.00)
    ]

    datos = []
    contador_id = 1001

    for _ in range(100):
        sucursal = random.choice(sucursales)
        producto, categoria, precio_base = random.choice(catalogo)

        if sucursal == "San Salvador":
            stock = random.randint(25, 90)
        elif sucursal in ["San Miguel", "Santa Ana"]:
            stock = random.randint(15, 65)
        else:
            stock = random.randint(5, 40)

        datos.append({
            "ID_Registro": f"INV-{contador_id}",
            "Sucursal": sucursal,
            "Producto": producto,
            "Categoria": categoria,
            "Stock_Actual": stock,
            "Precio_Unitario": precio_base,
            "Valor_Total_USD": round(stock * precio_base, 2)
        })
        contador_id += 1

    df = pd.DataFrame(datos)
    df.to_csv(nombre_archivo, index=False, encoding="utf-8")
    print(f"[OK] Archivo '{nombre_archivo}' generado correctamente con {len(df)} registros.\n")
    return df



def inspeccionar_datos(df):
    print("=" * 70)
    print("INSPECCIÓN DEL INVENTARIO CON PANDAS")
    print("=" * 70)

    print("\n1. PRIMERAS 5 FILAS (df.head):")
    print(df.head())

    print("\n2. ÚLTIMAS 5 FILAS (df.tail):")
    print(df.tail())

    print("\n3. ESTRUCTURA Y TIPOS DE DATOS (df.info):")
    df.info()

    print("\n4. VERIFICACIÓN DE VALORES NULOS (df.isnull().sum):")
    print(df.isnull().sum())

    print("\n5. ESTADÍSTICAS BÁSICAS DE VARIABLES NUMÉRICAS (df.describe):")
    print(df.describe().round(2))

    print("\n6. ESTADÍSTICAS DE VARIABLES CATEGÓRICAS:")
    print(df.describe(include=["object", "string"]))

    print("\n7. RESUMEN AGRUPADO POR SUCURSAL:")
    resumen_suc = df.groupby("Sucursal").agg(
        Total_Registros=("ID_Registro", "count"),
        Unidades_Totales=("Stock_Actual", "sum"),
        Promedio_Stock=("Stock_Actual", "mean"),
        Valor_Inventario_USD=("Valor_Total_USD", "sum")
    ).round(2).sort_values(by="Valor_Inventario_USD", ascending=False)
    print(resumen_suc)

    print("\n8. RESUMEN AGRUPADO POR CATEGORÍA:")
    resumen_cat = df.groupby("Categoria").agg(
        Total_Registros=("ID_Registro", "count"),
        Unidades_Totales=("Stock_Actual", "sum"),
        Promedio_Stock=("Stock_Actual", "mean"),
        Valor_Inventario_USD=("Valor_Total_USD", "sum")
    ).round(2).sort_values(by="Valor_Inventario_USD", ascending=False)
    print(resumen_cat)
    print("=" * 70 + "\n")



class VentanaInventario(QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df_original = df
        self.setWindowTitle("Sistema de Consultoría e Inventario - Sucursales El Salvador")
        self.resize(1200, 780)
        self.setStyleSheet("background-color: #f4f6f9;")
        self.inicializar_ui()

    def inicializar_ui(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QVBoxLayout(widget_central)
        layout_principal.setContentsMargins(15, 15, 15, 15)
        layout_principal.setSpacing(12)

        panel_superior = QFrame()
        panel_superior.setStyleSheet("background-color: #1e293b; border-radius: 8px; padding: 8px;")
        layout_superior = QHBoxLayout(panel_superior)

        titulo = QLabel("Dashboard de Inventario Nacional (5 Sucursales)")
        titulo.setFont(QFont("Segoe UI", 15, QFont.Bold))
        titulo.setStyleSheet("color: #ffffff;")

        etiqueta_filtro = QLabel("Filtrar por Sucursal:")
        etiqueta_filtro.setFont(QFont("Segoe UI", 10, QFont.Bold))
        etiqueta_filtro.setStyleSheet("color: #cbd5e1;")

        self.combo_sucursal = QComboBox()
        self.combo_sucursal.setFont(QFont("Segoe UI", 10))
        self.combo_sucursal.setStyleSheet(
            "background-color: #ffffff; color: #1e293b; padding: 5px 10px; border-radius: 4px;"
        )
        self.combo_sucursal.addItem("Todas las sucursales")
        self.combo_sucursal.addItems(sorted(self.df_original["Sucursal"].unique()))
        self.combo_sucursal.currentTextChanged.connect(self.actualizar_vista)

        layout_superior.addWidget(titulo)
        layout_superior.addStretch()
        layout_superior.addWidget(etiqueta_filtro)
        layout_superior.addWidget(self.combo_sucursal)
        layout_principal.addWidget(panel_superior)

        layout_kpis = QHBoxLayout()
        self.lbl_kpi_registros = self.crear_tarjeta_kpi("Lotes Registrados", "0")
        self.lbl_kpi_unidades = self.crear_tarjeta_kpi("Unidades en Stock", "0")
        self.lbl_kpi_valor = self.crear_tarjeta_kpi("Valor Total del Inventario", "$0.00")

        layout_kpis.addWidget(self.lbl_kpi_registros["frame"])
        layout_kpis.addWidget(self.lbl_kpi_unidades["frame"])
        layout_kpis.addWidget(self.lbl_kpi_valor["frame"])
        layout_principal.addLayout(layout_kpis)

        panel_graficos = QFrame()
        panel_graficos.setStyleSheet("background-color: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0;")
        layout_graficos = QVBoxLayout(panel_graficos)

        self.figura, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
        self.figura.patch.set_facecolor("#ffffff")
        self.canvas = FigureCanvas(self.figura)
        layout_graficos.addWidget(self.canvas)
        layout_principal.addWidget(panel_graficos, stretch=3)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(len(self.df_original.columns))
        self.tabla.setHorizontalHeaderLabels(self.df_original.columns)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet(
            "background-color: #ffffff; alternate-background-color: #f8fafc; "
            "gridline-color: #e2e8f0; font-size: 12px;"
        )
        layout_principal.addWidget(self.tabla, stretch=2)

        self.actualizar_vista()

    def crear_tarjeta_kpi(self, titulo_texto, valor_inicial):
        frame = QFrame()
        frame.setStyleSheet(
            "background-color: #ffffff; border-radius: 8px; border: 1px solid #cbd5e1; padding: 6px;"
        )
        layout = QVBoxLayout(frame)
        lbl_titulo = QLabel(titulo_texto)
        lbl_titulo.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_titulo.setStyleSheet("color: #64748b; border: none;")
        lbl_titulo.setAlignment(Qt.AlignCenter)

        lbl_valor = QLabel(valor_inicial)
        lbl_valor.setFont(QFont("Segoe UI", 14, QFont.Bold))
        lbl_valor.setStyleSheet("color: #0f172a; border: none;")
        lbl_valor.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        return {"frame": frame, "valor": lbl_valor}

    def actualizar_vista(self):
        seleccion = self.combo_sucursal.currentText()
        if seleccion == "Todas las sucursales":
            df_filtrado = self.df_original
        else:
            df_filtrado = self.df_original[self.df_original["Sucursal"] == seleccion]

        total_registros = len(df_filtrado)
        total_unidades = df_filtrado["Stock_Actual"].sum()
        valor_total = df_filtrado["Valor_Total_USD"].sum()

        self.lbl_kpi_registros["valor"].setText(f"{total_registros} registros")
        self.lbl_kpi_unidades["valor"].setText(f"{total_unidades:,} unidades")
        self.lbl_kpi_valor["valor"].setText(f"${valor_total:,.2f} USD")

        self.ax1.clear()
        self.ax2.clear()

        colores = ["#2563eb", "#0ea5e9", "#10b981", "#f59e0b", "#8b5cf6"]

        if seleccion == "Todas las sucursales":
            datos_g1 = df_filtrado.groupby("Sucursal")["Stock_Actual"].sum().sort_values(ascending=False)
            barras = self.ax1.bar(datos_g1.index, datos_g1.values, color=colores)
            self.ax1.set_title("Unidades Totales en Stock por Sucursal", fontsize=11, fontweight="bold")
            self.ax1.set_ylabel("Cantidad de Unidades")
            self.ax1.grid(axis="y", linestyle="--", alpha=0.4)
            for barra in barras:
                altura = barra.get_height()
                self.ax1.text(
                    barra.get_x() + barra.get_width() / 2, altura + 15,
                    f"{int(altura)}", ha="center", va="bottom", fontsize=9, fontweight="bold"
                )
        else:
            datos_g1 = df_filtrado.groupby("Categoria")["Stock_Actual"].sum().sort_values(ascending=False)
            barras = self.ax1.bar(datos_g1.index, datos_g1.values, color=colores[:len(datos_g1)])
            self.ax1.set_title(f"Unidades por Categoría ({seleccion})", fontsize=11, fontweight="bold")
            self.ax1.set_ylabel("Cantidad de Unidades")
            self.ax1.grid(axis="y", linestyle="--", alpha=0.4)
            for barra in barras:
                altura = barra.get_height()
                self.ax1.text(
                    barra.get_x() + barra.get_width() / 2, altura + 1,
                    f"{int(altura)}", ha="center", va="bottom", fontsize=9, fontweight="bold"
                )

        datos_g2 = df_filtrado.groupby("Categoria")["Valor_Total_USD"].sum().sort_values(ascending=True)
        barras_h = self.ax2.barh(datos_g2.index, datos_g2.values, color="#0f766e")
        self.ax2.set_title("Valor del Inventario por Categoría (USD)", fontsize=11, fontweight="bold")
        self.ax2.set_xlabel("Valor Monetario (USD)")
        self.ax2.grid(axis="x", linestyle="--", alpha=0.4)
        for barra in barras_h:
            ancho = barra.get_width()
            self.ax2.text(
                ancho, barra.get_y() + barra.get_height() / 2,
                f" ${ancho:,.0f}", ha="left", va="center", fontsize=8, fontweight="bold"
            )
        self.ax2.set_xlim(0, datos_g2.max() * 1.22 if len(datos_g2) > 0 else 100)

        self.figura.tight_layout()
        self.canvas.draw()

        self.tabla.setRowCount(len(df_filtrado))
        for fila_idx, (_, fila) in enumerate(df_filtrado.iterrows()):
            for col_idx, valor in enumerate(fila):
                texto = f"${valor:,.2f}" if col_idx in [5, 6] else str(valor)
                item = QTableWidgetItem(texto)
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(fila_idx, col_idx, item)


if __name__ == "__main__":
    archivo_csv = "datos.csv"
    if not os.path.exists(archivo_csv):
        df_inventario = generar_inventario_csv(archivo_csv)
    else:
        df_inventario = pd.read_csv(archivo_csv)

    inspeccionar_datos(df_inventario)

    app = QApplication(sys.argv)
    ventana = VentanaInventario(df_inventario)
    ventana.show()
    sys.exit(app.exec_())