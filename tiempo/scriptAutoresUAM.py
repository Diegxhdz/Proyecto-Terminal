import pandas as pd
import os
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
    
    # Set de autores únicos 
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
    
    # Diccionario de autores y su ID de Scopus
    diccionario_autores = dict(zip(df['Name'], df['Scopus author ID']))
    
    print(f"Cargando archivo de entrada: {excel_path}")
    
    return diccionario_autores


def buscar_autor(csv_path_publicaciones, conjunto_autores):

    try:
        df = pd.read_csv(csv_path_publicaciones)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return {}
    
    # Diccionario para almacenar autores y sus publicaciones
    # Estructura: { 'nombre_autor': [list de publicaciones] }
    autores_publicaciones = defaultdict(list)
    
    print(f"\nBuscando autores de la UAM ({len(conjunto_autores)} autores) en {len(df)} publicaciones...")
    
    # Para cada autor en la lista de autores de la UAM
    for autor_uam in conjunto_autores:
        # Iterar sobre todas las publicaciones
        for index, row in df.iterrows():
            # Validar que la celda no esté vacía
            if pd.isna(row.get('Authors')):
                continue 
                
            autores_fila = row['Authors']
            # Dividir los autores (separados por |)
            autores_list = [autor.strip() for autor in autores_fila.split('|')]

            # Si el autor de la UAM está en esta publicación
            if autor_uam in autores_list:
                # Crear registro de la publicación
                publicacion = {
                    'Título': row.get('Title', 'N/A'),
                    'Año': row.get('Year', 'N/A'),
                    'Citas': row.get('Cited by', 'N/A'),
                    'ID': row.get('EID', row.get('ID', 'N/A')),
                    'Fuente': row.get('Source title', 'N/A'),
                    'Tipo': row.get('Document Type', 'N/A'),
                    'Autores': autores_fila
                }
                autores_publicaciones[autor_uam].append(publicacion)

    return autores_con_publicaciones


def exportar_autores_a_csv(autores_publicaciones, output_path):

    registros = []
    
    for autor, publicaciones in autores_publicaciones.items():
        # Crear un registro por autor
        registro = {
            'Autor': autor,
            'Num_Publicaciones': len(publicaciones),
            'Años': '; '.join(str(p['Año']) for p in publicaciones if p['Año'] != 'N/A'),
            'Títulos': ' | '.join(p['Título'] for p in publicaciones),
            'Citas_Totales': sum(p['Citas'] if isinstance(p['Citas'], (int, float)) else 0 for p in publicaciones),
            'Fuentes': '; '.join(set(p['Fuente'] for p in publicaciones if p['Fuente'] != 'N/A')),
            'Tipos_Documento': '; '.join(set(p['Tipo'] for p in publicaciones if p['Tipo'] != 'N/A')),
            'IDs': '; '.join(p['ID'] for p in publicaciones if p['ID'] != 'N/A')
        }
        registros.append(registro)
    
    # Crear DataFrame y exportar
    df_resultado = pd.DataFrame(registros)
    # Ordenar por número de publicaciones (descendente)
    df_resultado = df_resultado.sort_values('Num_Publicaciones', ascending=False)
    
    df_resultado.to_csv(output_path, index=False, encoding='utf-8')
    
    return df_resultado

