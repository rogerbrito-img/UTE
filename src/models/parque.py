import arcpy, os
from utils import *
from models.fuso import Fuso
from config.variaveis import variaveis

class Parque():
    def __init__(self, fonte, ceg, id, nome_empreendimento, empresa, dt_ent_op_teste, dt_ent_op_comercial, poligono, pot_instalada, index):
        self.fonte = fonte
        self.ceg = ceg
        self.id_parque = None
        self.id = id
        self.nome_empreendimento = nome_empreendimento
        self.empresa = empresa
        self.dt_ent_op_teste = dt_ent_op_teste
        self.dt_ent_op_comercial = dt_ent_op_comercial
        self.poligono = poligono
        self.geometria = None
        self.territorio_nacional = None
        self.feature = None
        self.sobreposicao_parque = None
        self.sobreposicao_maior = None
        self.potencia_instalada = pot_instalada
        self.sobrep_parque_x_lt_aprovada = None
        self.nome_parques_sobrepostos = []
        self.mensagens_erro = []
        self.cria_geometria(index)
        
    def cria_geometria(self, index):
        logger("Criando geometria da Usina Termoelétricas")
        array = arcpy.Array()
        for par_coodenadas in self.poligono:
            long = float(par_coodenadas["Long"])
            lat = float(par_coodenadas["Lat"])
            array.append(arcpy.Point(long, lat))
        
        srs = arcpy.SpatialReference(variaveis["SR"])
        self.geometria = arcpy.Polygon(array, srs)
        caminho = arcpy.management.CreateFeatureclass(os.path.join(arcpy.env.scratchFolder, 'shapefiles'), f"PARQUE_TERMOELETRICAS_{index}", geometry_type="POLYGON", template=variaveis["TEMPLATE_UTE_P"], spatial_reference=arcpy.SpatialReference(variaveis["SR"]))
        self.feature = caminho.__str__()
        self.adiciona_geometria()
        logger("Finalizado processo de criação da geometria da Usina Termoelétricas")
        
    def adiciona_geometria(self):
        with arcpy.da.InsertCursor(self.feature, ["SHAPE@"]) as insert:
            insert.insertRow([self.geometria])
        
    def validacoes(self):
        logger("Iniciado validações da Usina Termoelétricas")
        self.verifica_geometria()
        self.verifica_dentro_territorio_nacional()
        self.verifica_sobreposicao_entre_parques()
        self.valida_sobreposicao_parque_x_linhas_de_transmissao()
        logger("Finalizado validações da Usina Termoelétricas")

    def verifica_geometria(self):
        if self.geometria.area == 0.0:
            self.mensagens_erro.append("Geometria de usina Termoelétricas invalida")

    def verifica_dentro_territorio_nacional(self):
        try:
            with arcpy.da.SearchCursor(variaveis["CMD_TERRITORIO_BRASIL"], ["SHAPE@"]) as cursor:
                for row in cursor:
                    brasil = row[0]
            self.territorio_nacional = self.geometria.within(brasil)
            logger(f"Dentro do Territorio Brasileiro? {self.territorio_nacional}")
        except Exception as erro:
            self.territorio_nacional = False
            self.mensagens_erro.append("Não foi possivel verificar se o parque esta dentro do territorio nacional")
            logger(str(erro))

         
    def verifica_sobreposicao_entre_parques(self):
        try:
            logger("Verificando se poligono da usina termoelétricas sobrepoem algum outro poligono da usina")
            arcpy.management.MakeFeatureLayer(variaveis["UTE_P_BASE"], "PARQUES_UTE_BASE")
            arcpy.management.SelectLayerByLocation("PARQUES_UTE_BASE","INTERSECT", self.geometria,"0 Meters","NEW_SELECTION","NOT_INVERT")
            parques_sobrepostos = []
            with arcpy.da.SearchCursor("PARQUES_UTE_BASE", ["SHAPE@", "NOME_UTE"]) as cursor_registros: # renomear
                for registro in cursor_registros:
                    parques_sobrepostos.append(registro[1])
            arcpy.management.SelectLayerByLocation("PARQUES_UTE_BASE","INTERSECT",self.geometria,"-50 Centimeters","NEW_SELECTION","NOT_INVERT")
            
            self.sobreposicao_parque = bool(len(parques_sobrepostos))
            self.sobreposicao_maior = bool(int(arcpy.GetCount_management("PARQUES_UTE_BASE")[0]))
            self.nome_parques_sobrepostos = ', '.join(list(set(parques_sobrepostos)))
            
            if self.nome_parques_sobrepostos == '':
                self.nome_parques_sobrepostos = "Sem sobreposição"

            
            logger(f"Parques sobrepostos menos que 50cm? {self.sobreposicao_maior}")
            logger(f"Parques sobrepostos mais que 50cm? {self.sobreposicao_parque}")
            logger(f"Nome dos parques sobrepostos: {self.nome_parques_sobrepostos}")
            
            arcpy.Delete_management("PARQUES_UTE_BASE")
            #arcpy.Delete_management("PARQUES_FOTOVOLTAICOS_TEMPORARIA_PORTAL") # Essa variavel é realmente necessaria?
        except Exception as erro:
            self.sobreposicao_parque = True
            self.sobreposicao_maior = True
            self.nome_parques_sobrepostos = []
            self.mensagens_erro.append("Não foi possivel verificar a sobreposição entre os parques.")
            logger(str(erro))

    def valida_sobreposicao_parque_x_linhas_de_transmissao(self):
        try:
            logger("Verificando se o parque esta dentro da margem de seguranca das linhas de transmissao")
            arcpy.MakeFeatureLayer_management(variaveis["UTE_LT_EOL_BASE"], "LINHA_TRANSMISSAO_TEMPORARIA_EOL_LT") # nome de variaveis diferentes do arquivo 'variaveis'
            arcpy.MakeFeatureLayer_management(variaveis["UTE_LT_AHE_BASE"], "LINHA_TRANSMISSAO_TEMPORARIA_AHE_LT")
            arcpy.MakeFeatureLayer_management(variaveis["UTE_LT_UFV_BASE"], "LINHA_TRANSMISSAO_TEMPORARIA_UFV_LT")
            arcpy.MakeFeatureLayer_management(variaveis["UTE_LT_UTE_BASE"], "LINHA_TRANSMISSAO_TEMPORARIA_UTE_LT")
            arcpy.MakeFeatureLayer_management(variaveis["UTE_LT_SIGET_BASE"], "LINHA_TRANSMISSAO_TEMPORARIA_SIGET_LT")
            arcpy.CreateFeatureclass_management("IN_MEMORY","PARQUE_TEMPORARIO","POLYGON",variaveis["UTE_P_BASE"], spatial_reference=arcpy.SpatialReference(variaveis["SR"]))
            with arcpy.da.InsertCursor("IN_MEMORY/PARQUE_TEMPORARIO", ["SHAPE@"]) as cursorInsert:
                cursorInsert.insertRow([self.geometria])
            arcpy.MakeFeatureLayer_management("IN_MEMORY/PARQUE_TEMPORARIO", "PARQUE_TEMPORARIO_2")
            arcpy.SelectLayerByLocation_management("PARQUE_TEMPORARIO_2","INTERSECT", "LINHA_TRANSMISSAO_TEMPORARIA_EOL_LT","60 Meters","NEW_SELECTION","NOT_INVERT")
            parque_x_EOL_LT = arcpy.GetCount_management("PARQUE_TEMPORARIO_2")[0]
            arcpy.SelectLayerByLocation_management("PARQUE_TEMPORARIO_2","INTERSECT","LINHA_TRANSMISSAO_TEMPORARIA_AHE_LT","60 Meters","NEW_SELECTION","NOT_INVERT")
            parque_x_AHE_LT = arcpy.GetCount_management("PARQUE_TEMPORARIO_2")[0]
            arcpy.SelectLayerByLocation_management("PARQUE_TEMPORARIO_2","INTERSECT","LINHA_TRANSMISSAO_TEMPORARIA_UFV_LT","60 Meters","NEW_SELECTION","NOT_INVERT")
            parque_x_UFV_LT = arcpy.GetCount_management("PARQUE_TEMPORARIO_2")[0]
            arcpy.SelectLayerByLocation_management("PARQUE_TEMPORARIO_2","INTERSECT","LINHA_TRANSMISSAO_TEMPORARIA_UTE_LT","60 Meters","NEW_SELECTION","NOT_INVERT")
            parque_x_UTE_LT = arcpy.GetCount_management("PARQUE_TEMPORARIO_2")[0]
            arcpy.SelectLayerByLocation_management("PARQUE_TEMPORARIO_2","INTERSECT","LINHA_TRANSMISSAO_TEMPORARIA_SIGET_LT","60 Meters","NEW_SELECTION","NOT_INVERT")
            parque_x_SIGET_LT = arcpy.GetCount_management("PARQUE_TEMPORARIO_2")[0]
            if(parque_x_EOL_LT != "0"):
                self.sobrep_parque_x_lt_aprovada = ("ATENCAO: linha de transmissao EOL_LT sobrepondo Parque Fotovoltaico.")
                logger(self.sobrep_parque_x_lt_aprovada)
            if(parque_x_AHE_LT != "0"):
                self.sobrep_parque_x_lt_aprovada = ("ATENCAO: linha de transmissao AHE_LT sobrepondo Parque Fotovoltaico.")
                logger(self.sobrep_parque_x_lt_aprovada)
            if(parque_x_UFV_LT != "0"):
                self.sobrep_parque_x_lt_aprovada = ("ATENCAO: linha de transmissao UFV_LT sobrepondo Parque Fotovoltaico.")
                logger(self.sobrep_parque_x_lt_aprovada)
            if(parque_x_UTE_LT != "0"):
                self.sobrep_parque_x_lt_aprovada = ("ATENCAO: linha de transmissao UTE_LT sobrepondo Parque Fotovoltaico.")
                logger(self.sobrep_parque_x_lt_aprovada)
            if(parque_x_SIGET_LT != "0"):
                self.sobrep_parque_x_lt_aprovada = ("ATENCAO: linha de transmissao sobrepondo Parque Fotovoltaico.")   
                logger(self.sobrep_parque_x_lt_aprovada)
        except Exception as erro:
            logger(str(erro))
            logger('Nao foi possivel validar se alguma linha de transmissao esta sobreponto o Parque Fotovoltaico')
        finally:
            arcpy.Delete_management("LINHA_TRANSMISSAO_TEMPORARIA_EOL_LT")
            arcpy.Delete_management("LINHA_TRANSMISSAO_TEMPORARIA_AHE_LT")
            arcpy.Delete_management("LINHA_TRANSMISSAO_TEMPORARIA_UFV_LT")
            arcpy.Delete_management("LINHA_TRANSMISSAO_TEMPORARIA_UTE_LT")
            arcpy.Delete_management("LINHA_TRANSMISSAO_TEMPORARIA_SIGET_LT")
            arcpy.Delete_management("IN_MEMORY/PARQUE_TEMPORARIO")
            arcpy.Delete_management("PARQUE_TEMPORARIO_2")
    
    def sobreposicao_parque_x_parques_analise(self):
            logger("Verificando se o poligono do parque sobrepoe outros parques em analise.")
            try:
                arcpy.MakeFeatureLayer_management(variaveis["banco_UFV"], "PARQUES_FOTOVOLTAICOS_TEMP")
                arcpy.SelectLayerByLocation_management("PARQUES_FOTOVOLTAICOS_TEMP", "INTERSECT", self.parque_geometria, "-50 Centimeters", "NEW SELECTION", "NOT_INVERT")
                sobreposicao_maior_50cm = arcpy.GetCount_management("PARQUES_FOTOVOLTAICOS_TEMP")[0]
                if sobreposicao_maior_50cm != "0":
                    self.sobrep_parque_x_parques_analise = "Sobreposição entre o polígono do parque enviado e a base de dados de Polígono do Parque de Outras Solicitações em Análise"
                    logger("Parque fotovoltaico sobrepondo outro parque mais do que 50cm.")
                else:
                    self.sobrep_parque_x_parques_analise = 'Sem sobreposicoes.'
            except Exception as erro:
                logger("Nao foi possivel verificar se o parque sobrepoe outro parque em analise.")
            finally:
                arcpy.Delete_management("PARQUES_FOTOVOLTAICOS_TEMP")

    def montar_saida(self):
        return {
            "dentro_territorio": self.territorio_nacional,
            "sobrepoem_outros_parques" : self.sobreposicao_parque,
            "sobrepoem_mais_limite" : self.sobreposicao_maior,
            "nome_parques_sobrepostos" : self.nome_parques_sobrepostos,
            "mensagens_erro": self.mensagens_erro
        }
    
    def classifica_envio(self):
        return False if(not self.territorio_nacional or self.sobreposicao_parque or self.sobreposicao_maior) else True

    def deleta_features(self):
        arcpy.Delete_management(self.feature)

    
    def insere_dados_banco(self, complexo_id):
            try:
                logger('Iniciando Append do Parque')
                edit = arcpy.da.Editor(variaveis["SDE_PATH"])
                edit.startEditing(False, False)
                edit.startOperation()
                fields = [complexo_id, self.id, self.ceg, self.nome_empreendimento, self.empresa, self.dt_ent_op_teste, self.dt_ent_op_comercial, self.potencia_instalada, self.geometria]
                with arcpy.da.InsertCursor(os.path.join(variaveis["SDE_PATH"],variaveis["DATASET"],variaveis["UTE_P"]), ["P_COMPLEXO_ID", "P_ID", "P_CEG", "P_EMPREENDIMENTO", "P_EMPRESA", "P_DT_OP_TESTE", "P_DT_OP_COMERCIAL", "P_POTENCIA_INSTALADA", "Shape"]) as cursorInsert:
                    oid = cursorInsert.insertRow(fields)
                with arcpy.da.UpdateCursor(os.path.join(variaveis["SDE_PATH"],variaveis["DATASET"],variaveis["UTE_P"]), ["CODIGO_UTE"], where_clause="OBJECTID = {}".format(oid)) as cursorUpdate:
                    for row in cursorUpdate:
                        cursorUpdate.updateRow([oid])
                edit.stopOperation()
                edit.stopEditing(True)
                self.id_parque = oid
                logger('Finalizando o Append do Parque')
            except Exception as inst:
                logger('Não foi possivel realizar o Append do Parque')
                logger(str(inst))