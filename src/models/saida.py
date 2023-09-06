import json
from utils import logger

class Saida():
    def __init__(self):
        self.json_status = "Invalido"
        self.saidas = [
            {
                "Empreendimento": None,
                "Parque": {},
                "UnidadeGeradora": {},
                "LinhaTransmissao": {}
            }
        ]
        self.saidas_agrupadas = self.saidas
        self.json = self.to_dict()
    
    def to_dict(self):
        return json.dumps({
            "json_status": self.json_status,
            "resultados": self.saidas_agrupadas
        })
    
       