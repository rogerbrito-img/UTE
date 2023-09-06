import json
from utils import *

class SaidaGeral():
    def __init__(self):
        self.json_status = "Invalido"
        self.empreendimentos = []
        self.json_stringfy = self.to_dict()
    
    def to_dict(self):
        return json.dumps({
            "json_status": self.json_status,
            "empreendimentos": self.empreendimentos
        })
    
    def montar_saida(self, empreendimentos):
        logger("Montando saida")
        lista_saidas = []
        for empreendimento in empreendimentos:
            saida_parcial = {
                "Empreendimento": empreendimento.parque.nome_empreendimento,
                "Parque": empreendimento.parque.montar_saida(),
                "LinhaTrasmisssao": empreendimento.linha_transmissao.montar_saida(),
                "Subestacao": empreendimento.subestacao.montar_saida(), # Conforme doc recebido dia 12/07/23 solicitado remover validação.
                "PontoReferencia": empreendimento.ponto_referencia.montar_saida(),
            }
            lista_saidas.append(saida_parcial)
        logger("Finalizado saida")
        self.empreendimentos = lista_saidas
        self.json_stringfy = self.to_dict()    

    def montar_zip(self):
        logger("Compactando relatorios")
        pasta_relatorios = os.path.join(arcpy.env.scratchFolder, "relatorios")
        caminho = zip_relatorios(pasta_relatorios)
        logger("Arquivo compactado")
        return caminho