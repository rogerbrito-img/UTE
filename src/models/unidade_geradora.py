import arcpy
from utils import *
from config.variaveis import variaveis
from models.parque import Parque


class UnidadeGeradora():
    def __init__(self, poligono_area_total_ug, potencia_instalada, fuso):
        self.poligono_area_total_ug = poligono_area_total_ug
        self.potencia_instalada = potencia_instalada
        self.fuso = fuso
        self.mensagem_topologia = None
        self.geometria = None
        self.mensagem_topologia = None
        self.feature = None
        #self.mensagens_erro = []
        self.cria_geometria()

    def cria_geometria(self):
        logger("Criando geometria da area total da Unidade Geradora") 
        array = arcpy.Array()
        for par_coodenadas in self.poligono_area_total_ug:
            long = float(par_coodenadas["Long"])
            lat = float(par_coodenadas["Lat"])
            array.append(arcpy.Point(long, lat))
        self.geometria = arcpy.Polygon(array, arcpy.SpatialReference(variaveis["SR"]))
        caminho = arcpy.management.CreateFeatureclass(os.path.join(arcpy.env.scratchFolder, 'shapefiles'), f"PARQUE_FOTOVOLTAICO", geometry_type="POLYGON", template=variaveis["TEMPLATE_UFV_P"], spatial_reference=arcpy.SpatialReference(variaveis["SR"]))
        self.feature = caminho.__str__()
        self.adiciona_geometria()
        #self.projeta_geometria
        logger("Finalizado processo de criação da geometria da Usina Fotovoltaica")

    # def adiciona_geometria(self):
    #     for par_coodenada in self.poligono_area_total_ug:
    #         with arcpy.da.InsertCursor(self.feature, ["SHAPE@"]) as insert:
    #             insert.insertRow([par_coodenada.geometria])   

    def adiciona_geometria(self):
        with arcpy.da.InsertCursor(self.feature, ["SHAPE@"]) as insert:
            insert.insertRow([self.geometria])

    # def projeta_geometria(self):
    #     projetado = self.geometria.projectAs(arcpy.SpatialReference(self.fuso))
    #     return {"X": round(projetado.centroid.X, 2), "Y":round(projetado.centroid.Y, 2)}
    
    def validacoes(self):
        logger("Iniciado validações das Usinas Geradoras")
        #self.valida_coordenadas_vertices()
        self.valida_poligono_topologicamente()
        logger("Finalizado validações das Usinas Geradoras")


    def valida_coordenadas_vertices(self):
        logger("Verificando se as coordenadas dos vertices estao dentro do poligono do parque enviado.")
        try:
            logger('teste')
        except Exception as erro:
            logger("Nao foi possivel verificar se as coordenadas dos vertices estao dentro do poligono do parque enviado.")
        finally:
            logger("teste")
 

    def valida_poligono_topologicamente(self):
        logger("Verificando se as coordenadas do poligono formam uma geometria topologicamente consistente.")
        try:
            camada_in_memoria = "IN_MEMORY/POLIGONO_ENVIADO"
            camada_make = "MAKE_POLYGONO"
            camada_saida = "IN_MEMORY/SAIDA"
            if(arcpy.Exists(camada_saida)):
                arcpy.Delete_management(camada_saida)

            arcpy.CreateFeatureclass_management("IN_MEMORY", "POLIGONO_ENVIADO", "POLYGON", spatial_reference=arcpy.SpatialReference(variaveis["SR"]))
            with arcpy.da.InsertCursor(camada_in_memoria, ["SHAPE@"]) as insertCursor:
                insertCursor.insertRow([self.geometria])

            # Cria a camada em memória a partir do polígono inserido
            arcpy.MakeFeatureLayer_management(camada_in_memoria, camada_make)

            # Realiza a verificação de geometria
            with arcpy.EnvManager(extent="DEFAULT"):
                arcpy.CheckGeometry_management(camada_make, camada_saida, "OGC")

            # Verifica se há problemas de não consistencia
            with arcpy.da.SearchCursor(camada_saida, ["PROBLEM"], where_clause="PROBLEM = 'non simple'") as cursor:
                for row in cursor:
                    logger("Erro na topologia do poligono da Unidade Geradora")
                    self.mensagem_topologia = "As coordenadas informadas na aba Unidade Geradora, formam um poligono inconsistente. Revise a formatacao dos dados e/ou o ordenamento sequencial dos vertices."
                    self.poligono_inconsistente = True
        except Exception as erro:
            logger("Nao foi possivel verificar se as coordenadas formam um poligono topologicamente consistente.")
            self.poligono_inconsistente.mensagem = "Houve um problema na aba Unidade Geradora. Realize uma nova tentativa de submissao."
            self.mensagem_topologia = self.poligono_inconsistente.mensagem
            self.poligono_inconsistente.status = False
        finally:
            arcpy.Delete_management(camada_in_memoria)
            arcpy.Delete_management(camada_make)
            arcpy.Delete_management(camada_saida)


    def deleta_features(self):
        arcpy.Delete_management("IN_MEMORY/GERADO")
        arcpy.Delete_management(self.feature)
        
    def montar_saida(self):
        return {
           # "aegs_dentro_parque": self.aegs_dentro_parque,
            "retorno_topologia": self.mensagem_topologia,
           # "interseccao_AEGs_LT_EOL": self.interseccao_AEGs_LT_EOL,
           # "interseccao_AEGs_LT_AHE": self.interseccao_AEGs_LT_AHE,
           # "interseccao_AEGs_LT_UFV": self.interseccao_AEGs_LT_UFV,
           # "interseccao_AEGs_LT_UTE": self.interseccao_AEGs_LT_UTE,
           # "interseccao_AEGs_LT_SIGET": self.interseccao_AEGs_LT_SIGET,
           # "mensagens_erro": self.mensagens_erro
        }