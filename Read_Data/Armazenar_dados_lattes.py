import base64

import pandas as pd
import os
import zipfile
import sys
import xml.etree.ElementTree as ET
from zeep import Client
import csv
import logging
import shutil
from zeep import Client
from zeep.transports import Transport
import time
import requests

# Adicione o diretório raiz do seu projeto ao caminho de busca do Python
projeto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(projeto_dir)

from constants import *

# Configurar o logger
logger = logging.getLogger('dash_app')


class StorageLattes:
    dict_ids = {}
    arquivos_extrator = []
    dicionario_bolsistas = {'ID': [], 'PESQUISADOR': [], 'CATEGORIA_BOLSA': []}
    planilha_bolsistas = None

    def __init__(self, arquivo_base) -> None:

        self.dict_ids = self.gerar_dicionario(arquivo_base)

        if os.path.exists(PASTA_EXTRATOR):
            self.arquivos_extrator = os.listdir(PASTA_EXTRATOR)

    def criar_cliente_zeep(self, url_servico, tentativas=3, delay=2):
        """Tenta criar o cliente Zeep com algumas tentativas"""
        # código para mitigar erros na primeira conexão
        for tentativa in range(1, tentativas + 1):
            try:
                session = requests.Session()
                transport = Transport(session=session, timeout=15)
                cliente = Client(url_servico, transport=transport)
                return cliente
            except Exception as e:
                logger.warning(f"[!] Tentativa {tentativa}/{tentativas} falhou ao criar o cliente: {e}")
                time.sleep(delay * tentativa)
        raise ConnectionError("[X] Não foi possível conectar ao serviço WSDL após múltiplas tentativas.")

    def baixar_dados_docentes(self, lista_ids, pasta_salvamento):
        logger.info("[.] Baixando informacoes de docentes...")
        try:
            if not (os.path.exists(pasta_salvamento)):
                os.makedirs(pasta_salvamento)

            url_servico = "http://servicosweb.cnpq.br/srvcurriculo/WSCurriculo?wsdl"
            cliente = self.criar_cliente_zeep(url_servico)

            def corrigir_padding_base64(s):
                # Se s for bytes, converte para string utf-8
                if isinstance(s, bytes):
                    s = s.decode('utf-8')

                missing_padding = len(s) % 4
                if missing_padding != 0:
                    s += '=' * (4 - missing_padding)
                return s

            for id_lattes in lista_ids:
                resultado_base64 = cliente.service.getCurriculoCompactado(id_lattes)
                nome_arquivo_zip = str(id_lattes) + ".zip"

                if resultado_base64:
                    # se for bytes, salvar direto (assumindo ser zip binário)
                    if isinstance(resultado_base64, bytes):
                        with open(f"{pasta_salvamento}/{nome_arquivo_zip}", 'wb') as arquivo_zip:
                            arquivo_zip.write(resultado_base64)

                    # se for string, corrigir padding e decodificar base64
                    elif isinstance(resultado_base64, str):
                        resultado_base64 = corrigir_padding_base64(resultado_base64)
                        with open(f"{pasta_salvamento}/{nome_arquivo_zip}", 'wb') as arquivo_zip:
                            arquivo_zip.write(base64.b64decode(resultado_base64))

                    else:
                        logger.error(f"Tipo inesperado de retorno: {type(resultado_base64)}")
                else:
                    logger.info(f"Falha na obtencao de dados para o ID {id_lattes}")

            logger.info("Arquivos Baixados com sucesso!!!")
        except Exception as e:
            logger.error(f"[X] Erro ao tentar baixar dados de docentes: {str(e)}")
            raise ValueError(f"[X] Erro ao tentar baixar dados de docentes: {str(e)}")

    def baixar_dados_grupo(self, ids, pasta_salvamento):
        url_servico = "http://servicosweb.cnpq.br/wsgruposv3/WSGrupoSoapHttpPort?wsdl"

        cliente = Client(url_servico)

        for id in ids:
            r = cliente.service.getXMLGrupo(id, 'Atual')

            if r:
                # nome do arquivo pra salvar o ZIP
                nome_arquivo_zip = str(id) + ".zip"

                with open(f"{pasta_salvamento}/{nome_arquivo_zip}", 'wb') as arquivo_zip:
                    arquivo_zip.write(r['zipXMLs'])

                logger.info(f"Resultado ZIP salvo em {nome_arquivo_zip}")
            else:
                logger.error(f"Falha na obtenção de dados para o ID {id}")

    def gerar_lista(self, caminho_arquivo: str):

        lista_ids = []  # lista onde serão armazenados todos os ids

        dict_planilha = pd.read_excel(caminho_arquivo,
                                      sheet_name=None)  # retorna um dicionário de DataFrames, cada um respectivo a uma folha do arquivo

        for key in dict_planilha.keys():  # percorre as chaves do dicionário

            df = dict_planilha.get(key)  # pega o dataframe associado a key (neste caso, a key é a área)
            possui_id = False  # verifica se existe coluna de ids

            # identifiquei na planilha a coluna de id com dois nomes diferentes: 'Id Lattes' e 'id Lattes'. Abaixo, verifica-se a existência da coluna para ambos os nomes

            if 'Id Lattes' in df.columns:

                ids_df = df['Id Lattes']
                possui_id = True

            elif 'id Lattes' in df.columns:

                ids_df = df['id Lattes']
                possui_id = True

            if possui_id == True:  # algumas áreas na planilha estão sem o id associado ao docente!

                for id_df in ids_df:
                    lista_ids.append(id_df)  # adiciona o id do docente a lista geral de ids

        return lista_ids

    def gerar_dicionario(self, arquivo_base: bytes):

        dict_planilha = pd.read_excel(arquivo_base,
                                      sheet_name=None)  # retorna um dicionário de DataFrames, cada um respectivo a uma folha do arquivo

        for key in dict_planilha.keys():

            lista_ids_area = []  # lista onde serão armazenados os da área ids
            df = dict_planilha.get(key)
            possui_id = False

            id_column_names = ('id Lattes', 'id lattes')  # tratar nomes da coluna id

            for id_column_name in id_column_names:
                if id_column_name in df.columns:
                    df.rename(columns={id_column_name: 'Id Lattes'}, inplace=True)
                    break

            if 'Id Lattes' in df.columns:
                df['Id Lattes'] = df['Id Lattes'].astype(str).str.zfill(16)
                ids_df = df['Id Lattes']
                possui_id = True

            if possui_id == True:
                for id_df in ids_df:
                    lista_ids_area.append(id_df)

                dict_planilha.update({key: lista_ids_area})  # atualiza os valores dos dicionários para listas de ids

            else:
                dict_planilha.update({
                                         key: []})  # se a área não possuir os ids associados aos docentes, atualiza-se o dicionário com a seguinte mensagem

        logger.info(f"[.] Dados recebidos da planilha: {dict_planilha}")
        return dict_planilha

    def extrair_dict_grupo(self, xml, id_grupo):

        ids_pesquisadores = []
        xml_grupo = ET.parse(xml)
        raiz_xml = xml_grupo.getroot()

        for pesquisador in raiz_xml.iter('PESQUISADOR'):
            id = pesquisador.get('NRO-ID-CNPQ')
            ids_pesquisadores.append(id)

        dict_grupo = {id_grupo: ids_pesquisadores}
        return dict_grupo

    def extrair_bolsistas(self, xml):
        xml_grupo = ET.parse(xml)
        raiz_xml = xml_grupo.getroot()

        for pesquisador in raiz_xml.iter('PESQUISADOR'):

            if ((pesquisador.get('BOLSA-CATEGORIA') == 'Produtividade Desen. Tec. e Extensão Inovadora') | (
                    pesquisador.get('BOLSA-CATEGORIA') == 'Produtividade em Pesquisa')):
                self.dicionario_bolsistas.get('ID').append(pesquisador.get('NRO-ID-CNPQ'))
                self.dicionario_bolsistas.get('PESQUISADOR').append(pesquisador.get('NOME-COMPLETO'))
                self.dicionario_bolsistas.get('CATEGORIA_BOLSA').append(pesquisador.get('BOLSA-CATEGORIA'))

    def leitor_dos_resultados(self):
        faltantes = []
        ids_totais = []

        if not (os.path.exists(PASTA_PROGRAMAS)):
            os.makedirs(PASTA_PROGRAMAS)

        for area, ids in self.dict_ids.items():
            path_programa = f'./{PASTA_PROGRAMAS}/{area}'

            if not (os.path.exists(path_programa)):
                os.makedirs(path_programa)

            logger.info(f"[.] Baixando curriculos de {len(ids)} pesquisadores")

            self.baixar_dados_docentes(ids, PASTA_EXTRATOR)
            self.arquivos_extrator = os.listdir(PASTA_EXTRATOR)

            if len(ids) != 0:
                logger.info("[.] Curriculos baixados, inserindo na pasta temporaria...")
                for id in ids:
                    ids_totais.append(id)
                    nome_zip = f'{id}.zip'
                    if os.path.exists(PASTA_EXTRATOR):
                        if nome_zip in self.arquivos_extrator:
                            # Extrair o arquivo ZIP
                            caminho_arquivo_zip = f'{PASTA_EXTRATOR}/{nome_zip}'

                            try:
                                with zipfile.ZipFile(caminho_arquivo_zip, 'r') as zip_ref:
                                    zip_ref.extractall(path_programa)

                            except Exception as e:
                                logger.error(f"Ocorreu um erro durante a extração do arquivo ZIP: {str(e)}")
                        else:
                            faltantes.append(nome_zip.split('.')[0])

                logger.info(f'[.] Arquivos na pasta: {os.listdir(path_programa)}')
        
        if os.path.exists(PASTA_EXTRATOR):
            if os.path.isdir(PASTA_EXTRATOR):
                shutil.rmtree(PASTA_EXTRATOR)  # Remove o diretório e seu conteúdo
            else:
                os.remove(PASTA_EXTRATOR)  # Remove o arquivo
        
        erros_extracao = []  # Criando uma lista de erros de extração, mesmo que esteja vazia para evitor erros
        return faltantes, erros_extracao
        
        
    def extrair_zip_grupos(self):
        xmls_grupos = []
        zips_grupos = []
        dict_grupos = {}
        faltantes = []

        if os.path.exists(PASTA_XMLS_GRUPOS) == False:
            os.makedirs(PASTA_XMLS_GRUPOS)

        if os.path.exists(PASTA_GRUPOS_DIRETORIO_ATUAL) == False:
            os.makedirs(PASTA_GRUPOS_DIRETORIO_ATUAL)

        if os.path.exists(PASTA_EXTRATOR_GRUPOS):
            zips_grupos = os.listdir(PASTA_EXTRATOR_GRUPOS)

            for zip in zips_grupos:
                caminho_arquivo_zip = f'{PASTA_EXTRATOR_GRUPOS}/{zip}'
                zip_desejado = f"GRU_{zip.split('.')[0]}_ATUAL_ESTENDIDO.xml"

                try:

                    with zipfile.ZipFile(caminho_arquivo_zip, 'r') as zip_ref:

                        if zip_desejado in zip_ref.namelist():
                            zip_ref.extract(member=zip_desejado, path=PASTA_XMLS_GRUPOS)

                except Exception as e:
                    print(f"Ocorreu um erro durante a extração do arquivo ZIP: {str(e)}")

        xmls_grupos = os.listdir(PASTA_XMLS_GRUPOS)

        if len(xmls_grupos) != 0:
            for xml in xmls_grupos:
                caminho_xml_grupo = f'{PASTA_XMLS_GRUPOS}/{xml}'
                id_grupo_xml = xml.split('_')[1]
                dict_grupos.update(self.extrair_dict_grupo(caminho_xml_grupo, id_grupo_xml))
                self.extrair_bolsistas(caminho_xml_grupo)

        if len(dict_grupos.keys()) != 0:
            for id_grupo, pesquisadores in dict_grupos.items():

                path_grupo = f'{PASTA_GRUPOS_DIRETORIO_ATUAL}/{id_grupo}'

                if os.path.exists(path_grupo) == False:
                    os.makedirs(path_grupo)

                for pesquisador in pesquisadores:
                    arquivo = f'{pesquisador}.zip'

                    if arquivo in self.arquivos_extrator:
                        # Extrair o arquivo ZIP
                        caminho_arquivo_zip = f'{PASTA_EXTRATOR}/{arquivo}'

                        try:
                            with zipfile.ZipFile(caminho_arquivo_zip, 'r') as zip_ref:
                                zip_ref.extract(member=f'{pesquisador}.xml', path=path_grupo)

                        except Exception as e:
                            print(f"Ocorreu um erro durante a extração do arquivo ZIP: {str(e)}")
                    else:
                        faltantes.append(pesquisador)

    def gerar_planilha(self):

        self.planilha_bolsistas = pd.DataFrame(self.dicionario_bolsistas)
        self.planilha_bolsistas.to_csv('Read_Data/static/PLANILHA_BOLSISTAS.csv')


if __name__ == "__main__":
    armazenador = StorageLattes()
    armazenador.leitor_dos_resultados()
