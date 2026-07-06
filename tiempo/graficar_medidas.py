import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def cargar_csv_autores(rutas):
    dfs = []
    for ruta in rutas:
        ruta_path = Path(ruta)
        if not ruta_path.exists():
            print(f"Error: El archivo '{ruta}' no existe.")
            return None
        try:
            df_temp = pd.read_csv(ruta_path)
        except Exception as e:
            print(f"Error al leer el archivo '{ruta}': {e}")
            return None

        if 'Autor' not in df_temp.columns:
            autor_nombre = ruta_path.stem
            df_temp['Autor'] = autor_nombre
        dfs.append(df_temp)

    if not dfs:
        return None

    df = pd.concat(dfs, ignore_index=True)
    return df

def graficar_medida_anual_por_autor(df, medida, titulo, autores=None, guardar=False, nombre_archivo=None):

    # Validar que la columna exista
    if medida not in df.columns:
        print(f"Error: La columna '{medida}' no existe en el DataFrame.")
        print(f"Columnas disponibles: {list(df.columns)}")
        return df

    # Convertir Año a string para mejor manejo
    df['Año'] = df['Año'].astype(str)

    if 'Autor' not in df.columns:
        print("Error: La columna 'Autor' no existe en el DataFrame.")
        return df

    # Preparar la lista de autores a graficar
    if autores is None:
        autores = df['Autor'].unique().tolist()
    elif isinstance(autores, str):
        autores = [autor.strip() for autor in autores.split(',') if autor.strip()]
    else:
        autores = [str(autor).strip() for autor in autores if str(autor).strip()]

    autores_disponibles = df['Autor'].unique().astype(str).tolist()
    autores_seleccionados = [autor for autor in autores if autor in autores_disponibles]

    if not autores_seleccionados:
        print(f"No se encontraron autores válidos en el DataFrame. Autores disponibles: {autores_disponibles}")
        return df

    df_filtrado = df[df['Autor'].astype(str).isin(autores_seleccionados)].copy()

    # Pivotar datos para graficar cada autor por separado
    df_pivot = df_filtrado.pivot_table(index='Año', columns='Autor', values=medida, aggfunc='sum')
    df_pivot = df_pivot.sort_index()

    # Crear la gráfica
    fig, ax = plt.subplots(figsize=(12, 6))
    for autor in df_pivot.columns:
        ax.plot(df_pivot.index, df_pivot[autor], marker='o', linewidth=2, markersize=8, label=autor)

    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel(medida, fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(title='Autor')
    plt.xticks(rotation=45)
    plt.tight_layout()

    if guardar and nombre_archivo:
        imagen_path = Path(f'{nombre_archivo}.png')
        csv_path = Path(f'{nombre_archivo}_filtrado.csv')
        fig.savefig(imagen_path, dpi=300)
        df_filtrado.to_csv(csv_path, index=False, encoding='utf-8')
        print(f'Gráfica guardada en: {imagen_path}')
        print(f'Datos guardados en: {csv_path}')

    plt.show()
    return df_filtrado



# Pedir la ruta del CSV o varias rutas separadas por coma
print("\nIngrese la ruta del archivo CSV, o varias rutas separadas por coma:")
rutas_input = input().strip()
rutas = [ruta.strip() for ruta in rutas_input.split(',') if ruta.strip()]

if not rutas:
    print("Error: Debe ingresar al menos una ruta de archivo CSV.")
    exit()

# Cargar los archivos CSV
if len(rutas) == 1:
    ruta_path = Path(rutas[0])
    if not ruta_path.exists():
        print(f"Error: El archivo '{rutas[0]}' no existe.")
        exit()
    try:
        df = pd.read_csv(ruta_path)
    except Exception as e:
        print(f"Error al leer el archivo '{rutas[0]}': {e}")
        exit()
    if 'Autor' not in df.columns:
        df['Autor'] = ruta_path.stem
else:
    df = cargar_csv_autores(rutas)
    if df is None:
        exit()

# Mostrar columnas disponibles
print("\nColumnas disponibles en el archivo:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Pedir la medida a graficar
print("\nIngrese el nombre de la medida a graficar: ")
medida = input().strip()

# Usar todos los autores directamente desde el DataFrame
autores = None

# Pedir el título de la gráfica
print("\nIngrese el título para la gráfica: ")
titulo = input().strip()

# Pedir si guardar los archivos
print("\n¿Desea guardar la gráfica y los datos? (s/n): ")
guardar = input().strip().lower() == 's'

nombre_archivo = None
if guardar:
    print("Ingrese el nombre base para los archivos (sin extensión): ")
    nombre_archivo = input().strip()

# Generar la gráfica
graficar_medida_anual_por_autor(df, medida, titulo, autores, guardar, nombre_archivo)


