import os
import pandas as pd
import sys
import shutil
import traceback
import logging

projeto_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(projeto_dir)

from constants import *
from Leitor_xml import Leitor_xml
from Entidades.Pesquisador import Pesquisador

logger = logging.getLogger('dash_app')

class Leitor:

    def __init__(self):
        os.makedirs(PASTA_PROGRAMAS, exist_ok=True)
        download_path = None

    def le_programas(self):
        with open('./programas.txt', 'r') as arquivo:
            programas = arquivo.read()
        PROGRAMAS = programas.split(',')

        # verifica estrutura de pastas
        for programa in PROGRAMAS:
            name_file = os.path.join(PASTA_PROGRAMAS, programa)
            if not os.path.exists(name_file):
                os.makedirs(name_file, exist_ok=True)
                logger.info(f'[.] A pasta {programa} foi criada')
            else:
                logger.info(f'[.] A pasta {programa} existe')

    def read_pesquisador(self, xml, ano_inicio=None, ano_termino=None):
        leitor_xml = Leitor_xml(xml, ano_inicio, ano_termino)
        id = os.path.basename(xml).split('.')[0]

        # eixo Ensino
        nome_e_id_bolsista = leitor_xml.extrair_nome_id_bolsista(id)
        orientacoes_mestrado_concluidas = leitor_xml.extrair_orientacao(
            ORIENTACOES_CONCLUIDAS_PARA_MESTRADO,
            DETALHAMENTO_DE_ORIENTACOES_CONCLUIDAS_PARA_MESTRADO,
            DADOS_BASICOS_DE_ORIENTACOES_CONCLUIDAS_PARA_MESTRADO, True
        )
        orientacoes_mestrado_andamento = leitor_xml.extrair_orientacao(
            ORIENTACOES_EM_ANDAMENTO_MESTRADO,
            DETALHAMENTO_DA_ORIENTACAO_EM_ANDAMENTO_DE_MESTRADO,
            DADOS_BASICOS_DA_ORIENTACAO_EM_ANDAMENTO_DE_MESTRADO, False
        )
        orientacoes_doutorado_concluidas = leitor_xml.extrair_orientacao(
            ORIENTACOES_CONCLUIDAS_PARA_DOUTORADO,
            DETALHAMENTO_DE_ORIENTACOES_CONCLUIDAS_PARA_DOUTORADO,
            DADOS_BASICOS_DE_ORIENTACOES_CONCLUIDAS_PARA_DOUTORADO, True
        )
        orientacoes_doutorado_andamento = leitor_xml.extrair_orientacao(
            ORIENTACOES_EM_ANDAMENTO_DOUTORADO,
            DETALHAMENTO_DA_ORIENTACAO_EM_ANDAMENTO_DE_DOUTORADO,
            DADOS_BASICOS_DA_ORIENTACAO_EM_ANDAMENTO_DE_DOUTORADO, False
        )

        # eixo Pesquisa
        trabalhos_eventos = leitor_xml.extrair_trabalho_completo_evento(
            TRABALHO_EM_EVENTOS, DADOS_BASICOS_DO_TRABALHO, DETALHAMENTO_DO_TRABALHO
        )
        patentes = leitor_xml.extrair_patentes(REGISTRO_OU_PATENTE, None)
        livros_ISBN = leitor_xml.extrair_livro_ISBN(LIVRO_PUBLICADO, DADOS_BASICOS_DO_LIVRO, DETALHAMENTO_DO_LIVRO)
        capitulos_ISBN = leitor_xml.extrair_capitulo_ISBN(
            CAPITULO_DE_LIVRO_PUBLICADO, DADOS_BASICOS_DO_CAPITULO, DETALHAMENTO_DO_CAPITULO
        )
        artigos_publicados = leitor_xml.extrair_artigos(
            ARTIGO_PUBLICADO, DADOS_BASICOS_DO_ARTIGO, DETALHAMENTO_DO_ARTIGO
        )
        orientacoes_ic_concluidas = leitor_xml.extrair_orientacao_ic(
            OUTRAS_ORIENTACOES_CONCLUIDAS, DETALHAMENTO_DE_OUTRAS_ORIENTACOES_CONCLUIDAS, DADOS_BASICOS_DE_OUTRAS_ORIENTACOES_CONCLUIDAS, True
        )
        orientacoes_ic_andamento = leitor_xml.extrair_orientacao_ic(
            IC_ANDAMENTO, DETALHAMENTO_IC_ANDAMENTO, DADOS_IC_ANDAMENTO, False
        )
        orientacoes_tcc_concluidas = leitor_xml.extrair_outras_orientacoes(OUTRAS_ORIENTACOES_CONCLUIDAS,
                                                                           DETALHAMENTO_DE_OUTRAS_ORIENTACOES_CONCLUIDAS,
                                                                           DADOS_BASICOS_DE_OUTRAS_ORIENTACOES_CONCLUIDAS,
                                                                           [NATUREZA_TCC], True)
        orientacoes_tcc_tcr_especializacao_concluidas = leitor_xml.extrair_outras_orientacoes(
            OUTRAS_ORIENTACOES_CONCLUIDAS, DETALHAMENTO_DE_OUTRAS_ORIENTACOES_CONCLUIDAS,
            DADOS_BASICOS_DE_OUTRAS_ORIENTACOES_CONCLUIDAS, [NATUREZA_TCC_TCR_ESPECIALIZACAO], True)

        tecnicos_artisticos_nao_indexados = leitor_xml.extrair_tecnico_artistico(
            ARTIGO_PUBLICADO, DADOS_BASICOS_DO_ARTIGO, DETALHAMENTO_DO_ARTIGO
        )

        # eventos organizados
        eventos_organizados = leitor_xml.extrair_eventos_organizados(
            ORGANIZACAO_DE_EVENTO, DADOS_BASICOS_DA_ORGANIZACAO_DE_EVENTO
        )

        # projetos
        projetos_pesquisa = leitor_xml.extrair_projetos(PROJETO, PROJETO_PESQUISA)
        projetos_desenvolvimento = leitor_xml.extrair_projetos(PROJETO, PROJETO_DESENVOLVIMENTO)

        # registros de software
        softwares = leitor_xml.extrair_softwares(REGISTRO_OU_PATENTE, None)


        historico_itens = []

        def mapear_anos(colecao, nome_metrica):
            for item in colecao:
                # Tenta pegar o ano de diferentes atributos comuns nos seus objetos
                ano = getattr(item, 'ano', getattr(item, 'ano_evento', getattr(item, 'ano_inicio', None)))
                if ano:
                    try:
                        historico_itens.append({'Ano': int(ano), 'Metrica': nome_metrica})
                    except:
                        pass

        # Mapeando as métricas principais para o gráfico geral
        mapear_anos(artigos_publicados, 'PUBLICAÇÕES CIENTÍFICAS')
        mapear_anos(livros_ISBN, 'LIVROS ISBN')
        mapear_anos(capitulos_ISBN, 'CAPÍTULOS ISBN')
        mapear_anos(orientacoes_mestrado_concluidas, 'O.P MESTRADO CONC.')
        mapear_anos(orientacoes_doutorado_concluidas, 'O.P DOUTORADO CONC.')
        mapear_anos(orientacoes_mestrado_andamento, 'O.P MESTRADO AND.')
        mapear_anos(orientacoes_doutorado_andamento,'O.P DOUTORADO AND.')
        mapear_anos(trabalhos_eventos,'EVENTOS')
        mapear_anos(patentes,'PATENTES')
        mapear_anos(orientacoes_ic_concluidas, 'O.P IC CONC.')
        mapear_anos(orientacoes_tcc_concluidas, 'ORIENTAÇÕES CONC. TCC')
        mapear_anos(orientacoes_tcc_tcr_especializacao_concluidas, 'ORIENTAÇÕES CONC. ESPECIALIZAÇÃO')
        mapear_anos(tecnicos_artisticos_nao_indexados, 'PUB. TEC. E ART.')
        mapear_anos(eventos_organizados, 'EVENTOS ORGANIZADOS')
        #
        mapear_anos(projetos_pesquisa, 'PUB. TRAB. EVENTOS')
        mapear_anos(projetos_desenvolvimento,'PUB. TRAB. EVENTOS')
        #
        mapear_anos(softwares,'REGISTROS DE SW')


        # MONTAGEM DO OBJETO PESQUISADOR 
        pesquisador = Pesquisador(
            nome_e_id_bolsista[0], nome_e_id_bolsista[1],
            nome_e_id_bolsista[2], nome_e_id_bolsista[3],
            nome_e_id_bolsista[4]
        )

        pesquisador.orientacoes_mestrado = orientacoes_mestrado_concluidas + orientacoes_mestrado_andamento
        pesquisador.orientacoes_doutorado = orientacoes_doutorado_concluidas + orientacoes_doutorado_andamento
        pesquisador.publicacoes_trabalhos_eventos = trabalhos_eventos
        pesquisador.patentes = patentes
        pesquisador.publicacoes_livros_ISBN = livros_ISBN
        pesquisador.publicacoes_capitulos_ISBN = capitulos_ISBN
        pesquisador.publicacoes_cientificas = artigos_publicados
        pesquisador.orientacoes_ic = orientacoes_ic_concluidas + orientacoes_ic_andamento
        pesquisador.publicacoes_tecnicas_e_artisticas = tecnicos_artisticos_nao_indexados
        pesquisador.eventos_organizados = eventos_organizados
        pesquisador.projetos_pesquisa = projetos_pesquisa
        pesquisador.projetos_desenvolvimento = projetos_desenvolvimento
        pesquisador.softwares = softwares
        pesquisador.orientacoes_tcc = orientacoes_tcc_concluidas
        pesquisador.orientacoes_tcc_tcr_especializacao = orientacoes_tcc_tcr_especializacao_concluidas

        pesquisador.historico_bruto = historico_itens

        return pesquisador

    def listar_arquivos_em_pasta(self, caminho_da_pasta):
        try:
            itens = os.listdir(caminho_da_pasta)
            arquivos_xml = [
                item for item in itens
                if os.path.isfile(os.path.join(caminho_da_pasta, item)) and item.lower().endswith('.xml')
            ]
            return arquivos_xml
        except OSError as e:
            logger.error(f"[X] Ocorreu um erro: {e}")
            return []

    def checa_organizacao_evento(self, pesquisadores):
        eventos_programa = []
        for pesquisador in pesquisadores:
            for evento in pesquisador.eventos_organizados:
                titulo = evento.titulo.lower().strip()
                ano = evento.ano
                eventos_programa.append((titulo, ano))
        return set(eventos_programa)

    def read_pesquisadores_programas(self, programa: str, ano_inicio=None, ano_termino=None):
        pesquisadores = []
        name_file = os.path.join(PASTA_PROGRAMAS, programa)

        if os.path.isdir(name_file):
            arquivos_xml = self.listar_arquivos_em_pasta(name_file)
            logger.info(f"[.] {len(arquivos_xml)} ARQUIVOS LISTADOS NA PASTA {name_file}")

            for arquivo in arquivos_xml:
                xml = os.path.join(name_file, arquivo)
                try:
                    pesquisador = self.read_pesquisador(xml, ano_inicio, ano_termino)
                    pesquisadores.append(pesquisador)
                except Exception as e:
                    logger.error(f'[X] Erro ao ler pesquisador {arquivo}: {str(e)}')
        else:
            logger.warning(f'[X] A pasta do programa não existe: {name_file}')

        return pesquisadores

    def read_pesquisadores_grupos(self, grupo: str):
        pesquisadores = []
        name_file = os.path.join(PASTA_GRUPOS, grupo)

        if os.path.isdir(name_file):
            arquivos_xml = self.listar_arquivos_em_pasta(name_file)
            for arquivo in arquivos_xml:
                pesquisador = self.read_pesquisador(os.path.join(name_file, arquivo))
                pesquisadores.append(pesquisador)
        else:
            logger.warning(f'[X] A pasta do grupo não existe: {name_file}')

        return pesquisadores

    def gerar_estrutura_de_csv_programas(self, ano_inicio=None, ano_termino=None, metricas=None):
        try:
            lista_dfs = []
            programas_totais = []
            programas_totais_eventos = []
            historico_acumulado = []

            if os.path.exists(PASTA_PROGRAMAS):
                programas = os.listdir(PASTA_PROGRAMAS)
            else:
                programas = []

            if not programas:
                logger.error('[X] NÃO EXISTEM PROGRAMAS A PERCORRER')
                return None

            for programa in programas:
                pesquisadores_programa = self.read_pesquisadores_programas(programa, ano_inicio, ano_termino)
                eventos_organizados = self.checa_organizacao_evento(pesquisadores_programa)

                if not pesquisadores_programa:
                    logger.warning(f'[X] Não há pesquisadores no programa {programa}')
                    continue

                # dados individuais
                dados_pesquisadores = [p.series_eixo_ensino() for p in pesquisadores_programa]
                df = pd.DataFrame(dados_pesquisadores)
                df = df.loc[:, ~df.columns.duplicated()]

                for p in pesquisadores_programa:
                    if hasattr(p, 'historico_bruto'):
                        for item in p.historico_bruto:
                            item_com_programa = item.copy() if isinstance(item, dict) else item
                            if isinstance(item_com_programa, dict):
                                item_com_programa['Grupo'] = programa
                            historico_acumulado.append(item_com_programa)

                linha_programa_full = {col: df[col].sum() for col in df.columns if df[col].dtype in [int, float]}
                if metricas:
                    cols_totais = list(metricas)
                    if 'PUBLICAÇÕES CIENTÍFICAS' in metricas:
                        cols_totais += LISTA_QUALIS
                    linha_programa = {c: linha_programa_full.get(c, 0) for c in cols_totais}
                else:
                    linha_programa = linha_programa_full.copy()

                linha_programa['Nome'] = programa
                linha_programa['ID LATTES'] = 'Não possui'
                df_totais = pd.DataFrame([linha_programa])

                df_concat = pd.concat([df, df_totais], ignore_index=True)
                df_concat = df_concat.loc[:, ~df_concat.columns.duplicated()]

                # aplica filtro de métricas nos dados individuais (colunas mostradas por programa)
                if metricas:
                    cols = ['Nome', 'ID LATTES'] + metricas
                    if 'PUBLICAÇÕES CIENTÍFICAS' in metricas:
                        cols += LISTA_QUALIS
                    df_concat = df_concat.loc[:, [c for c in cols if c in df_concat.columns]]

                lista_dfs.append([programa, df_concat])

                # totais gerais (linha já construída respeitando metricas quando fornecidas)
                programas_totais.append(linha_programa)
                programas_totais_eventos.append({'Nome': programa, 'Quantidade de Eventos': len(eventos_organizados)})

            # aba total
            df_total = pd.DataFrame(programas_totais)

            # linha de soma (total geral)
            linha_soma = df_total.drop(columns=['Nome', 'ID LATTES'], errors='ignore').sum(numeric_only=True)
            linha_soma['Nome'] = 'Total Geral'
            linha_soma['ID LATTES'] = 'Não possui'

            # concatena df_total com a linha de soma **no final**
            df_total = pd.concat([df_total, pd.DataFrame([linha_soma])], ignore_index=True)

            # força a ordem das colunas: Nome e ID LATTES primeiro
            colunas = ['Nome', 'ID LATTES'] + [c for c in df_total.columns if c not in ['Nome', 'ID LATTES']]
            df_total = df_total[colunas]

            lista_dfs.append(['total', df_total])

            dict_retorno = {df[0]: df[1].to_json(orient='split') for df in lista_dfs}

            # se temos histórico acumulado, transforma e adiciona ao dicionário de retorno
            df_historico_geral = pd.DataFrame(historico_acumulado)
            if not df_historico_geral.empty:
                # Normaliza e canonicaliza nomes de métricas para evitar discrepâncias (ex.: espaços, maiúsculas diferentes, variantes)
                df_historico_geral['Metrica'] = df_historico_geral['Metrica'].astype(str).str.strip()
                # Mapa de canonicalização (chave: upper stripped) -> valor padronizado
                canonical_map = {
        'PUBLICAÇÃO DE LIVROS COM ISBN': 'LIVROS ISBN',
        'PUBLICAÇÃO DE CAPÍTULOS COM ISBN': 'CAPÍTULOS ISBN',
        'PUBLICAÇÃO TÉCNICA OU ARTÍSTICA': 'PUB. TEC. E ART.',
        'PUBLICAÇÃO DE TRABALHO EM EVENTOS': 'PUB. TRAB. EVENTOS',
        'EVENTOS ORGANIZADOS': 'EVENTOS ORGANIZADOS',
        'ANO DE TITULAÇÃO': 'ANO TITULACAO',
        'PUBLICAÇÕES CIENTÍFICAS': 'PUBLICAÇÕES CIENTÍFICAS',
        'ORIENTAÇÕES CONCLUÍDAS DE TCC NA UPE': 'ORIENTAÇÕES CONC. TCC',
        'ORIENTAÇÃO DE TCC/TCR DE APERFEIÇOAMENTO/ESPECIALIZAÇÃO NA UPE':'ORIENTAÇÕES CONC. ESPECIALIZAÇÃO',
        'ORIENTAÇÃO PRINCIPAL DE MESTRADO CONCLUÍDA': 'O.P MESTRADO CONC.',
        'ORIENTAÇÃO PRINCIPAL DE DOUTORADO CONCLUÍDA': 'O.P DOUTORADO CONC.',
        'CO-ORIENTAÇÃO DE MESTRADO CONCLUÍDA': 'C.O MESTRADO CONC.',
        'CO-ORIENTAÇÃO DE DOUTORADO CONCLUÍDA': 'C.O DOUTORADO CONC.',
        'ORIENTAÇÃO PRINCIPAL DE MESTRADO EM ANDAMENTO': 'O.P MESTRADO AND.',
        'ORIENTAÇÃO PRINCIPAL DE DOUTORADO EM ANDAMENTO':'O.P DOUTORADO AND.',
        'CO-ORIENTAÇÃO DE MESTRADO EM ANDAMENTO': 'C.O MESTRADO AND.',
        'CO-ORIENTAÇÃO DE DOUTORADO EM ANDAMENTO': 'C.O DOUTORADO AND.',
        'ORIENTAÇÃO DE INICIAÇÃO CIENTÍFICA': 'ORIENTAÇÕES I.C',
        'DEPÓSITO OU REGISTRO DE PATENTES': 'PATENTES',
        'REGISTROS DE SOFTWARE': 'REGISTROS DE SW'
        }
                df_historico_geral['Metrica_upper'] = df_historico_geral['Metrica'].str.upper().str.replace('\u00ad','')
                df_historico_geral['Metrica'] = df_historico_geral['Metrica_upper'].map(lambda x: canonical_map.get(x, x))
                df_historico_geral = df_historico_geral.drop(columns=['Metrica_upper'])

                df_historico_geral = df_historico_geral.groupby(['Ano', 'Metrica', 'Grupo'], dropna=False).size().reset_index(name='Quantidade')
                dict_retorno['historico_geral'] = df_historico_geral.to_json(orient='split')

            # limpa pasta programas
            if os.path.exists(PASTA_PROGRAMAS):
                shutil.rmtree(PASTA_PROGRAMAS)

            return dict_retorno

        except Exception as e:
            exc_type, exc_value, exc_tb = sys.exc_info()
            logger.error(f"[X] ERRO AO GERAR ESTRUTURA DE PLANILHA: {traceback.format_exception(exc_type, exc_value, exc_tb)}")
            return None

    def gerar_estrutura_de_csv_grupos(self, ano_inicio=None, ano_termino=None):
        df_grupo = pd.read_excel('./Read_Data/id_nome_grupo.xlsx')
        grupos_totais = []
        grupos_totais_eventos = []
        historico_acumulado = []

        if not os.path.exists(PASTA_DADOS_SALVOS_GRUPOS):
            os.makedirs(PASTA_DADOS_SALVOS_GRUPOS)

        grupos = os.listdir(PASTA_GRUPOS) if os.path.exists(PASTA_GRUPOS) else []

        if not grupos:
            logger.error('NÃO EXISTEM GRUPOS A PERCORRER')
            return None

        for grupo in grupos:
            nome_grupo = df_grupo.loc[df_grupo["id"] == int(grupo), "nome"].unique()[0]
            # obtém a lista de objetos Pesquisador
            pesquisadores_grupo = self.read_pesquisadores_grupos(grupo)
            eventos_organizados = self.checa_organizacao_evento(pesquisadores_grupo)

            if not pesquisadores_grupo:
                logger.warning(f'[X] Não há pesquisadores no grupo {nome_grupo} de id {grupo}')
                continue

            for p in pesquisadores_grupo:
                if hasattr(p, 'historico_bruto'):
                    for item in p.historico_bruto:
                        item_com_grupo = item.copy() if isinstance(item, dict) else item
                        if isinstance(item_com_grupo, dict):
                            item_com_grupo['Grupo'] = nome_grupo
                        historico_acumulado.append(item_com_grupo)

            dados_pesquisadores = [p.series_eixo_ensino() for p in pesquisadores_grupo]
            df = pd.DataFrame(dados_pesquisadores)
            df = df.loc[:, ~df.columns.duplicated()]

            linha_grupo = {col: df[col].sum() for col in df.columns if df[col].dtype in [int, float]}
            linha_grupo['Nome'] = nome_grupo
            linha_grupo['ID LATTES'] = grupo

            # Salva o Excel individual do grupo 
            df_totais = pd.DataFrame([linha_grupo])
            df_concat = pd.concat([df, df_totais], ignore_index=True)
            diretorio = os.path.join(PASTA_DADOS_SALVOS_GRUPOS, grupo)
            os.makedirs(diretorio, exist_ok=True)
            df_concat.to_excel(os.path.join(diretorio, f'{grupo}.xlsx'))

            grupos_totais.append(linha_grupo)
            grupos_totais_eventos.append({'Nome': nome_grupo, 'Quantidade de eventos': len(eventos_organizados)})

        df_total = pd.DataFrame(grupos_totais)
        linha_soma = df_total.drop(columns=['Nome', 'ID LATTES'], errors='ignore').sum(numeric_only=True)
        linha_soma['Nome'] = 'Total Geral'
        linha_soma['ID LATTES'] = 'Não possui'
        df_total = pd.concat([pd.DataFrame([linha_soma]), df_total], ignore_index=True)
        df_total.to_excel(os.path.join(PASTA_DADOS_SALVOS_GRUPOS, 'total_grupos.xlsx'))

        df_historico_geral = pd.DataFrame(historico_acumulado)

        # Criação do dicionário de retorno que será usado pelo Dash (store-lista-dfs)
        resultado_dash = {
            'total': df_total.to_json(orient='split'),
            'eventos': pd.DataFrame(grupos_totais_eventos).to_json(orient='split')
        }

        if not df_historico_geral.empty:
            # Normaliza e canonicaliza os nomes de métrica antes de agrupar
            df_historico_geral['Metrica'] = df_historico_geral['Metrica'].astype(str).str.strip()
            canonical_map = {
        'ORIENTAÇÃO PRINCIPAL DE MESTRADO CONCLUÍDA': 'O.P MESTRADO CONC.',
        'ORIENTAÇÃO PRINCIPAL DE DOUTORADO CONCLUÍDA': 'O.P DOUTORADO CONC.',
        'CO-ORIENTAÇÃO DE MESTRADO CONCLUÍDA': 'C.O MESTRADO CONC.',
        'CO-ORIENTAÇÃO DE DOUTORADO CONCLUÍDA': 'C.O DOUTORADO CONC.',
        'ORIENTAÇÃO PRINCIPAL DE MESTRADO EM ANDAMENTO': 'O.P MESTRADO AND.',
        'ORIENTAÇÃO PRINCIPAL DE DOUTORADO EM ANDAMENTO':'O.P DOUTORADO AND.',
        'CO-ORIENTAÇÃO DE MESTRADO EM ANDAMENTO': 'C.O MESTRADO AND.',
        'CO-ORIENTAÇÃO DE DOUTORADO EM ANDAMENTO': 'C.O DOUTORADO AND.',
        'ORIENTAÇÃO DE INICIAÇÃO CIENTÍFICA': 'ORIENTAÇÕES I.C',
        'DEPÓSITO OU REGISTRO DE PATENTES': 'PATENTES',
        'REGISTROS DE SOFTWARE': 'REGISTROS DE SW',
        'PUBLICAÇÃO DE LIVROS COM ISBN': 'LIVROS ISBN',
        'PUBLICAÇÃO DE CAPÍTULOS COM ISBN': 'CAPÍTULOS ISBN',
        'PUBLICAÇÃO TÉCNICA OU ARTÍSTICA': 'PUB. TEC. E ART.',
        'PUBLICAÇÃO DE TRABALHO EM EVENTOS': 'PUB. TRAB. EVENTOS',
        'EVENTOS ORGANIZADOS': 'EVENTOS ORGANIZADOS',
        'ANO DE TITULAÇÃO': 'ANO_TITULACAO',
        'PUBLICAÇÕES CIENTÍFICAS': 'PUBLICAÇÕES CIENTÍFICAS',
        'ORIENTAÇÕES CONCLUÍDAS DE TCC NA UPE': 'ORIENTAÇÕES CONC. TCC',
        'ORIENTAÇÃO DE TCC/TCR DE APERFEIÇOAMENTO/ESPECIALIZAÇÃO NA UPE':'ORIENTAÇÕES CONC. ESPECIALIZAÇÃO'
        }
            df_historico_geral['Metrica_upper'] = df_historico_geral['Metrica'].str.upper().str.replace('\u00ad','')
            df_historico_geral['Metrica'] = df_historico_geral['Metrica_upper'].map(lambda x: canonical_map.get(x, x))
            df_historico_geral = df_historico_geral.drop(columns=['Metrica_upper'])

            # Agrupa por Ano, Métrica e Grupo para somar as quantidades
            df_historico_geral = df_historico_geral.groupby(['Ano', 'Metrica', 'Grupo'], dropna=False).size().reset_index(name='Quantidade')

            df_historico_geral.to_excel(os.path.join(PASTA_DADOS_SALVOS_GRUPOS, 'historico_geral_anos.xlsx'))

            # Adiciona a chave 'historico_geral' que o visualizacoes.py vai ler
            resultado_dash['historico_geral'] = df_historico_geral.to_json(orient='split')

        return resultado_dash
