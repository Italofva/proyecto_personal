from numpy import std
import pandas as pd
import statistics as sta
#Mejoras pendientes:
#Exportar archivo con respecto a un mes determinado (filtro por fechas)

#Descarga de la base maestra de SKU
'''input_path=input("Ingrese la ruta del archivo:")
input_sheet=input("Ingrese el nombre de la hoja de calculo:")'''

path=r'C:\Automatizaciones\Precios\Data_limpia_prueba.xlsx'
df=pd.read_excel(path)
df["FECHA_REGISTRO"]=pd.to_datetime(df["FECHA_REGISTRO"],format='%d/%m/%Y')
skus=df["NOMBRE_ELEMENTO"].unique()
sku=[]
moda=[]
media=[]
dest=[]
for nombre_sku in skus:
    df_sku=df[(df["NOMBRE_ELEMENTO"]==nombre_sku)]["Precio Normal"]
    df_sku=df_sku.fillna(0)
    sku.append(nombre_sku)
    moda.append(sta.mode(df_sku))
    media.append(sta.mean(df_sku))
    dest.append(sta.pstdev(df_sku))
    

datos={'SKU':sku, 'Moda':moda, 'Media':media, 'Des.Est':dest}
df1=pd.DataFrame(datos)
df1.to_excel("MTC_actual.xlsx", index=False)
df1=df1.sort_values(by="Des.Est", ascending=False)
print(df1.head(12))
print("Archivo descargado")
