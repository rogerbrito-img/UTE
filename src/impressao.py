import arcpy, os, json
from datetime import datetime
from arcpy import env
from arcgis.gis import GIS
from typing import Dict, Any, List
from arcpy.da import InsertCursor
from arcpy import env, Extent, SpatialReference, Polygon, Describe
from arcpy.management import CreateFeatureclass, MinimumBoundingGeometry, Delete
from config.variaveis import variaveis
from utils import *


# json_resultado-> dict do empreendimento
def gerar_relatorio(json_resultado, dict_feat):
    logger(f"Gerando relatorio de validacao do empreendimento: {json_resultado['Empreendimento']}")
    try:
        arcpy.SetLogHistory(False)
        logger("Historico desativado")

        GIS(variaveis["URL_PORTAL"], variaveis["USR_PORTAL"], variaveis["PSW_PORTAL"], "true")
        logger("Logado no GIS")
    
        aprx = arcpy.mp.ArcGISProject(variaveis["PROJECT"])
        logger("Projeto Aberto")
    
        relatorio = aprx.listLayouts()[0]
        logger("Relatorio Aberto")
        
        mapa = aprx.listMaps()[0]
        logger("Mapa Aberto")
        
        mapFrame = relatorio.listElements("MAPFRAME_ELEMENT")[0]
        logger("Elemetos Aberto")
        
        mapFrame.map = mapa
    
    except Exception as erro:
        logger(str(erro))

    lyrExtents = []
    spatialRef = SpatialReference(variaveis['SR'])
    for item, val in dict_feat.items():
            layer = mapFrame.map.addDataFromPath(val['shape'])
            layer.name = item
            # arcpy.ApplySymbologyFromLayer_management(layer, val['lyrx'])
            if(layer.name in ["Parque Termoelétrico"]):
                item_extent = json.loads(mapFrame.getLayerExtent(layer).JSON)
                lyrExtents.append(
                    Extent(
                    item_extent['xmin'],
                    item_extent['ymin'],
                    item_extent['xmax'],
                    item_extent['ymax'],
                    spatial_reference=spatialRef
                    )
                )

    mapExtent = get_map_extent(lyrExtents, spatialRef)
    mapFrame.camera.setExtent(mapExtent)
    mapFrame.camera.scale = mapFrame.camera.scale * 1.00
    mapa.defaultCamera = mapFrame.camera

    lista_obs = [''.join(x) for x in list(get_obs(json_resultado, 'observacoes')) if x]
    obs = "\n".join(lista_obs)
    #array_resultado = [obs, json_resultado['Empreendimento'], json_resultado['Interferencia']['interferindo_em'], json_resultado['Interferencia']['interferido_por'], "Valido", json_resultado['Parque']['nome_parques_sobrepostos']]
    #array_resultado = [json_resultado['Parque']['id_parque'], obs, json_resultado['Empreendimento'], json_resultado['Interferencia']['interferindo_em'], json_resultado['Interferencia']['interferido_por'], "Valido", json_resultado['Parque']['nome_parques_sobrepostos']]
    #array_resultado = [json_resultado['Parque']['id_parque'], cpf_cnpj, json_resultado['Empreendimento'],"Valido", json_resultado['Parque']['nome_estado'], json_resultado['Parque']['nome_municipio']]
    array_resultado = [obs, json_resultado['Empreendimento'], json_resultado['Parque']['nome_parques_sobrepostos'],"Valido"]
    custom_elements = monta_custom_text_elements(array_resultado)

    for k, v in custom_elements.items(): 
        for item in relatorio.listElements("TEXT_ELEMENT", '{*}'): 
            if item.name == k: 
                item.text = v

    caminho_saida = os.path.join(arcpy.env.scratchFolder, 'relatorios')
    if not os.path.exists(caminho_saida):
        os.mkdir(caminho_saida)    

    nome_empreend = json_resultado['Empreendimento']
    # Exporta o PDF georreferenciado
    caminho_final = os.path.join(caminho_saida, "{0}.pdf".format(nome_empreend))
    relatorio.exportToPDF(caminho_final, georef_info=True)
    logger("Relatorio gerado com sucesso")
    return caminho_final

def monta_custom_text_elements(array):
    # observacao, nome_empreendimento, parques_interferidos_em, parques_interferidos_por, validacao_final, parques_sobrepostos = array
    # dro, id_parque, nome_empreendimento, validacao_final, estado, municipio, cpf_cnpj = array
    observacao, nome_empreendimento, parques_sobrepostos, validacao_final = array
    dt = datetime.datetime.now()
    data = dt.strftime("%d/%m/%Y")
    custom_text_elements = {
        #"{lbl_InterferidoPor}" : parques_interferidos_por,
        "{lbl_NomeEmpreendimento}" : nome_empreendimento,
        #"{lbl_ParquesInterferidos}" : parques_interferidos_em,
        #"{lbl_ParqueSobrepostos}" : parques_sobrepostos,
        "{lbl_ValidacaoFinal}" : validacao_final,
        "{lbl_Observacao}" : observacao,
        "{lbl_DataEmissao}" : data,
        "{lbl_LinhaTRSE}" : '',
        "{lbl_MunEstadoReqCNPJ}" : '',
        "{lbl_NumeroRecibo}" : '',
        "{lbl_NomeArquivo}" : '',
        "{lbl_DataValidacao}" : data
    }
    return custom_text_elements

def get_obs(data, key):
    if isinstance(data, list):
        # check nested elements
        for item in data:
            yield from get_obs(item, key)
    elif isinstance(data, dict):
        # check key in dictionary
        if key in data.keys():
            #print(data[key])
            yield data[key]
        # check nested elements
        for item in data.values():
            yield from get_obs(item, key)

def monta_de_para(LT, PQ, SUB, PR): # (LT, P, SE, AI, AG) def monta_de_para(LT, P, SE, UG, PR): 
    dict_obj = {
        "Linha de Transmissão": {
            "shape": LT,
            "lyrx": variaveis["LAYER_UTE_LT"]
        },
        "Parque Termoelétrico": {
            "shape": PQ,
            "lyrx": variaveis["LAYER_UTE_P"]
        },
        "Subestação": {
            "shape": SUB,
            "lyrx": variaveis["LAYER_UTE_SE"]
        },
        "Ponto de Referência": {
           "shape": PR,
           "lyrx": variaveis["LAYER_UTE_PR"]
        }
    }
    return dict_obj

def get_map_extent(layer_extents, spatialRef):
    # Calculando o extent global de todas as classes de feição
    polygon_extents_resultado: List[Polygon] = [
        extent.polygon for extent in layer_extents
    ]
    feature_class_extent = CreateFeatureclass(
        "memory", "extent", "POLYGON", spatial_reference=spatialRef
    )
    with InsertCursor(feature_class_extent, ["SHAPE@"]) as cursor:
        for polygon_extent_resultado in polygon_extents_resultado:
            cursor.insertRow([polygon_extent_resultado])
    MinimumBoundingGeometry(
        os.path.join("memory", "extent"),
        os.path.join("memory", "envelope"),
        "ENVELOPE",
        "ALL",
        None,
        "NO_MBG_FIELDS",
    )
    Delete(os.path.join("memory", "extent"))

    mapExtent = Describe(os.path.join("memory", "envelope")).extent
    Delete(os.path.join("memory", "envelope"))
    return mapExtent