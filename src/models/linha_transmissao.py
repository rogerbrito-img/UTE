import arcpy, os
from utils import *
from config.variaveis import variaveis
from models.subestacao import Subestacao


class LinhaTransmissao():
    def __init__(self, linha_transmissao):
        self.linha_transmissao = linha_transmissao
        self.geometria = None
        self.lt_conectada_sub = None
        self.feature = None
        self.msg_linha_p_ufv_base = None
        self.linha_transmissao_inconsistente = None
        self.mensagens_erro = []
        self.cria_geometria()
        
    def cria_geometria(self):
        logger("Criando geometria da Linha de Transmissão")
        array = arcpy.Array()
        for par_coodenadas in self.linha_transmissao:
            long = float(par_coodenadas["Long"])
            lat = float(par_coodenadas["Lat"])
            array.append(arcpy.Point(long, lat))

        srs = arcpy.SpatialReference(variaveis["SR"])
        self.geometria = arcpy.Polyline(array, srs)
        caminho = arcpy.management.CreateFeatureclass(os.path.join(arcpy.env.scratchFolder, 'shapefiles'), "LINHA_TRANSMISSAO", geometry_type="POLYLINE", template=variaveis["TEMPLATE_UTE_LT"], spatial_reference=srs)
        self.feature = caminho.__str__()
        self.adiciona_geometria()
        logger("Finalizado processo de criação da geometria da Linha de Transmissão")
            
    def adiciona_geometria(self):
        with arcpy.da.InsertCursor(self.feature, ["SHAPE@"]) as insert:
            insert.insertRow([self.geometria])
        
    def validacoes(self, geometria_subestacao_buffer):
        logger("Iniciado validações da Linha de Transmissão")
        # self.verifica_conexao_subestacao(geometria_subestacao_buffer) # Conforme doc recebido dia 12/07/23 solicitado remover validação.
        # self.verifica_sobreposicao_entre_parques(geometria_subestacao_buffer)
        self.valida_linha_topologicamente()
        self.verifica_sobreposicao_linha_transmissao()
        logger("Finalizado validações da Linha de Transmissão")

    def verifica_conexao_subestacao(self, geometria_subestacao_buffer):
        self.lt_conectada_sub = self.geometria.crosses(geometria_subestacao_buffer)
        logger(f"Subestação conectada a linha de transmissão? {self.lt_conectada_sub}")  
        

    def verifica_sobreposicao_linha_transmissao(self):
        try:
            logger("Verificando a sobreposicao entre linhas de transmissao.")
            FT_LINHA_TEMPORARIA = "FT_LINHA_TEMPORARIA"
            FT_LINHA_TEMPORARIA_MAKE = "FT_LINHA_TEMPORARIA_MAKE"
            PARQUE_BASE_MAKE = "PARQUE_BASE_MAKE"

            arcpy.management.CreateFeatureclass("IN_MEMORY", FT_LINHA_TEMPORARIA, "POLYLINE", variaveis["UTE_LT_UFV_BASE"], spatial_reference=arcpy.SpatialReference(variaveis["SR"]))

            with arcpy.da.InsertCursor("IN_MEMORY/"+FT_LINHA_TEMPORARIA, ["SHAPE@"]) as cursorInsert:
                cursorInsert.insertRow([self.geometria])

            arcpy.management.MakeFeatureLayer("IN_MEMORY/"+FT_LINHA_TEMPORARIA, FT_LINHA_TEMPORARIA_MAKE)
            arcpy.management.MakeFeatureLayer(variaveis["UTE_P_BASE"], PARQUE_BASE_MAKE)

            arcpy.management.SelectLayerByLocation(FT_LINHA_TEMPORARIA_MAKE, "INTERSECT", PARQUE_BASE_MAKE, "200 Meters", "NEW_SELECTION", "NOT_INVERT")
            RESULT_UFV_AG_BASE = arcpy.GetCount_management(FT_LINHA_TEMPORARIA_MAKE)[0]

            if(RESULT_UFV_AG_BASE != "0"):
                self.msg_linha_p_ufv_base = "ATENCAO: linha de transmissao sobrepondo Poligono de Parque Termoelétrico Aprovado."

        except Exception as erro:
            self.msg_linha_p_ufv_base = "Houve um problema e nao foi possivel realizar a verificacao de intereseccao entre a linha de transmissao e os parques termoelétricos aprovados."
            logger(str(erro))
            logger(self.msg_linha_p_ufv_base)
        finally:
            arcpy.Delete_management("IN_MEMORY/"+FT_LINHA_TEMPORARIA)
            arcpy.Delete_management(FT_LINHA_TEMPORARIA_MAKE)
            arcpy.Delete_management(PARQUE_BASE_MAKE)

# -- Adaptar a seguinte funcao

    def valida_linha_topologicamente(self):
        logger("Verificando se as coordenadas da linha de transmissao formam uma geometria topologicamente consistente.")
        try:
            CAMADA_OVER = f"{variaveis['DATA_SET_TEMP']}\OVERLAP_POLYLINE"
            TOPOLOGIA = f"{variaveis['DATA_SET_TEMP']}\TOPOLOGIA_POLYLINE"

            limpa_gdb_temp(CAMADA_OVER)

            if(not arcpy.Exists(variaveis['DATA_SET_TEMP'])):
                arcpy.CreateFeatureDataset_management(variaveis["GDB_TEMP"], "DATASET", arcpy.SpatialReference(4674))
                arcpy.CreateTopology_management(variaveis["DATA_SET_TEMP"], "TOPOLOGIA_POLYLINE", 0.001)
                arcpy.CreateFeatureclass_management(variaveis["DATA_SET_TEMP"], "OVERLAP_POLYLINE", "POLYLINE", spatial_reference=arcpy.SpatialReference(variaveis["SR"]))

            edit = arcpy.da.Editor(variaveis["GDB_TEMP"])
            edit.startEditing(False, False)
            edit.startOperation()    

            with arcpy.da.InsertCursor(CAMADA_OVER, ["SHAPE@"]) as insertCursor:
                insertCursor.insertRow([self.geometria])

            edit.stopOperation()
            edit.stopEditing(True)
            arcpy.AddRuleToTopology_management(TOPOLOGIA, "Must Not Self-Intersect (Line)", CAMADA_OVER, '', "#", '')
            arcpy.ValidateTopology_management(TOPOLOGIA, visible_extent="Full_Extent")
            arcpy.ExportTopologyErrors_management(TOPOLOGIA, variaveis["DATA_SET_TEMP"], out_basename=variaveis['OVERLAP_EXPORT'])        

            quantidade_registro = arcpy.GetCount_management(f"{variaveis['DATA_SET_TEMP']}\OVERLAP_EXPORT_point")[0]

            if(int(quantidade_registro) > 0):
               self.mensagens_erro = "As coordenadas informadas na aba Linha de Transmissao, a partir da linha 6, formam uma linha inconsistente. Revise a formatacao dos dados e/ou o ordenamento sequencial dos vertices e realize uma nova tentativa de submissao."
               self.linha_transmissao_inconsistente.status = False

        except Exception as erro:
            logger("Nao foi possivel verificar se as coordenadas formam um poligono topologicamente consistente.")
            self.mensagens_erro = "Houve um problema na aba Linha de Tranmissao tente novamente."
            self.linha_transmissao_inconsistente.status = False

    
    def deleta_features(self):
        arcpy.Delete_management("IN_MEMORY/LINHA_TRANSMISSAO")
        arcpy.Delete_management(self.feature)
        
    def montar_saida(self):
        return {
            # "lt_conectada_sub": self.lt_conectada_sub, # Conforme doc recebido dia 12/07/23 solicitado remover validação.
            # "interseccao_LT_enviada_AEGs": self.interseccao_LT_enviada_AEGs,
            "mensagens_erro": self.mensagens_erro
        }
    
    def classifica_envio(self):
        return False if(not self.lt_conectada_sub or self.interseccao_LT_enviada_AEGs) else True
    

    def insere_dados_banco(self, id_parque):
        try:
            logger('Iniciando Append da Linha de Transmissão')
            edit = arcpy.da.Editor(variaveis["SDE_PATH"])
            edit.startEditing(False, False)
            edit.startOperation()

            fields = [id_parque, self.geometria]
            with arcpy.da.InsertCursor(os.path.join(variaveis["SDE_PATH"],variaveis["UTE_LT"]), ["CODIGO_UTE", "SHAPE@"]) as cursorInsert:
                cursorInsert.insertRow(fields)

            edit.stopOperation()
            edit.stopEditing(True)

            logger('Finalizando Append da Linha de Transmissão')
        except Exception as inst:
            logger('Não foi possivel Realizar o Append da Linha de Transmissão')
            logger(str(inst))