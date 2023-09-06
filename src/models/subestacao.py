import arcpy, os
from utils import *
from config.variaveis import variaveis

class Subestacao():
    def __init__(self, centroide_subestacao):
        self.centroide_subestacao = centroide_subestacao
        #self.fuso = fuso
        self.geometria = None
        self.dentro_parque_fotovoltaico = None
        self.geometria_buffer = None
        self.feature = None
        #self.mensagens_erro = []
        self.cria_geometria()
        
    def cria_geometria(self):
        logger("Criando geometria da Subestação")
        # long = float(self.centroide_subestacao[0]["Long"])
        # lat = float(self.centroide_subestacao[0]["Lat"])
        long = float(self.centroide_subestacao["Long"])
        lat = float(self.centroide_subestacao["Lat"])
        ponto = arcpy.Point(long, lat)
        srs = arcpy.SpatialReference(variaveis["SR"])
        self.geometria = arcpy.PointGeometry(ponto, srs)
        self.geometria_buffer = self.geometria.buffer(0.0001945) # Gera um poligono sobre o ponto da subestação com 20m de diametro(Variação: 19,86 ~ 21,54)
        caminho = arcpy.management.CreateFeatureclass(os.path.join(arcpy.env.scratchFolder, 'shapefiles'), "SUBESTACAO", geometry_type="POINT", template=variaveis["TEMPLATE_UTE_SE"], spatial_reference=arcpy.SpatialReference(variaveis["SR"]))
        self.feature = caminho.__str__()
        self.adiciona_geometria()
        logger("Finalizado processo de criação da geometria da Subestação")
        
    def adiciona_geometria(self):
        with arcpy.da.InsertCursor(self.feature, ["SHAPE@"]) as insert:
            insert.insertRow([self.geometria])
           
    def validacoes(self, geometria_parque):
        logger("Iniciado validações da Subestação")
        self.verifica_dentro_parque(geometria_parque)
        self.verifica_dentro_territorio_nacional()
        logger("Finalizado validações da Subestação")        
    
    def verifica_dentro_parque(self, geometria_parque):
        self.dentro_parque_fotovoltaico = self.geometria.within(geometria_parque)
        logger(f"Subestação dentro do Poligono da Usina Termoelétrica? {self.dentro_parque_fotovoltaico}")

    def verifica_dentro_territorio_nacional(self):
        try:
            with arcpy.da.SearchCursor(variaveis["CMD_TERRITORIO_BRASIL"], ["SHAPE@"]) as cursor:
                for row in cursor:
                    brasil = row[0]
            self.territorio_nacional = self.geometria.within(brasil)
            logger(f"Dentro do Territorio Brasileiro? {self.territorio_nacional}")
        except Exception as erro:
            self.territorio_nacional = False
            self.mensagens_erro.append("Não foi possivel verificar se o ponto de referencia esta dentro do territorio nacional")
            logger(str(erro))
        
    def deleta_features(self):
        arcpy.Delete_management("IN_MEMORY/SUBESTACAO")
        arcpy.Delete_management(self.feature)
        
    def montar_saida(self):
        return {
            "dentro_parque_fotovoltaico" : self.dentro_parque_fotovoltaico
        }
    
    def classifica_envio(self):
        return False if(not self.dentro_parque_fotovoltaico) else True
    

    def insere_dados_banco(self, id_parque):
        try:
            logger('Iniciando Append da Subestação')
            edit = arcpy.da.Editor(variaveis["SDE_PATH"])
            edit.startEditing(False, False)
            edit.startOperation()
            geom = json.loads(self.geometria.JSON)
            x = geom['x']
            y = geom['y']

            fields = [id_parque, x, y, self.geometria]
            with arcpy.da.InsertCursor(os.path.join(variaveis["SDE_PATH"],variaveis["UTE_SE"]), ["CODIGO_UTE", "SUB_COORD_X", "SUB_COORD_Y", "SHAPE@"]) as cursorInsert:
                cursorInsert.insertRow(fields)

            edit.stopOperation()
            edit.stopEditing(True)
            logger('Finalizando Append da Subestação')
        except Exception as inst:
            logger('Não foi possivel realizar o Append da Subestação')
            logger(str(inst))