import pandas as pd
from pathlib import Path

"""
Adjunto encontras los archivos de publicaciones de miembros de la UAM para el periodo 2015 - 2024, en donde cada renglón corresponde a una publicación. Como te había comentado la primer tarea consiste en clasificar cada publicación alguna de las siguientes categorias de colaboración:
Internacional - Hay coautores de instituiciones extranjeras.
Nacional - Hay coautores de instituciones nacionales diferentes a la UAM.
UAM - Todo los coautores son de la UAM (pueden ser de diferentes Unidades).
Personal - Artículos de un sólo autor

La primer tarea será realizar un script en python que realice la clasificación de la siguente manera:

- Lee el csv y los guarda en un DF.
- Las columnas útiles para la clasificación son: "Number of authors", "Country / Regions" (los valores están separados por '|'), "Number of countries / Regions", "Institutions" (los valores están separados por '|')
- Agrega al DF una columna colaboracion y ahí se le asigna a cada reglón uno los 3 tipos de colaboración.
- Agrega al DF una columna Number of national institutions. Debes contar cuantas instituciones nacionales diferentes hay en la columna institutons.
"""

def solo_uam(instituciones):
    instituciones_list = [inst.strip() for inst in instituciones.split('|')]
    for inst in instituciones_list:
        if 'Universidad Autónoma Metropolitana' not in inst:
            return False
    return True


def contar_instituciones_nacionales(instituciones):
  
    df = pd.read_csv("Institutions.csv")

    instituciones_list = [inst.strip() for inst in instituciones.split('|')]
    instituciones_nacionales = set()

    for inst in instituciones_list:
        if inst in df['Institution'].values:
            instituciones_nacionales.add(inst)

    return len(instituciones_nacionales)



def clasificar_nacionalidades(info_publicacion):

    if info_publicacion['Number of Authors'] == 1:
        return "Personal", 1
    
    elif info_publicacion['Number of Countries/Regions'] == 1 and 'Mexico' in info_publicacion['Country / Regions']:
        if solo_uam(info_publicacion['Institutions']):
            return "UAM", 1
        return "Nacional", contar_instituciones_nacionales(info_publicacion['Institutions'])

    elif info_publicacion['Number of Countries/Regions'] > 1:
        return "Internacional", contar_instituciones_nacionales(info_publicacion['Institutions'])

    return 



def procesar_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return 
    
    
    print(f"Cargando archivo de entrada: {csv_path}")

    try:
        for idx, row in df.iterrows():
            clasificar_publicacion = clasificar_nacionalidades(row)
            df.at[idx, 'Colaboracion'] = clasificar_publicacion[0]
            df.at[idx, 'Number of national institutions'] = clasificar_publicacion[1]

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
        return
    
    print("Archivo procesado exitosamente.")
    return df

if __name__ == "__main__":
    csv_path = Path("instituciones.csv")
    df_resultado = procesar_csv(csv_path)
    if df_resultado is not None:
        df_resultado.to_csv("publicaciones_clasificadas.csv", index=False)
        print("Archivo de salida guardado como 'publicaciones_clasificadas.csv'")