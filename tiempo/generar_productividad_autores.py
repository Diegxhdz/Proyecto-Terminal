from pathlib import Path
from collections import defaultdict
import pandas as pd


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


def calcular_productividad_anual_por_autor(autores_publicaciones):
    registros = []

    for autor, publicaciones in autores_publicaciones.items():
        publicaciones_por_ano = defaultdict(list)
        for publicacion in publicaciones:
            ano = publicacion.get('Año', 'N/A')
            publicaciones_por_ano[ano].append(publicacion)

        for ano, pubs in sorted(publicaciones_por_ano.items(), key=lambda x: str(x[0])):
            total_pub = len(pubs)
            total_autores = 0
            autores_distintos = set()
            total_instituciones = 0
            total_instituciones_nacionales = 0
            total_instituciones_internacionales = 0
            regiones_unicas = set()
            publicaciones_solo_uam = 0
            publicaciones_nacional = 0
            publicaciones_internacional = 0
            publicaciones_individual = 0

            for pub in pubs:
                autores_list = [autor.strip() for autor in str(pub.get('Autores', '')).split('|') if autor.strip()]
                num_autores_pub = len(autores_list)
                total_autores += num_autores_pub
                autores_distintos.update(autores_list)

                colaboracion = str(pub.get('Colaboracion', '')).strip()
                if colaboracion == 'UAM':
                    publicaciones_solo_uam += 1
                elif colaboracion == 'Nacional':
                    publicaciones_nacional += 1
                elif colaboracion == 'Internacional':
                    publicaciones_internacional += 1
                elif colaboracion == 'Personal':
                    publicaciones_individual += 1

                instituciones_list = [inst.strip() for inst in str(pub.get('Instituciones', '')).split('|') if inst.strip()]
                num_instituciones = len(set(instituciones_list))
                total_instituciones += num_instituciones

                num_nacionales = pub.get('Instituciones_Nacionales', 0)
                try:
                    num_nacionales = int(num_nacionales)
                except Exception:
                    num_nacionales = 0
                total_instituciones_nacionales += num_nacionales

                total_instituciones_internacionales += max(0, num_instituciones - num_nacionales)

                regiones_list = [r.strip() for r in str(pub.get('Regiones', '')).split('|') if r.strip()]
                regiones_unicas.update(regiones_list)

            promedio_autores = total_autores / total_pub if total_pub else 0

            registro = {
                'Autor': autor,
                'Año': ano,
                'Número de publicaciones en el año': total_pub,
                'Número de publicaciones individual': publicaciones_individual,
                'Número de autores promedio por artículo': round(promedio_autores, 2),
                'Número de autores diferentes': len(autores_distintos),
                'Número de instituciones nacionales (No UAM)': total_instituciones_nacionales,
                'Número de instituciones internacionales': total_instituciones_internacionales,
                'Número de regiones': len(regiones_unicas),
                'Número de publicaciones Sólo UAM en el año': publicaciones_solo_uam,
                'Número de publicaciones Nacional en el año': publicaciones_nacional,
                'Número de publicaciones Internacional en el año': publicaciones_internacional
            }
            registros.append(registro)

    return pd.DataFrame(registros)


def obtener_id_autor(autor, diccionario_autores=None):
    if not diccionario_autores:
        return None
    autor_id = diccionario_autores.get(autor)
    if pd.isna(autor_id):
        return None
    return str(int(autor_id)) if isinstance(autor_id, (int, float)) and not pd.isna(autor_id) else str(autor_id).strip()


def exportar_productividad_por_autor_individual(autores_publicaciones, diccionario_autores=None, output_folder='.'):
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    for autor, publicaciones in autores_publicaciones.items():
        autor_id = obtener_id_autor(autor, diccionario_autores)
        if autor_id:
            filename = f'productividad_au{autor_id}.csv'
        output_path = output_folder / filename
        df_autor = calcular_productividad_anual_por_autor({autor: publicaciones})
        df_autor = df_autor.sort_values(['Autor', 'Año'])
        df_autor.to_csv(output_path, index=False, encoding='utf-8')

    return True



def generar_productividad_desde_archivos(input_folder, output_folder, excel_path):
    input_folder = Path(input_folder)
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    autores_publicaciones = defaultdict(list)
    archivos = sorted(input_folder.glob('articulos_*.csv'))

    if not archivos:
        print(f'No se encontraron archivos en {input_folder}')
        return False

    for archivo in archivos:
        df_publicaciones = pd.read_csv(archivo)
        if df_publicaciones.empty:
            continue

        autor = None
        if 'Autor' in df_publicaciones.columns and not df_publicaciones['Autor'].dropna().empty:
            autor = str(df_publicaciones['Autor'].dropna().iloc[0])
        else:
            autor = archivo.stem.replace('articulos_', '').strip()

        for _, row in df_publicaciones.iterrows():
            publicacion = dict(row.to_dict())
            publicacion.update({
                'Año': row.get('Año', row.get('Year', 'N/A')),
                'Citas': row.get('Citas', row.get('Citations', 'N/A')),
                'Colaboracion': row.get('Colaboracion', row.get('Colaboration', 'N/A')),
                'Autores': row.get('Autores', row.get('Authors', 'N/A')),
                'Instituciones': row.get('Instituciones', row.get('Institutions', 'N/A')),
                'Regiones': row.get('Regiones', row.get('Country/Region', 'N/A')),
                'Instituciones_Nacionales': row.get('Instituciones_Nacionales', row.get('Number of national institutions', 0))
            })
            autores_publicaciones[autor].append(publicacion)

    dic_autores = diccionario_autores(excel_path)
    exportar_productividad_por_autor_individual(autores_publicaciones, dic_autores, output_folder)
    print(f'Productividad exportada para {len(autores_publicaciones)} autores en {output_folder}')
    return True


if __name__ == '__main__':
    base_dir = Path(r'C:\Users\diex2\Documents\ProyectoTerminal\tiempo')
    input_dir = base_dir / 'pubs_autor'
    output_dir = base_dir / 'autores'
    excel_autores = base_dir / 'All_Authors_Universidad+Autónoma+Metropolitana_20260615.xlsx'

    generar_productividad_desde_archivos(input_dir, output_dir, excel_autores)
