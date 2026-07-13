import pandas as pd
import re
from pathlib import Path
from collections import defaultdict

#Función para facilitar la comparación de los IDs de autor, eliminando prefijos, sufijos y espacios
def _canonical_base(author_id):
    """Return a canonical base form for an author id: strip 'au' prefix, .0, spaces and lower."""
    if author_id is None or (isinstance(author_id, float) and pd.isna(author_id)):
        return None
    s = str(author_id).strip()
    if s.endswith('.0'):
        s = s[:-2]
    s = s.replace(' ', '')
    s = s.lower()
    if s.startswith('au'):
        s = s[2:]
    return s


def procesar_autores(excel_path):
    """
    Lee un archivo Excel y retorna un set con todos los autores únicos.
    """
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return set()

    # Normalizar author IDs
    conjunto_autores = set()
    for raw in df['Scopus author ID'].unique():
        base = _canonical_base(raw)
        if base:
            conjunto_autores.add(base)
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

    # Map canonical base id -> Name
    diccionario_autores = {}
    for raw_id, name in zip(df['Scopus author ID'], df['Name']):
        base = _canonical_base(raw_id)
        if base:
            diccionario_autores[base] = name
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

    for _, row in df.iterrows():
        print("progreso {}/{}".format(_, len(df)), end='\r')
        scopus_ids = row.get('Scopus Author Ids')
        if pd.isna(scopus_ids):
            continue

        autores_fila = str(scopus_ids)
        autores_list = re.split(r"\||;|,", autores_fila)
        row_bases = set()
        for autor in autores_list:
            a = autor.strip()
            if not a:
                continue
            base = _canonical_base(a)
            if base:
                row_bases.add(base)

        matched = row_bases & conjunto_autores
        if not matched:
            continue

        publicacion = dict(row.to_dict())
        for base in matched:
            autores_publicaciones[base].append(publicacion)

    return autores_publicaciones




def obtener_id_autor(autor, diccionario_autores=None):
    if autor is None or pd.isna(autor):
        return None
    base = _canonical_base(autor)
    return base


def obtener_nombre_autor(autor, diccionario_autores=None):
    if autor is None or pd.isna(autor):
        return None
    base = _canonical_base(autor)
    if diccionario_autores and base in diccionario_autores:
        return diccionario_autores[base]
    return autor


#Funciones anteriores fueron propuestas por la IA, para mejorar la búsqueda de autores y la exportación de publicaciones por autor en cuanto a velocidad.

def exportar_publicaciones_por_autor(autores_publicaciones, diccionario_autores=None, output_folder='.'):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for autor, publicaciones in autores_publicaciones.items():
        autor_id = obtener_id_autor(autor, diccionario_autores)
        autor_nombre = obtener_nombre_autor(autor, diccionario_autores)
        #nombre del archivo
        filename = f'articulos_{autor_id}.csv'
        output_path = output_folder / filename
        df_autor = pd.DataFrame(publicaciones)
        if 'Autor' not in df_autor.columns:
            df_autor.insert(0, 'Autor', autor_nombre)
        if 'Scopus author ID' not in df_autor.columns:
            autor_col_idx = df_autor.columns.get_loc('Autor') + 1
            df_autor.insert(autor_col_idx, 'Scopus author ID', autor_id)
        df_autor.to_csv(output_path, index=False, encoding='utf-8')

    return True



if __name__ == '__main__':
    excel_autores = Path('All_Authors_Universidad+Autónoma+Metropolitana_20260615.xlsx')
    csv_publicaciones = Path('publicaciones_clasificadas.csv')
    output_dir_publicaciones = Path(r'C:\Users\diex2\Documents\ProyectoTerminal\analisis_tiempo\pubs_autor')

    autores_uam = procesar_autores(excel_autores)
    dic_autores = diccionario_autores(excel_autores)
    autores_publicaciones = buscar_autor(csv_publicaciones, autores_uam)

    print(f'Exportando {len(autores_publicaciones)} archivos de publicaciones a {output_dir_publicaciones}')
    exportar_publicaciones_por_autor(autores_publicaciones, dic_autores, output_dir_publicaciones)
    print('Exportación de publicaciones completa.')
  