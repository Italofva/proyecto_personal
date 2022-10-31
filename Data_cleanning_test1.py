import pandas as pd
from datetime import datetime as dt
import statistics as sta
import numpy as np

pd.options.mode.chained_assignment = None

path=r'C:\Automatizaciones\Precios\Base_test.xlsx'
df=pd.read_excel(path, sheet_name="Base")

# Añadimos la columna Mes
df["Mes"]=pd.to_datetime(df["FECHA_REGISTRO"], format='%m').dt.month_name()

try:
    if (isinstance(df["Precio Normal"], object)) | (isinstance(df["Precio Promoción."],object)):
        df["Precio Normal"]=df['Precio Normal'].str.replace(",",".").astype(float)
        df["Precio Promoción."]=df["Precio Promoción."].str.replace(",",".").astype(float)
    else:
        pass
except Exception as e:
    pass

# Rellenar valores null a 0
df["Precio Normal"].fillna(0, inplace=True)
df["Precio Promoción."].fillna(0,inplace=True)

# Creacion de codigo unico para eliminar valores duplicados.
df["concat"]=df.FECHA_REGISTRO.dt.day.map(str)+\
            df.FECHA_REGISTRO.dt.month.map(str)+\
            df.FECHA_REGISTRO.dt.year.map(str)+\
            df.USUARIO+df.PDV+df.NOMBRE_ELEMENTO

print("Cantidad de filas sin limpiar: ", df.shape[0])

df=df.drop_duplicates(subset=["concat"])
print("Cantidad de filas sin duplicado: ",df.shape[0])

# Eliminación de precio normal y precio promoción igual a 0:
df_not_null=df.loc[(df["Precio Normal"]!=0) | (df["Precio Promoción."]!=0)]
df_not_null.reset_index(inplace=True)

#Extracción de sku que no se venden en el PDV:
df_null=df.loc[(df["Precio Normal"]==0) & (df["Precio Promoción."]==0)]
df_null.reset_index(inplace=True)

print("Filas limpias: ",df_not_null.shape[0],"\nFilas que no venden ese SKU: ",df_null.shape[0])

# Reemplazamos valores vacios o 0 de los precios normales por los valores de precio promocion
for i in range(0,len(df_not_null.index)):
    if df_not_null["Precio Normal"][i]==0:
        val=df_not_null["Precio Promoción."][i]
        df_not_null["Precio Normal"][i]=val
    else:
        pass

#Opcional
df_not_null.to_excel("Base_test_clean.xlsx", index=False)
df_null.to_excel("Base_null_test.xlsx", index=False)

# Función que almacena las medidas de tendecia central de cada SKU
def MTC_file(file):
    #path=r'C:\Minorista\CP\precios\Base_test_clean.xlsx'
    df=pd.read_excel(file)
    df["Mes"]=pd.to_datetime(df["FECHA_REGISTRO"], format='%m').dt.month_name()
    
    start_list=[]
    df_result=pd.DataFrame(start_list)

    # Iteramos por Mes
    for i in df.Mes.unique():
        df1=df[df.Mes==i]
        sku_mes=df1["NOMBRE_ELEMENTO"].unique()
        sku=[]
        moda=[]
        media=[]
        dest=[]
        mounth=[]
        # Iteramos por SKU por mes
        for nombre_sku in sku_mes:
            mes=i
            df_sku=df1[df1["NOMBRE_ELEMENTO"]==nombre_sku]["Precio Normal"]
            df_sku=df_sku.fillna(0)
            sku.append(nombre_sku)
            moda.append(sta.mode(df_sku))
            media.append(sta.mean(df_sku))
            dest.append(sta.pstdev(df_sku))
            mounth.append(mes)
        # Apilamos dataframes por cada mes
        df_start=df_result
        data_last={'SKU':sku, 'Moda':moda, 'Media':media, 'Des.Est':dest, 'Mes':mounth}
        df_finish=pd.DataFrame(data_last)
        df_result=pd.concat([df_start,df_finish], axis=0)
    
    df_result.to_excel("MTC_Mensual_prueba.xlsx", index=False)
    return df_result

# Función que detecta los outliers y lo almacena un una lista
def detect_ouliers_zscore(data):
    outliers=[]
    thres=2.5
    mean=np.mean(data)
    std=np.std(data)
    if std!=0:
        for i in data:
            z_score=(i-mean)/std
            if (np.abs(z_score)>thres):
                outliers.append(i)
    else:
        pass
    return outliers

# Función que reemplaza valores atípicos (outlier) por su moda
def replace_outliers(data,mtc_file):
    skus=data.NOMBRE_ELEMENTO.unique()
    for nombre_sku in skus:
        df_sku=data[data["NOMBRE_ELEMENTO"]==nombre_sku]
        sample_outliers=detect_ouliers_zscore(df_sku["Precio Normal"])
        if len(sample_outliers)!=0:
            for i in sample_outliers:
                moda=mtc_file[mtc_file.SKU==nombre_sku]["Moda"].iloc[0]
                df_sku.loc[df_sku["Precio Normal"]==i,"Precio Normal"]=moda
        else:
            pass
        data[data["NOMBRE_ELEMENTO"]==nombre_sku]=df_sku

    data.to_excel("Data_limpia_prueba.xlsx", index=False)
    return data




path_clean_data=r'C:\Automatizaciones\Precios\Base_test_clean.xlsx'
for i in range(0,3):
    if i==0:
        mtc=MTC_file(path_clean_data)
        dts=replace_outliers(df_not_null,mtc)
        update_path=r'C:\Automatizaciones\Precios\Data_limpia_prueba.xlsx'
    else:
        mtc=MTC_file(update_path)
        dts=replace_outliers(dts,mtc)



skus=dts.NOMBRE_ELEMENTO.unique()
for nombre_sku in skus:
    df_sku=dts[dts["NOMBRE_ELEMENTO"]==nombre_sku]
    for i in df_sku["Precio Normal"]:
        moda=mtc[mtc.SKU==nombre_sku]["Moda"].iloc[0]
        if (i>moda+3.5) | (i<moda-3.5):
            df_sku.loc[df_sku["Precio Normal"]==i,"Precio Normal"]=moda
        else:
            pass
    dts[dts["NOMBRE_ELEMENTO"]==nombre_sku]=df_sku

dts.drop(["index"], axis=1)
dts.to_excel("Data_limpia_prueba.xlsx", index=False)
print("Archivo MTC descargado")
print("Archivo DTS_base descargado")