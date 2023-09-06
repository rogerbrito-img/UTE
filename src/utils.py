import json, os
import arcpy
import datetime
from zipfile import ZipFile
from config.variaveis import variaveis
from models.modelo_json import campos_esperados


def remove_shapefiles():
    arquivos = os.listdir(variaveis["pasta_shp_"])
    for arquivo in arquivos:
        os.remove(os.path.join(variaveis["pasta_shp_"], arquivo)) # Reforça a indicacao do caminho


def logger(mensagem):
    try:
        now = datetime.datetime.now()
        file = open(variaveis["LOG"] + "\\Log_carga-" + str(now.strftime("%m")) + "-" + str(now.year) + ".log", "a", encoding="UTF-8")
        file.write(now.strftime("%d-%m-%Y %H:%M:%S") + " - " + mensagem + "\n")
        arcpy.AddMessage(mensagem)
        file.close()
    except Exception as erro:
        logger(str(erro))

def validar_json(json_input):

    # Convertendo o JSON para um objeto Python
    objeto_json = json.loads(json_input)
    
    if(len(objeto_json) > 0):
        # Verificando se os campos esperados existem no objeto
        for empreendimento in objeto_json:
            for campo, tipo in campos_esperados.items():
                if(campo not in empreendimento or not isinstance(empreendimento[campo], tipo)):
                    logger("Json invalido.")   
                    logger("Campo invalido ou tipo incorreto: {}".format(campo))   
                    raise Exception("Json invalido, faltam campo ou preenchimento incorreto.")
                if(empreendimento[campo] == None or empreendimento[campo] == ""):
                    logger(f"Campo Vazio: {campo}")
    else:
        logger("Json Vazio.")   
        raise Exception("Json Vazio.")
    
def limpa_gdb_temp(CAMADA_OVER):

    OVERLAP_EXPORT_line = f"{variaveis['DATA_SET_TEMP']}\{variaveis['OVERLAP_EXPORT']}_line"
    OVERLAP_EXPORT_point = f"{variaveis['DATA_SET_TEMP']}\{variaveis['OVERLAP_EXPORT']}_point"
    OVERLAP_EXPORT_poly = f"{variaveis['DATA_SET_TEMP']}\{variaveis['OVERLAP_EXPORT']}_poly"

    if(arcpy.Exists(CAMADA_OVER)): 
        arcpy.DeleteRows_management(CAMADA_OVER)
    if(arcpy.Exists(OVERLAP_EXPORT_line)):
        arcpy.Delete_management(OVERLAP_EXPORT_line)
    if(arcpy.Exists(OVERLAP_EXPORT_point)):
        arcpy.Delete_management(OVERLAP_EXPORT_point)
    if(arcpy.Exists(OVERLAP_EXPORT_poly)):
        arcpy.Delete_management(OVERLAP_EXPORT_poly)

def zip_relatorios(targetFolder):
    caminho_final = os.path.join(arcpy.env.scratchFolder, "Relatorios.zip")

    zipObj = ZipFile(caminho_final, "w")
    os.chdir(targetFolder)
    for file in os.listdir(targetFolder):
        zipObj.write(file)
    zipObj.close()
    
    return caminho_final