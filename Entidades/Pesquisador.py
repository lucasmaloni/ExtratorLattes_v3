import pandas as pd
from Filtros.constantes_filtros import *


class Pesquisador:

    def __init__(self, nome, id, bolsista, categoria_bolsa, ano_titulacao_doutorado):

        self.nome = nome
        self.id = id
        self.bolsista = bolsista
        self.ano_titulacao_doutorado = ano_titulacao_doutorado
        self.categoria_bolsa = categoria_bolsa
        self.quantidades_orientacao_mestrado = dict()
        self.quantidades_orientacao_doutorado = dict()
        self.orientacoes_mestrado = []
        self.orientacoes_doutorado = []
        self.orientacoes_ic = []
        self.patentes = []
        self.publicacoes_cientificas = []
        self.publicacoes_livros_ISBN = []
        self.publicacoes_capitulos_ISBN = []
        self.publicacoes_tecnicas_e_artisticas = []
        self.publicacoes_trabalhos_eventos = []
        self.eventos_organizados = []
        self.projetos_pesquisa = []
        self.projetos_desenvolvimento = []
        self.softwares = []
        self.orientacoes_tcc = []
        self.orientacoes_tcc_tcr_especializacao = []

    def update_quantidades_orientacao(self, tipo: str):

        orientador_principal_em_andamento = list()
        orientador_principal_concluido = list()
        co_orientador_concluido = list()
        co_orientador_em_andamento = list()

        if tipo == 'mestrado':

            for orientacao_mestrado in self.orientacoes_mestrado:

                if orientacao_mestrado.natureza == DESCRICAO_MESTRADO:

                    if orientacao_mestrado.tipo_orientacao == ORIENTADOR_PRINCIPAL:
                        if orientacao_mestrado.concluido == True:
                            orientador_principal_concluido.append(orientacao_mestrado)
                        else:
                            orientador_principal_em_andamento.append(orientacao_mestrado)

                    elif orientacao_mestrado.tipo_orientacao == CO_ORIENTADOR:
                        if orientacao_mestrado.concluido == True:
                            co_orientador_concluido.append(orientacao_mestrado)
                        else:
                            co_orientador_em_andamento.append(orientacao_mestrado)

            self.quantidades_orientacao_mestrado = {
                "O.P MESTRADO CONC.": orientador_principal_concluido,
                "O.P MESTRADO AND.": orientador_principal_em_andamento,
                "C.O MESTRADO CONC.": co_orientador_concluido,
                "C.O MESTRADO AND.": co_orientador_em_andamento
            }

        elif tipo == 'doutorado':

            for orientacao_doutorado in self.orientacoes_doutorado:

                if orientacao_doutorado.natureza == DESCRICAO_DOUTORADO:
                    if orientacao_doutorado.tipo_orientacao == ORIENTADOR_PRINCIPAL:
                        if orientacao_doutorado.concluido == True:
                            orientador_principal_concluido.append(orientacao_doutorado)
                        else:
                            orientador_principal_em_andamento.append(orientacao_doutorado)

                    elif orientacao_doutorado.tipo_orientacao == CO_ORIENTADOR:
                        if orientacao_doutorado.concluido == True:
                            co_orientador_concluido.append(orientacao_doutorado)
                        else:
                            co_orientador_em_andamento.append(orientacao_doutorado)

            self.quantidades_orientacao_doutorado = {
                "O.P DOUTORADO CONC.": orientador_principal_concluido,
                "O.P DOUTORADO AND.": orientador_principal_em_andamento,
                "C.O DOUTORADO CONC.": co_orientador_concluido,
                "C.O DOUTORADO AND.": co_orientador_em_andamento,
            }

    def pontuacao_bolsista(self):

        if self.bolsista:

            return PONTUACAO_BOLSISTA

        else:

            return 0

    def pontuacao_mestrado(self):

        p_mestrado = 0

        if len(self.orientacoes_mestrado) == 0:
            return 0

        else:
            for orientacao_mestrado in self.orientacoes_mestrado:
                p_mestrado += orientacao_mestrado.peso

            return p_mestrado

    def pontuacao_doutorado(self):

        p_doutorado = 0

        if len(self.orientacoes_doutorado) == 0:
            return 0

        else:
            for orientacao_doutorado in self.orientacoes_doutorado:
                p_doutorado += orientacao_doutorado.peso

            return p_doutorado

    def pontuacao_ic(self):

        p_ic = 0

        if len(self.orientacoes_ic) == 0:
            return 0

        else:
            for orientacao_ic in self.orientacoes_ic:
                p_ic += orientacao_ic.peso

            return p_ic

    def pontuacao_patentes(self):

        p_patentes = 0

        if len(self.patentes) == 0:
            return 0

        else:
            for patente in self.patentes:
                p_patentes += patente.peso

            return p_patentes
    def pontuacao_softwares(self):

        p_softwares = 0

        if len(self.softwares) == 0:
            return 0

        else:
            for software in self.softwares:
                p_softwares += software.peso

            return p_softwares

    def pontuacao_pub_cientificas(self):

        p_pub_cientificas = 0

        if len(self.publicacoes_cientificas) == 0:
            return 0

        else:
            for publicacao_cientifica in self.publicacoes_cientificas:
                p_pub_cientificas += publicacao_cientifica.peso

            return p_pub_cientificas

    def pontuacao_pub_livros(self):

        p_pub_livros_ISBN = 0

        if len(self.publicacoes_livros_ISBN) == 0:
            return 0

        else:
            for publicacao_livro_ISBN in self.publicacoes_livros_ISBN:
                p_pub_livros_ISBN += publicacao_livro_ISBN.peso

            return p_pub_livros_ISBN

    def pontuacao_pub_capitulos(self):

        p_pub_capitulos_ISBN = 0

        if len(self.publicacoes_capitulos_ISBN) == 0:
            return 0

        else:
            for publicacao_capitulo_ISBN in self.publicacoes_capitulos_ISBN:
                p_pub_capitulos_ISBN += publicacao_capitulo_ISBN.peso

            return p_pub_capitulos_ISBN

    def pontuacao_pub_tecnicas_artisticas(self):

        p_pub_tecnicas_artisticas = 0

        if len(self.publicacoes_tecnicas_e_artisticas) == 0:
            return 0

        else:
            for publicacao_tecnica_artistica in self.publicacoes_tecnicas_e_artisticas:
                p_pub_tecnicas_artisticas += publicacao_tecnica_artistica.peso

            return p_pub_tecnicas_artisticas

    def pontuacao_trabalhos_eventos(self):

        p_trabalhos_eventos = 0

        if len(self.publicacoes_trabalhos_eventos) == 0:
            return 0

        else:
            for publicacao_trabalho_evento in self.publicacoes_trabalhos_eventos:
                p_trabalhos_eventos += publicacao_trabalho_evento.peso

            return p_trabalhos_eventos

    def pontuacao_total_ensino(self):

        pontuacao_total_ensino = 0

        pontuacao_total_ensino += self.pontuacao_mestrado()
        pontuacao_total_ensino += self.pontuacao_doutorado()

        return pontuacao_total_ensino

    def pontuacao_total_pesquisa(self):

        pontuacao_total_pesquisa = 0

        pontuacao_total_pesquisa += self.pontuacao_ic()
        pontuacao_total_pesquisa += self.pontuacao_patentes()
        pontuacao_total_pesquisa += self.pontuacao_pub_cientificas()
        pontuacao_total_pesquisa += self.pontuacao_pub_livros()
        pontuacao_total_pesquisa += self.pontuacao_pub_capitulos()
        pontuacao_total_pesquisa += self.pontuacao_pub_tecnicas_artisticas()
        pontuacao_total_pesquisa += self.pontuacao_trabalhos_eventos()
        pontuacao_total_pesquisa += self.pontuacao_bolsista()

        return pontuacao_total_pesquisa

    def pontuacao_total(self):

        pontuacao_total = 0

        pontuacao_total = self.pontuacao_total_pesquisa() + self.pontuacao_total_ensino()

        return pontuacao_total

    def series_eixo_ensino(self):

        self.update_quantidades_orientacao('mestrado')
        self.update_quantidades_orientacao('doutorado')

        series = pd.Series(dtype='object')

        dict_qualis = {'A1': 0, 'A2': 0, 'A3': 0, 'A4': 0, 'B1': 0, 'B2': 0, 'B3': 0, 'B4': 0, 'B5': 0, 'C': 0}

        series = {
            "Nome": self.nome,
            "ID LATTES": str(self.id),
            "O.P MESTRADO CONC.": len(self.quantidades_orientacao_mestrado["O.P MESTRADO CONC."]),
            "O.P MESTRADO AND.": len(self.quantidades_orientacao_mestrado["O.P MESTRADO AND."]),
            "C.O MESTRADO CONC.": len(self.quantidades_orientacao_mestrado["C.O MESTRADO CONC."]),
            "C.O MESTRADO AND.": len(self.quantidades_orientacao_mestrado["C.O MESTRADO AND."]),
            "O.P DOUTORADO CONC.": len(self.quantidades_orientacao_doutorado["O.P DOUTORADO CONC."]),
            "O.P DOUTORADO AND.": len(self.quantidades_orientacao_doutorado["O.P DOUTORADO AND."]),
            "C.O DOUTORADO CONC.": len(self.quantidades_orientacao_doutorado["C.O DOUTORADO CONC."]),
            "C.O DOUTORADO AND.": len(self.quantidades_orientacao_doutorado["C.O DOUTORADO AND."]),
            "ORIENTAÇÕES I.C": len(self.orientacoes_ic),
            "ORIENTAÇÕES CONC. TCC": len(self.orientacoes_tcc),
            "ORIENTAÇÕES CONC. ESPECIALIZAÇÃO": len(self.orientacoes_tcc_tcr_especializacao),
            "PATENTES": len(self.patentes),
            "REGISTROS DE SW": len(self.softwares),
            "LIVROS ISBN": len(self.publicacoes_livros_ISBN),
            "CAPÍTULOS ISBN": len(self.publicacoes_capitulos_ISBN),
            "PUB. TEC. E ART.": len(self.publicacoes_tecnicas_e_artisticas),
            "PUB. TRAB. EVENTOS": len(self.publicacoes_trabalhos_eventos),
            "EVENTOS ORGANIZADOS": len(self.eventos_organizados),
            # "BOLSISTA": self.bolsista,
            'ANO_TITULACAO': self.ano_titulacao_doutorado,
            "PUBLICAÇÕES CIENTÍFICAS": len(self.publicacoes_cientificas),
        }

        for publicacao in self.publicacoes_cientificas:
            for key, element in dict_qualis.items():
                if key == publicacao.qualis:
                    element += 1
                    dict_qualis[key] = element

        series.update(dict_qualis)

        return series
