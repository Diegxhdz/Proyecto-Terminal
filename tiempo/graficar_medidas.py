import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def graficar_medida_anual_por_autor(df, medida, titulo, guardar=False, nombre_archivo=None):

    # Validar que la columna exista
    if medida not in df.columns:
        print(f"Error: La columna '{medida}' no existe en el DataFrame.")
        print(f"Columnas disponibles: {list(df.columns)}")
        return df

    # Convertir Año a string para mejor manejo
    df['Año'] = df['Año'].astype(str)
    
    # Obtener el nombre del autor desde el DataFrame
    autor_nombre = df['Autor'].iloc[0] if 'Autor' in df.columns else "Autor"

    # Crear la gráfica
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Año'], df[medida], marker='o', linewidth=2, markersize=8, color='#2E86AB')

    ax.set_xlabel('Año', fontsize=12)
    ax.set_ylabel(medida, fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    plt.tight_layout()

    if guardar and nombre_archivo:
        imagen_path = Path(f'{nombre_archivo}.png')
        csv_path = Path(f'{nombre_archivo}_filtrado.csv')
        fig.savefig(imagen_path, dpi=300)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f'Gráfica guardada en: {imagen_path}')
        print(f'Datos guardados en: {csv_path}')

    plt.show()
    return df



# Pedir la ruta del CSV
print("\nIngrese la ruta del archivo CSV del autor: ")
ruta_csv = input().strip()

# Validar que el archivo existe
ruta_path = Path(ruta_csv)
if not ruta_path.exists():
    print(f"Error: El archivo '{ruta_csv}' no existe.")
    exit()

# Cargar el CSV
try:
    df = pd.read_csv(ruta_csv)
except Exception as e:
    print(f"Error al leer el archivo: {e}")
    exit()

# Mostrar columnas disponibles
print("\nColumnas disponibles en el archivo:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

# Pedir la medida a graficar
print("\nIngrese el nombre de la medida a graficar: ")
medida = input().strip()

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
graficar_medida_anual_por_autor(df, medida, titulo, guardar, nombre_archivo)


