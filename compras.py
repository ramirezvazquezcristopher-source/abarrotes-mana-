import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


# ==========================================================
# BASE DE DATOS
# ==========================================================

conexion = sqlite3.connect("inventario.db")
cursor = conexion.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL
    )
""")

conexion.commit()


# ==========================================================
# PALETA DE COLORES
# ==========================================================

# Fondo general: gris cálido muy suave
COLOR_FONDO = "#E9ECEB"

# Paneles y tarjetas
COLOR_PANEL = "#F7F8F6"

# Color principal: verde petróleo
COLOR_PRIMARIO = "#355C5A"
COLOR_PRIMARIO_HOVER = "#2C4D4B"

# Acciones
COLOR_VERDE = "#648C78"
COLOR_VERDE_HOVER = "#557665"

COLOR_ROJO = "#A86F6F"
COLOR_ROJO_HOVER = "#915D5D"

# Textos
COLOR_TEXTO = "#263332"
COLOR_TEXTO_SECUNDARIO = "#687574"

# Blanco cálido
COLOR_BLANCO = "#F7F8F6"

# Selección de tabla
COLOR_SELECCION = "#D7E4E0"

# Bordes suaves
COLOR_BORDE = "#D5DCDA"


# ==========================================================
# VENTANA
# ==========================================================

ventana = tk.Tk()

ventana.title("Sistema de Inventario")
ventana.geometry("1000x650")

ventana.configure(
    bg=COLOR_FONDO
)

ventana.minsize(
    850,
    550
)


# ==========================================================
# FUNCIONES
# ==========================================================

def actualizar_contadores():

    cursor.execute(
        "SELECT COUNT(*) FROM productos"
    )

    cantidad_productos = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COALESCE(SUM(cantidad), 0) FROM productos"
    )

    cantidad_unidades = cursor.fetchone()[0]

    etiqueta_productos.config(
        text=f"Productos: {cantidad_productos}"
    )

    etiqueta_stock.config(
        text=f"Unidades: {cantidad_unidades}"
    )


def cargar_productos():

    for producto in tabla.get_children():
        tabla.delete(producto)

    cursor.execute("""
        SELECT codigo, nombre, cantidad, precio
        FROM productos
        ORDER BY id DESC
    """)

    productos = cursor.fetchall()

    for producto in productos:

        codigo, nombre, cantidad, precio = producto

        tabla.insert(
            "",
            tk.END,
            values=(
                codigo,
                nombre,
                cantidad,
                f"${precio:.2f}"
            )
        )

    actualizar_contadores()


def limpiar_campos():

    entrada_codigo.delete(
        0,
        tk.END
    )

    entrada_nombre.delete(
        0,
        tk.END
    )

    entrada_cantidad.delete(
        0,
        tk.END
    )

    entrada_precio.delete(
        0,
        tk.END
    )

    tabla.selection_remove(
        tabla.selection()
    )


def agregar_producto():

    codigo = entrada_codigo.get().strip()
    nombre = entrada_nombre.get().strip()
    cantidad = entrada_cantidad.get().strip()
    precio = entrada_precio.get().strip()

    if not codigo or not nombre or not cantidad or not precio:

        messagebox.showwarning(
            "Campos incompletos",
            "Completa todos los campos."
        )

        return

    try:

        cantidad = int(cantidad)
        precio = float(precio)

    except ValueError:

        messagebox.showerror(
            "Error",
            "Cantidad debe ser un número entero y precio un número."
        )

        return

    if cantidad < 0 or precio < 0:

        messagebox.showerror(
            "Error",
            "No se permiten valores negativos."
        )

        return

    try:

        cursor.execute("""
            INSERT INTO productos
            (codigo, nombre, cantidad, precio)
            VALUES (?, ?, ?, ?)
        """, (
            codigo,
            nombre,
            cantidad,
            precio
        ))

        conexion.commit()

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Código repetido",
            "Ya existe un producto con ese código."
        )

        return

    cargar_productos()
    limpiar_campos()

    messagebox.showinfo(
        "Producto agregado",
        "El producto se guardó correctamente."
    )


def eliminar_producto():

    seleccionado = tabla.selection()

    if not seleccionado:

        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona un producto para eliminar."
        )

        return

    datos = tabla.item(
        seleccionado[0]
    )["values"]

    codigo = datos[0]

    confirmar = messagebox.askyesno(
        "Confirmar eliminación",
        f"¿Eliminar '{datos[1]}'?"
    )

    if not confirmar:
        return

    cursor.execute(
        "DELETE FROM productos WHERE codigo = ?",
        (codigo,)
    )

    conexion.commit()

    cargar_productos()
    limpiar_campos()


def modificar_producto():

    seleccionado = tabla.selection()

    if not seleccionado:

        messagebox.showwarning(
            "Selecciona un producto",
            "Selecciona un producto para modificar."
        )

        return

    codigo = entrada_codigo.get().strip()
    nombre = entrada_nombre.get().strip()
    cantidad = entrada_cantidad.get().strip()
    precio = entrada_precio.get().strip()

    if not codigo or not nombre or not cantidad or not precio:

        messagebox.showwarning(
            "Campos incompletos",
            "Completa todos los campos."
        )

        return

    try:

        cantidad = int(cantidad)
        precio = float(precio)

    except ValueError:

        messagebox.showerror(
            "Error",
            "Cantidad o precio inválido."
        )

        return

    datos = tabla.item(
        seleccionado[0]
    )["values"]

    codigo_original = datos[0]

    try:

        cursor.execute("""
            UPDATE productos
            SET codigo = ?,
                nombre = ?,
                cantidad = ?,
                precio = ?
            WHERE codigo = ?
        """, (
            codigo,
            nombre,
            cantidad,
            precio,
            codigo_original
        ))

        conexion.commit()

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Error",
            "Ese código ya pertenece a otro producto."
        )

        return

    cargar_productos()
    limpiar_campos()


def seleccionar_producto(event):

    seleccionado = tabla.selection()

    if not seleccionado:
        return

    datos = tabla.item(
        seleccionado[0]
    )["values"]

    entrada_codigo.delete(
        0,
        tk.END
    )

    entrada_codigo.insert(
        0,
        datos[0]
    )

    entrada_nombre.delete(
        0,
        tk.END
    )

    entrada_nombre.insert(
        0,
        datos[1]
    )

    entrada_cantidad.delete(
        0,
        tk.END
    )

    entrada_cantidad.insert(
        0,
        datos[2]
    )

    entrada_precio.delete(
        0,
        tk.END
    )

    entrada_precio.insert(
        0,
        str(datos[3]).replace("$", "")
    )


def buscar_producto():

    texto = entrada_busqueda.get().strip()

    if not texto:

        cargar_productos()

        return

    for producto in tabla.get_children():
        tabla.delete(producto)

    cursor.execute("""
        SELECT codigo, nombre, cantidad, precio
        FROM productos
        WHERE codigo LIKE ?
           OR nombre LIKE ?
        ORDER BY nombre
    """, (
        f"%{texto}%",
        f"%{texto}%"
    ))

    productos = cursor.fetchall()

    for producto in productos:

        codigo, nombre, cantidad, precio = producto

        tabla.insert(
            "",
            tk.END,
            values=(
                codigo,
                nombre,
                cantidad,
                f"${precio:.2f}"
            )
        )


def mostrar_todos():

    entrada_busqueda.delete(
        0,
        tk.END
    )

    cargar_productos()


# ==========================================================
# HOVER DE BOTONES
# ==========================================================

def hover_azul(event):

    event.widget.config(
        bg=COLOR_PRIMARIO_HOVER
    )


def salir_azul(event):

    event.widget.config(
        bg=COLOR_PRIMARIO
    )


def hover_verde(event):

    event.widget.config(
        bg=COLOR_VERDE_HOVER
    )


def salir_verde(event):

    event.widget.config(
        bg=COLOR_VERDE
    )


def hover_rojo(event):

    event.widget.config(
        bg=COLOR_ROJO_HOVER
    )


def salir_rojo(event):

    event.widget.config(
        bg=COLOR_ROJO
    )


# ==========================================================
# ENCABEZADO
# ==========================================================

encabezado = tk.Frame(
    ventana,
    bg=COLOR_PRIMARIO,
    height=90
)

encabezado.pack(
    fill="x"
)


titulo = tk.Label(
    encabezado,
    text="📦  ABAROTES MANA",
    font=("Arial", 24, "bold"),
    bg=COLOR_PRIMARIO,
    fg=COLOR_BLANCO
)

titulo.pack(
    side="left",
    padx=30,
    pady=20
)


subtitulo = tk.Label(
    encabezado,
    text="Inventario",
    font=("Arial", 11),
    bg=COLOR_PRIMARIO,
    fg="#DDE7E4"
)

subtitulo.pack(
    side="left"
)


# ==========================================================
# TARJETAS
# ==========================================================

marco_tarjetas = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

marco_tarjetas.pack(
    fill="x",
    padx=25,
    pady=20
)


# ------------------------------
# TARJETA PRODUCTOS
# ------------------------------

tarjeta_productos = tk.Frame(
    marco_tarjetas,
    bg=COLOR_PANEL,
    highlightbackground=COLOR_BORDE,
    highlightthickness=1
)

tarjeta_productos.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


etiqueta_productos = tk.Label(
    tarjeta_productos,
    text="Productos: 0",
    font=("Arial", 16, "bold"),
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO
)

etiqueta_productos.pack(
    pady=25
)


# ------------------------------
# TARJETA STOCK
# ------------------------------

tarjeta_stock = tk.Frame(
    marco_tarjetas,
    bg=COLOR_PANEL,
    highlightbackground=COLOR_BORDE,
    highlightthickness=1
)

tarjeta_stock.pack(
    side="left",
    fill="x",
    expand=True,
    padx=5
)


etiqueta_stock = tk.Label(
    tarjeta_stock,
    text="Unidades: 0",
    font=("Arial", 16, "bold"),
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO
)

etiqueta_stock.pack(
    pady=25
)


# ==========================================================
# FORMULARIO
# ==========================================================

marco_formulario = tk.Frame(
    ventana,
    bg=COLOR_PANEL,
    highlightbackground=COLOR_BORDE,
    highlightthickness=1
)

marco_formulario.pack(
    fill="x",
    padx=25
)


tk.Label(
    marco_formulario,
    text="Agregar / modificar producto",
    font=("Arial", 14, "bold"),
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO
).grid(
    row=0,
    column=0,
    columnspan=4,
    sticky="w",
    padx=20,
    pady=15
)


# ==========================================================
# CAMPOS
# ==========================================================

# Código

tk.Label(
    marco_formulario,
    text="Código",
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO_SECUNDARIO
).grid(
    row=1,
    column=0,
    padx=15,
    sticky="w"
)

entrada_codigo = tk.Entry(
    marco_formulario,
    width=20,
    font=("Arial", 11),
    bg="#FFFFFF",
    fg=COLOR_TEXTO,
    relief="solid",
    bd=1
)

entrada_codigo.grid(
    row=2,
    column=0,
    padx=15,
    pady=(3, 15)
)


# Producto

tk.Label(
    marco_formulario,
    text="Producto",
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO_SECUNDARIO
).grid(
    row=1,
    column=1,
    padx=15,
    sticky="w"
)

entrada_nombre = tk.Entry(
    marco_formulario,
    width=25,
    font=("Arial", 11),
    bg="#FFFFFF",
    fg=COLOR_TEXTO,
    relief="solid",
    bd=1
)

entrada_nombre.grid(
    row=2,
    column=1,
    padx=15,
    pady=(3, 15)
)


# Cantidad

tk.Label(
    marco_formulario,
    text="Cantidad",
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO_SECUNDARIO
).grid(
    row=1,
    column=2,
    padx=15,
    sticky="w"
)

entrada_cantidad = tk.Entry(
    marco_formulario,
    width=15,
    font=("Arial", 11),
    bg="#FFFFFF",
    fg=COLOR_TEXTO,
    relief="solid",
    bd=1
)

entrada_cantidad.grid(
    row=2,
    column=2,
    padx=15,
    pady=(3, 15)
)


# Precio

tk.Label(
    marco_formulario,
    text="Precio",
    bg=COLOR_PANEL,
    fg=COLOR_TEXTO_SECUNDARIO
).grid(
    row=1,
    column=3,
    padx=15,
    sticky="w"
)

entrada_precio = tk.Entry(
    marco_formulario,
    width=15,
    font=("Arial", 11),
    bg="#FFFFFF",
    fg=COLOR_TEXTO,
    relief="solid",
    bd=1
)

entrada_precio.grid(
    row=2,
    column=3,
    padx=15,
    pady=(3, 15)
)


# ==========================================================
# BOTONES
# ==========================================================

marco_botones = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

marco_botones.pack(
    fill="x",
    padx=25,
    pady=10
)


# AGREGAR

boton_agregar = tk.Button(
    marco_botones,
    text="＋ Agregar",
    font=("Arial", 10, "bold"),
    bg=COLOR_PRIMARIO,
    fg=COLOR_BLANCO,
    activebackground=COLOR_PRIMARIO_HOVER,
    activeforeground=COLOR_BLANCO,
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2",
    command=agregar_producto
)

boton_agregar.pack(
    side="left",
    padx=5
)

boton_agregar.bind(
    "<Enter>",
    hover_azul
)

boton_agregar.bind(
    "<Leave>",
    salir_azul
)


# MODIFICAR

boton_modificar = tk.Button(
    marco_botones,
    text="✎ Modificar",
    font=("Arial", 10, "bold"),
    bg=COLOR_VERDE,
    fg=COLOR_BLANCO,
    activebackground=COLOR_VERDE_HOVER,
    activeforeground=COLOR_BLANCO,
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2",
    command=modificar_producto
)

boton_modificar.pack(
    side="left",
    padx=5
)

boton_modificar.bind(
    "<Enter>",
    hover_verde
)

boton_modificar.bind(
    "<Leave>",
    salir_verde
)


# ELIMINAR

boton_eliminar = tk.Button(
    marco_botones,
    text="🗑 Eliminar",
    font=("Arial", 10, "bold"),
    bg=COLOR_ROJO,
    fg=COLOR_BLANCO,
    activebackground=COLOR_ROJO_HOVER,
    activeforeground=COLOR_BLANCO,
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2",
    command=eliminar_producto
)

boton_eliminar.pack(
    side="left",
    padx=5
)

boton_eliminar.bind(
    "<Enter>",
    hover_rojo
)

boton_eliminar.bind(
    "<Leave>",
    salir_rojo
)


# LIMPIAR

boton_limpiar = tk.Button(
    marco_botones,
    text="Limpiar",
    bg="#DDE2E0",
    fg=COLOR_TEXTO,
    activebackground="#CDD4D1",
    activeforeground=COLOR_TEXTO,
    relief="flat",
    padx=15,
    pady=8,
    cursor="hand2",
    command=limpiar_campos
)

boton_limpiar.pack(
    side="left",
    padx=5
)


# ==========================================================
# BUSCADOR
# ==========================================================

marco_busqueda = tk.Frame(
    ventana,
    bg=COLOR_FONDO
)

marco_busqueda.pack(
    fill="x",
    padx=25,
    pady=5
)


tk.Label(
    marco_busqueda,
    text="🔎 Buscar:",
    font=("Arial", 11, "bold"),
    bg=COLOR_FONDO,
    fg=COLOR_TEXTO
).pack(
    side="left"
)


entrada_busqueda = tk.Entry(
    marco_busqueda,
    width=35,
    font=("Arial", 11),
    bg="#FFFFFF",
    fg=COLOR_TEXTO,
    relief="solid",
    bd=1
)

entrada_busqueda.pack(
    side="left",
    padx=10
)


boton_buscar = tk.Button(
    marco_busqueda,
    text="Buscar",
    bg=COLOR_PRIMARIO,
    fg=COLOR_BLANCO,
    activebackground=COLOR_PRIMARIO_HOVER,
    activeforeground=COLOR_BLANCO,
    relief="flat",
    padx=15,
    cursor="hand2",
    command=buscar_producto
)

boton_buscar.pack(
    side="left"
)


boton_todos = tk.Button(
    marco_busqueda,
    text="Mostrar todos",
    bg="#DDE2E0",
    fg=COLOR_TEXTO,
    activebackground="#CDD4D1",
    activeforeground=COLOR_TEXTO,
    relief="flat",
    padx=15,
    cursor="hand2",
    command=mostrar_todos
)

boton_todos.pack(
    side="left",
    padx=5
)


# ==========================================================
# TABLA
# ==========================================================

marco_tabla = tk.Frame(
    ventana,
    bg=COLOR_PANEL,
    highlightbackground=COLOR_BORDE,
    highlightthickness=1
)

marco_tabla.pack(
    fill="both",
    expand=True,
    padx=25,
    pady=10
)


# ==========================================================
# ESTILO DE TABLA
# ==========================================================

estilo = ttk.Style()

estilo.theme_use("clam")


estilo.configure(
    "Treeview",
    background=COLOR_PANEL,
    foreground=COLOR_TEXTO,
    rowheight=35,
    fieldbackground=COLOR_PANEL,
    font=("Arial", 10),
    borderwidth=0
)


estilo.configure(
    "Treeview.Heading",
    background=COLOR_PRIMARIO,
    foreground=COLOR_BLANCO,
    font=("Arial", 10, "bold"),
    padding=8,
    relief="flat"
)


estilo.map(
    "Treeview",
    background=[
        ("selected", COLOR_SELECCION)
    ],
    foreground=[
        ("selected", COLOR_TEXTO)
    ]
)


# ==========================================================
# COLUMNAS
# ==========================================================

columnas = (
    "codigo",
    "nombre",
    "cantidad",
    "precio"
)


tabla = ttk.Treeview(
    marco_tabla,
    columns=columnas,
    show="headings"
)


tabla.heading(
    "codigo",
    text="Código"
)

tabla.heading(
    "nombre",
    text="Producto"
)

tabla.heading(
    "cantidad",
    text="Cantidad"
)

tabla.heading(
    "precio",
    text="Precio"
)


tabla.column(
    "codigo",
    width=120,
    anchor="center"
)

tabla.column(
    "nombre",
    width=350
)

tabla.column(
    "cantidad",
    width=120,
    anchor="center"
)

tabla.column(
    "precio",
    width=150,
    anchor="center"
)


tabla.pack(
    fill="both",
    expand=True
)


tabla.bind(
    "<<TreeviewSelect>>",
    seleccionar_producto
)


# ==========================================================
# CARGAR DATOS
# ==========================================================

cargar_productos()


# ==========================================================
# CERRAR BASE DE DATOS
# ==========================================================

def cerrar_programa():

    conexion.close()
    ventana.destroy()


ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar_programa
)


# ==========================================================
# EJECUTAR
# ==========================================================

ventana.mainloop()