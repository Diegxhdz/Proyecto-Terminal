import pandas as pd
from pathlib import Path


def procesar_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return 
    
    
    print(f"Cargando archivo de entrada: {csv_path}")

    try:
        for idx, row in df.iterrows():
            no_autores = row['Number of authors']

    except Exception as e:
        print(f"Error al procesar el archivo CSV: {e}")
        return