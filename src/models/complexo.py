import arcpy
from utils import *
from models.saida import Saida

class Complexo():
    def __init__(self, json_entrada, saida_geral):
        self.empreendimentos = []
        self.sobreposicao_entre_parques = None
        self.status_geral = False
        validar_json(json_entrada)
        saida_geral.json_status = "Valido"
        self.obj_json = json.loads(json_entrada)
        
    def adiciona(self, empreendimento):
        self.empreendimentos.append(empreendimento)
        
    def validacao_entre_parques(self):
        logger("Iniciado processo de validação entre parques enviados.")        
        index = 0
        for empreendimento in self.empreendimentos:
            index += 1
            if(index < len(self.empreendimentos)):
                for index_empreendimento in range(index, len(self.empreendimentos)):
                    arcpy.MakeFeatureLayer_management(empreendimento.parque.feature,  'EMPREENDIMENTO_1')
                    arcpy.MakeFeatureLayer_management(self.empreendimentos[index_empreendimento].parque.feature, 'EMPREENDIMENTO_2')
                    arcpy.SelectLayerByLocation_management('EMPREENDIMENTO_1', 'INTERSECT', 'EMPREENDIMENTO_2', "-50 Centimeters", "NEW_SELECTION", "NOT_INVERT")
                    self.sobreposicao_entre_parques = bool(int(arcpy.GetCount_management("EMPREENDIMENTO_1")[0]))
                    arcpy.Delete_management("EMPREENDIMENTO_1")
                    arcpy.Delete_management("EMPREENDIMENTO_2")
        logger(f"Existe sobreposição entre os parques enviados? {self.sobreposicao_entre_parques}")
        logger("Finalizado processo de validação entre parques enviados.")        

    def classifica_envio(self):
        logger("Classificando envio")
        lista_status_empreendimento = []
        for empreendimento in self.empreendimentos:
            lista_status_empreendimento.append(empreendimento.status_geral())
        
        self.status_geral = False if(False in lista_status_empreendimento) else True
        logger(f"Status do envio: {str(self.status_geral)}" )

    def agrupar_saidas(self):
        self.saida.montar_saida(self.empreendimentos)
        self.saida.to_dict()

    def insere_dados_banco(self):
        try:
            logger('Iniciando Append do Complexo')
            edit = arcpy.da.Editor(variaveis["SDE_PATH"])
            edit.startEditing(False, False)
            edit.startOperation()
            fields = [self.getJobID()]
            with arcpy.da.InsertCursor(os.path.join(variaveis["SDE_PATH"],variaveis["UTE_C"]), ["JOB_ID"]) as cursorInsert:
                oid = cursorInsert.insertRow(fields)
            #edit.stopOperation()
            #edit.stopEditing(True)
            
            #edit.startEditing(False, False)
            #edit.startOperation()
            with arcpy.da.UpdateCursor(os.path.join(variaveis["SDE_PATH"],variaveis["UTE_C"]), ["COMPLEXO_ID"], where_clause="OBJECTID = {}".format(oid)) as cursorUpdate:
                for row in cursorUpdate:
                    cursorUpdate.updateRow([oid])
            edit.stopOperation()
            edit.stopEditing(True)
            self.complexo_id = oid
            logger('Finalizando o Append do Complexo')
            logger('ID de Complexo: {}'.format(oid))
        except Exception as inst:
            logger('Não foi possivel realizar o Append do Complexo')
            logger(str(inst))

    def getJobID(self):
        try:
            scr = arcpy.env.scratchFolder
            jobId = os.path.split(os.path.split(scr)[0])[1] #split 'scratch' off, then split remainder and grab guid    
            logger(jobId)
            return jobId
        except Exception as inst:
            logger('ERRO: Não foi possível buscar o JOB ID do processo.')
            logger(inst)