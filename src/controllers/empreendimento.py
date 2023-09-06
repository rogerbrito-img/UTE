import os
from utils import *
from impressao import *
from models.saida import Saida
from models.parque import Parque
from models.subestacao import Subestacao
from models.unidade_geradora import UnidadeGeradora
from models.linha_transmissao import LinhaTransmissao
from models.ponto_referencia import PontoReferencia


class Empreendimento():
    def __init__(self, empreendimento, index, complexo_id):
        self.empreendimento = empreendimento
        self.parque = None
        self.poligono_area_total_ug = None
        #self.unidade_geradora = None
        self.linha_transmissao = None
        self.subestacao = None
        self.ponto_referencia = None
        self.saida = Saida()
        self.complexo_id = complexo_id
        self.iniciar_processamento(index)
        self.validacoes()
        self.insere_dados_banco()
        #self.impressao_relatorio()
        self.deleta_features()
        logger("*********** ------------------------ ***********\n")
        
    def iniciar_processamento(self, index):
        logger("Iniciado montagem dos objetos.")
        shape_folder = os.path.join(arcpy.env.scratchFolder, 'shapefiles')
        if not os.path.exists(shape_folder):
            os.mkdir(shape_folder)
        self.parque = Parque(self.empreendimento["Fonte"],  self.empreendimento["Ceg"],  self.empreendimento["Id"],  self.empreendimento["NomeEmpreendimento"],  self.empreendimento["Empresa"],  self.empreendimento["DtEntOpTeste"],  self.empreendimento["DtEntOpComercial"],  self.empreendimento["Poligono"], self.empreendimento["Potencia_Instalada"], index)
        self.linha_transmissao = LinhaTransmissao(self.empreendimento["LinhaTransmissao"])
        self.subestacao = Subestacao(self.empreendimento["CentroideSubestacao"])
        self.ponto_referencia = PontoReferencia(self.empreendimento["PontoReferencia"])
        logger("Finalizado montagem dos objetos.")
        
    def validacoes(self):
        logger("Iniciado validacoes.")
        print("\n")
        self.parque.validacoes()
        print("\n\n")
        self.linha_transmissao.validacoes(self.subestacao.geometria_buffer)
        print("\n\n")
        self.subestacao.validacoes(self.subestacao.geometria_buffer)
        print("\n\n")
        self.ponto_referencia.validacoes(self.ponto_referencia.geometria_buffer)
        print("\n\n")
        logger("Finalizado validacoes")
     
    def deleta_features(self):
        self.parque.deleta_features()
        self.linha_transmissao.deleta_features()
        self.subestacao.deleta_features()
        self.ponto_referencia.deleta_features()
    
    def status_geral(self):
        status_parque = self.parque.classifica_envio()
        # status_unidade_geradora = self.unidade_geradora.classifica_envio()
        status_linha_transmissao = self.linha_transmissao.classifica_envio()
        status_subestacao = self.subestacao.classifica_envio()
        status_ponto_referencia = self.ponto_referencia.classifica_envio()
        return status_parque and status_linha_transmissao and status_subestacao and status_ponto_referencia

    def monta_resultado(self):
        dict_resultado = {
                "Empreendimento": self.parque.nome_empreendimento, 
                "Parque": 
                    {
                    "id_parque": self.parque.id_parque,
                    "dentro_territorio": self.parque.territorio_nacional, 
                    "sobrepoem_outros_parques": self.parque.sobreposicao_parque, 
                    "sobrepoem_mais_limite": self.parque.sobreposicao_maior, 
                    "nome_parques_sobrepostos": self.parque.nome_parques_sobrepostos, 
                    "observacoes": self.parque.mensagens_erro
                    }, 
                "LinhaTrasmisssao": 
                    {
                    "observacoes": self.linha_transmissao.mensagens_erro
                    }, 
                "PontoReferencia": 
                    {
                    "observacoes": self.ponto_referencia.mensagens_erro
                    }
                # Caso necessario, adicionar o campo da substacao posteriormente
                }
        return dict_resultado

    def impressao_relatorio(self):
        dict_obj= monta_de_para(self.linha_transmissao.feature, self.parque.feature, self.subestacao.feature, self.ponto_referencia.feature)
        resultados = self.monta_resultado()
        caminho_relatorio = gerar_relatorio(resultados, dict_obj)
        logger(f"Relatorio salvo em: {caminho_relatorio}")
    
    def insere_dados_banco(self):
        logger("Append do empreendimento: {}".format(self.empreendimento["NomeEmpreendimento"]))
        self.parque.insere_dados_banco(self.complexo_id)
        # self.linha_transmissao.insere_dados_banco(self.parque.id_parque)
        # self.subestacao.insere_dados_banco(self.parque.id_parque)
        # self.ponto_referencia.insere_dados_banco(self.parque.id_parque)
        # self.insere_validacoes()

    # def insere_validacoes(self):
    #     try:
    #         logger('Iniciando Append das Validações')
    #         edit = arcpy.da.Editor(variaveis["SDE_PATH"])
    #         edit.startEditing(False, False)
    #         edit.startOperation()

    #         fields = [self.parque.id_parque, 
    #                   self.parque.territorio_nacional, 
    #                   self.parque.sobreposicao_parque, #";".join(self.parque.nome_parques_sobrepostos),
    #                   self.parque.sobrep_parque_x_lt_aprovada,  ";".join(self.parque.mensagens_erro), 
    #                   self.linha_transmissao.msg_linha_p_ufv_base,
    #                   self.linha_transmissao.linha_transmissao_inconsistente, ";".join(self.linha_transmissao.mensagens_erro),
    #                   self.subestacao.dentro_parque_fotovoltaico, ";".join(self.linha_transmissao.mensagens_erro),
    #                   self.ponto_referencia.territorio_nacional,
    #                   self.ponto_referencia.dentro_parque_fotovoltaico, ";".join(self.ponto_referencia.mensagens_erro)]
    #         with arcpy.da.InsertCursor(os.path.join(variaveis["SDE_PATH"],
    #         variaveis["UTE_V"]), ["CODIGO_UTE", 
    #                               "V_P_TERRITORIO_NACIONAL", 
    #                               "V_P_SOBREPOSICAO_PARQUE", 
    #                               "V_P_SOBREPOSICAO_PARQUE_LINHA", 
    #                               "V_P_OBS", 
    #                               "V_LT_TOPOLOGIA", 
    #                               "V_LT_SOBREPOSICAO_LINHAS",
    #                               "V_LT_OBS", 
    #                               "V_SUB_DENTRO_PARQUE", 
    #                               "V_SUB_OBS",
    #                               "V_PR_TERRITORIO_NACIONAL", 
    #                               "V_PR_DENTRO_PARQUE",
    #                               "V_PR_OBS"]) as cursorInsert:
    #             cursorInsert.insertRow(fields)

    #         edit.stopOperation()
    #         edit.stopEditing(True)
    #         logger('Finalizando o Append das Validações')
    #     except Exception as inst:
    #         logger('Não foi possivel realizar o Append das Validações')
    #         logger(str(inst))
    