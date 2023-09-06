import arcpy
import sys
from utils import *
from models.complexo import Complexo
from models.saida_geral import SaidaGeral
from controllers.empreendimento import Empreendimento

# JSON de entrada para o ArcGIS:
#json_entrada = arcpy.GetParameterAsText(0)
    # json_entrada = '[]'

#json_entrada = '[{"Fonte":"UTE","Ceg":"UFVRSSP052406-9","Id":4332,"NomeEmpreendimento":"TESTE UTE","Empresa":"INSTITUTO DE PESQUISA ECONÔMICA APLICADA","Potencia_Instalada":6666.66,"DtEntOpTeste":"11/2000","DtEntOpComercial":"09/2050","Poligono":[{"Long":-47.082736335999982,"Lat":-4.8217524599999706 },{"Long":-47.045523236999941,"Lat":-4.6795078939999257},{"Long":-46.859169474999931,"Lat":-4.7198728089999804},{"Long":-46.891553588999955,"Lat":-4.8188601699999367},{"Long":-46.943201635999969,"Lat":-4.9767277829999443},{"Long":-47.154583640999931,"Lat":-5.0025681769999437},{"Long":-47.082736335999982,"Lat":-4.8217524599999706}],"LinhaTransmissao":[{"Long":-46.986079236999956,"Lat":-4.749671277999937},{"Long":-46.986079040999982,"Lat":-4.7496712949999278},{"Long":-46.986078823999947,"Lat":-4.7496713139999542},{"Long":-46.98607863999996,"Lat":-4.7496713299999556},{"Long":-46.986078447999944,"Lat":-4.7496713469999463}],"CentroideSubestacao":[{"Long":-46.986079258999951,"Lat":-4.7496712769999476}]}]'
#json_entrada = '[{"Fonte":"UTE","Ceg": "","Id":5456,"NomeEmpreendimento":"TESTE RN 161 UTE","Empresa":"AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA","Potencia_Instalada":987.98,"DtEntOpTeste":"11/2000","DtEntOpComercial":"11/2000","Poligono":[{"Long":-37.97328280,"Lat":-10.61009233},{"Long": -37.97096401,"Lat":-10.60921664},{"Long":-37.96538340,"Lat":-10.61065423},{"Long":-37.94013112,"Lat":-10.60706155},{"Long":-37.92639393,"Lat":-10.60679794},{"Long":-37.88239291,"Lat":-10.60660853},{"Long":-37.45675715,"Lat":-10.66213849}],"LinhaTransmissao":[{"Long":-37.97127525,"Lat":-10.61181296},{"Long":-37.97328280,"Lat":-10.61009233},{"Long":-37.97096401,"Lat":-10.60921664},{"Long":-37.96538340,"Lat":-10.61065423},{"Long":-37.94013112,"Lat":-10.60706155},{"Long":-37.92639393,"Lat":-10.60679794},{"Long":-37.88239291,"Lat":-10.60660853},{"Long":-37.45675715,"Lat":-10.66213849}],"CentroideSubestacao":{"Long":-37.97127525,"Lat":-10.61181296},"PontoReferencia":{"Long":-33.11111111,"Lat":-33.00000000}}]'
json_entrada = '[{"Fonte":"UTE","Ceg": "33","Id":5456,"NomeEmpreendimento":"TESTE RN 161 UTE","Empresa":"AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA","Potencia_Instalada":987.98,"DtEntOpTeste":"11/2000","DtEntOpComercial":"11/2000","Poligono":[{"Long":-47.082736335999982,"Lat":-4.8217524599999706 },{"Long":-47.045523236999941,"Lat":-4.6795078939999257},{"Long":-46.859169474999931,"Lat":-4.7198728089999804},{"Long":-46.891553588999955,"Lat":-4.8188601699999367},{"Long":-46.943201635999969,"Lat":-4.9767277829999443},{"Long":-47.154583640999931,"Lat":-5.0025681769999437},{"Long":-47.082736335999982,"Lat":-4.8217524599999706}],"LinhaTransmissao":[{"Long":-46.986079236999956,"Lat":-4.749671277999937},{"Long":-46.986079040999982,"Lat":-4.7496712949999278},{"Long":-46.986078823999947,"Lat":-4.7496713139999542},{"Long":-46.98607863999996,"Lat":-4.7496713299999556},{"Long":-46.986078447999944,"Lat":-4.7496713469999463}],"CentroideSubestacao":{"Long":-46.986079258999951,"Lat":-4.7496712769999476},"PontoReferencia":{"Long":-33.11111111,"Lat":-33.00000000}}]'

# json_entrada = '''[{"Fonte": "UTE",
#   "Ceg": "",
#   "Id": 5456,
#   "NomeEmpreendimento": "TESTE RN 161 UTE",
#   "Empresa": "AGÊNCIA NACIONAL DE ENERGIA ELÉTRICA",
#   "Potencia_Instalada": 987.98,
#   "DtEntOpTeste": "11/2000",
#   "DtEntOpComercial": "11/2000",
#   "Poligono": [
#     {
#       "Long": -37.97328280,
#       "Lat": -10.61009233
#     },
#     {
#       "Long": -37.97096401,
#       "Lat": -10.60921664
#     },
#     {
#       "Long": -37.96538340,
#       "Lat": -10.61065423
#     },
#     {
#       "Long": -37.94013112,
#       "Lat": -10.60706155
#     },
#     {
#       "Long": -37.92639393,
#       "Lat": -10.60679794
#     },
#     {
#       "Long": -37.88239291,
#       "Lat": -10.60660853
#     },
#     {
#       "Long": -37.45675715,
#       "Lat": -10.66213849
#     }
#   ],
#   "LinhaTransmissao": [
#     {
#       "Long": -37.97127525,
#       "Lat": -10.61181296
#     },
#     {
#       "Long": -37.97328280,
#       "Lat": -10.61009233
#     },
#     {
#       "Long": -37.97096401,
#       "Lat": -10.60921664
#     },
#     {
#       "Long": -37.96538340,
#       "Lat": -10.61065423
#     },
#     {
#       "Long": -37.94013112,
#       "Lat": -10.60706155
#     },
#     {
#       "Long": -37.92639393,
#       "Lat": -10.60679794
#     },
#     {
#       "Long": -37.88239291,
#       "Lat": -10.60660853
#     },
#     {
#       "Long": -37.45675715,
#       "Lat": -10.66213849
#     }
#   ],
#   "CentroideSubestacao": {
#     "Long": -37.97127525,
#     "Lat": -10.61181296
#   },
#   "PontoReferencia": {
#     "Long": -33.11111111,
#     "Lat": -33.00000000
#   }
# }]'''



if(__name__ == "__main__"):
    try:
        remove_shapefiles()
        saida_geral = SaidaGeral()
        complexo = Complexo(json_entrada, saida_geral)       
        logger("Processamento Iniciado.")
        complexo.insere_dados_banco()
        for index, empreendimento in enumerate(complexo.obj_json):
            complexo.adiciona(Empreendimento(empreendimento, index, complexo.complexo_id))
        if(len(complexo.empreendimentos) > 1):
            complexo.validacao_entre_parques()
        saida_geral.montar_saida(complexo.empreendimentos)
        # complexo.classifica_envio() # Conforme doc recebido dia 12/07/23 não teremos regras impeditivas.
        caminho_zip = saida_geral.montar_zip()
        logger("Processamento Finalizado.")
        arcpy.SetParameter(1, caminho_zip)
    except Exception as erro:
        logger(str(erro))
        sys.exit(1)