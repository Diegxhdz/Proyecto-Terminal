import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re as _re

from Configuracion import (
    RUTA_PRODUCTIVIDAD,
    LISTA_AUTORES,
    LISTA_MEDIDAS,
    GUARDAR,
    NOMBRE_ARCHIVO,
    TITULO,
)


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
        
    
        #extraer id del archivo 'productividad_au<id>.csv'
        stem = ruta_path.stem 
        # encontrar digitos después de 'au' en el nombre del archivo
        m = _re.search(r'au(\d+)', stem)

        id_autor = m.group(1)

        df_temp['Autor'] = id_autor

        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)
    return df

def graficar_medida_anual_por_autor(df, medida, titulo, guardar=False, nombre_archivo=None):

    # Convertir Año a string para mejor manejo
    df['Year'] = df['Year'].astype(str)

    autores = df['Autor'].unique().tolist()
    if isinstance(autores, str):
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
    df_pivot = df_filtrado.pivot_table(index='Year', columns='Autor', values=medida, aggfunc='sum')
    df_pivot = df_pivot.sort_index()

    # Crear la gráfica
    fig, ax = plt.subplots(figsize=(12, 6))
    for autor in df_pivot.columns:
        ax.plot(df_pivot.index, df_pivot[autor], marker='o', linewidth=2, markersize=8, label=autor)

    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel(medida, fontsize=12)
    ax.set_title(titulo, fontsize=14, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(title='Scopus Author ID')
    plt.xticks(rotation=45)
    plt.tight_layout()

    if guardar and nombre_archivo:
        imagen_dir = Path('graficas')
        csv_dir = Path('csv_graficas')
        imagen_dir.mkdir(parents=True, exist_ok=True)
        csv_dir.mkdir(parents=True, exist_ok=True)

        imagen_path = imagen_dir / f'{nombre_archivo}.png'
        csv_path = csv_dir / f'{nombre_archivo}_filtrado.csv'
        fig.savefig(imagen_path, dpi=300)
        df_filtrado.to_csv(csv_path, index=False, encoding='utf-8')
        print(f'Gráfica guardada en: {imagen_path}')
        print(f'Datos guardados en: {csv_path}')

    plt.show()
    return df_filtrado

if __name__ == "__main__":
    medida = LISTA_MEDIDAS[0] if LISTA_MEDIDAS else None
    titulo = TITULO
    nombre_archivo = NOMBRE_ARCHIVO
    guardar = GUARDAR

    df = cargar_csv_autores([f"{RUTA_PRODUCTIVIDAD}/productividad_au{autor}.csv" for autor in LISTA_AUTORES])
    graficar_medida_anual_por_autor(df, medida, titulo, guardar, nombre_archivo)


