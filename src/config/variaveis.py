variaveis = dict(
    # COORDENADAS
    SR = 4674, # Código KWID da referencia espacial SIRGAS 2000
    
    # CAMINHOS
    LOG = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\LOG", # Pasta onde seram gravados os arquivos de log
    pasta_shp_ = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\shp", # Pasta onde seram adicionados a saida do processo de criação da região de interferencia

    #CAMINHO_PASTA_GDB_TEMP = r"C:\GDB_TEMP",
    #CAMINHO_PASTA_ARQUIVOS_EXTRAIDOS = None,
    GDB_TEMP = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\GDB_TEMP\TEMP.gdb",
    DATA_SET_TEMP = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\GDB_TEMP\TEMP.gdb\DATASET", #necessita do arquivo local

    # EXTERNO
    CMD_TERRITORIO_BRASIL = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Externos\BRASIL_ZEE", # Externo base
    CMD_FUSO = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Externos\FUSO", # Externo base  

    PROJECT = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\project.aprx",
    LAYOUT_PAGX = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layout\ValidadorInternoUFVv2.pagx",
        
    TEMPLATE_UTE_P = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Template\UTE_P", # Template
    TEMPLATE_UTE_AG = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Template\UTE_UG", # Template
    TEMPLATE_UTE_LT = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Template\UTE_LT", # Template
    TEMPLATE_UTE_SE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Template\UTE_SE", # Template
    TEMPLATE_UTE_RI = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\Template\UTE_RI", # Template

    LAYER_UTE_P = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\P.lyrx",
    LAYER_UTE_AG = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\AG.lyrx",
    LAYER_UTE_UG = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\UG.lyr",
    LAYER_UTE_LT = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\LT.lyrx",
    LAYER_UTE_SE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\SE.lyrx",
    LAYER_UTE_RI = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\AI.lyrx",
    LAYER_UTE_PR = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\src\templates\Layers\PR.lyr",
    
    # Verificar arquivos do Default, se eles sao apenas para Eolica ou geral 
    # BASE
    UTE_RI_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\UTE_RI_BASE", # Região de interferencia da BASE ANEEL
    UTE_P_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\UTE_P_BASE", # Parques da BASE ANEEL
    UTE_LT_EOL_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\LinhaTransmissao_EOL", # LT da BASE ANEEL
    UTE_LT_AHE_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\LinhaTransmissao_AHE", # LT da BASE ANEEL
    UTE_LT_UFV_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\LinhaTransmissao_UFV", # LT da BASE ANEEL
    UTE_LT_UTE_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\LinhaTransmissao_UTE", # LT da BASE ANEEL
    UTE_LT_SIGET_BASE = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb\BASE\LinhaTransmissao_SIGET", # LT da BASE ANEEL
    
    # PORTAL
    URL_PORTAL = "https://sigel.aneel.gov.br/portal",
    USR_PORTAL = "portaladmin",
    PSW_PORTAL = "hWCv5Abu",

    SDE_PATH = r"C:\Tarefas\ANEEL\OS31\validador-interno-ute\UTE\project\Default.gdb",

    # UFV_APROVADOS = r"C:\repos\validador-ufv\Geodatabases\PORTAL_COPIA.gdb\UFV_P",
    # UFV_PONTO_REF_APROVADOS = r"C:\repos\validador-ufv\Geodatabases\PORTAL_COPIA.gdb\UFV_REF",
    # UFV_LT_APROVADA = r"C:\repos\validador-ufv\Geodatabases\PORTAL_COPIA.gdb\UFV_LT",

    # NOMES PADRAO
    TOPOLOGIA = "\TOPOLOGIA",
    OVERLAP_EXPORT = "OVERLAP_EXPORT",
    
    UTE_C = "UTE_SCGGO_COMPLEXO",
    UTE_V = "UTE_SCGGO_V",
    DATASET = "SCGGO",
    UTE_P = "UTE_SCGGO_P",
    UTE_SE = "UTE_SCGGO_SUB",
    UTE_LT = "UTE_SCGGO_LT",
    UTE_PR = "UTE_SCGGO_PR"


)