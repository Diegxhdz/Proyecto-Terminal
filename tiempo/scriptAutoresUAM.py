import pandas as pd
import re
from pathlib import Path
from collections import defaultdict


def procesar_autores(excel_path):
    """
    Lee un archivo Excel y retorna un set con todos los autores únicos.
    """
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return set()

    conjunto_autores = set(df['Name'].unique())
    print(f"Cargando archivo de entrada: {excel_path}")
    return conjunto_autores


def diccionario_autores(excel_path):
    """
    Lee un archivo Excel y retorna un diccionario con los autores y su ID de Scopus.
    """
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return {}

    diccionario_autores = dict(zip(df['Name'], df['Scopus author ID']))
    print(f"Cargando archivo de entrada: {excel_path}")
    return diccionario_autores


def buscar_autor(csv_path_publicaciones, conjunto_autores):
    try:
        df = pd.read_csv(csv_path_publicaciones)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return {}

    autores_publicaciones = defaultdict(list)

    print(f"\nBuscando autores de la UAM ({len(conjunto_autores)} autores) en {len(df)} publicaciones...")

    for autor_uam in conjunto_autores:
        for _, row in df.iterrows():
            if pd.isna(row.get('Authors')):
                continue

            autores_fila = str(row['Authors'])
            autores_list = [autor.strip() for autor in autores_fila.split('|') if autor.strip()]

            if autor_uam in autores_list:
                publicacion = dict(row.to_dict())
                publicacion.update({
                    'Año': row.get('Year', 'N/A'),
                    'Citas': row.get('Citations', 'N/A'),
                    'Colaboracion': row.get('Colaboracion', 'N/A'),
                    'Autores': row.get('Authors', 'N/A'),
                    'Instituciones': row.get('Institutions', 'N/A'),
                    'Regiones': row.get('Country/Region', 'N/A'),
                    'Instituciones_Nacionales': row.get('Number of national institutions', 0)
                })
                autores_publicaciones[autor_uam].append(publicacion)

    return autores_publicaciones




def obtener_id_autor(autor, diccionario_autores=None):
    if not diccionario_autores:
        return None
    autor_id = diccionario_autores.get(autor)
    if pd.isna(autor_id):
        return None
    return str(int(autor_id)) if isinstance(autor_id, (int, float)) and not pd.isna(autor_id) else str(autor_id).strip()

def exportar_publicaciones_por_autor(autores_publicaciones, diccionario_autores=None, output_folder='.'):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for autor, publicaciones in autores_publicaciones.items():
        autor_id = obtener_id_autor(autor, diccionario_autores)
        if autor_id:
            filename = f'articulos_{autor_id}.csv'
        output_path = output_folder / filename
        df_autor = pd.DataFrame(publicaciones)
        if 'Autor' not in df_autor.columns:
            df_autor.insert(0, 'Autor', autor)
        df_autor.to_csv(output_path, index=False, encoding='utf-8')

    return True



if __name__ == '__main__':
    excel_autores = Path('All_Authors_Universidad+Autónoma+Metropolitana_20260615.xlsx')
    csv_publicaciones = Path('Publications_at_Universidad_Aut_noma_Metropolitana_2015_-_2024.csv')
    output_dir_publicaciones = Path(r'C:\Users\diex2\Documents\ProyectoTerminal\tiempo\pubs_autor')

    autores_uam = procesar_autores(excel_autores)
    dic_autores = diccionario_autores(excel_autores)
    autores_publicaciones = buscar_autor(csv_publicaciones, autores_uam)

    print(f'Exportando {len(autores_publicaciones)} archivos de publicaciones a {output_dir_publicaciones}')
    exportar_publicaciones_por_autor(autores_publicaciones, dic_autores, output_dir_publicaciones)
    print('Exportación de publicaciones completa.')
  


