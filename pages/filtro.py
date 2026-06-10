import json

from dash import html, dcc, Input, Output, State, callback, no_update
import dash
from io import BytesIO, StringIO
import pandas as pd
import logging
from datetime import datetime
import traceback
import base64

from dash.exceptions import PreventUpdate

from Read_Data.Armazenar_dados_lattes import StorageLattes
from Read_Data.Leitor import Leitor
# Certificar que METRICAS_DASH contém as strings de métricas Leitor espera
# Assumimos que as constantes de pastas estão definidas em Read_Data.constants
from Read_Data.constants import PASTA_PROGRAMAS, PASTA_PROGRAMAS_DIRETORIO_ATUAL, PASTA_GRUPOS, \
    PASTA_GRUPOS_DIRETORIO_ATUAL, PASTA_EXTRATOR_GRUPOS

logger = logging.getLogger('dash_app')

dash.register_page(__name__, path='/filtros', name='Filtros')

layout = html.Div([

    html.Div([
        html.Div([
            html.Span("Extrator", style={'color': 'red', 'fontWeight': 'bold'}),
            html.Span("Lattes", style={'color': 'white', 'fontWeight': 'bold'})
        ], style={'display': 'inline-block', 'width': '50%', 'textAlign': 'left', 'padding': '20px', 'fontSize': '190%',
                  'fontFamily': 'Arial'}),

        html.Div([
            html.Img(src='/assets/upe_logo_site.png', style={'width': '12%'})
        ], style={'display': 'inline-block', 'width': '50%', 'textAlign': 'right', 'padding': '10px'})
    ], style={'backgroundColor': '#001F3F', 'padding': '10px', 'display': 'flex'}),

    html.Div([
        html.Div(id='uploaded-file-display-status', style={'display': 'none'}),
        html.Div(id='feedback-message', style={'display': 'none'}),

        html.Div([
            html.Div([
                html.Div([
                    html.H4("Orientação", style={'marginBottom': '10px'}),
                    html.P("Tipo:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        options=[
                            {'label': 'Co-orientação', 'value': 'coorientacao'},
                            {'label': 'Orientação', 'value': 'orientacao'},
                        ],
                        id='filtro-orientacao-1',
                        inline=False,
                        inputStyle={"margin-right": "10px"},
                    ),
                    html.Br(),
                    html.P("Status:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        options=[
                            {'label': 'Concluído', 'value': 'concluido'},
                            {'label': 'Andamento', 'value': 'andamento'},
                        ],
                        id='filtro-orientacao-2',
                        inline=False,
                        inputStyle={"margin-right": "10px"},
                    ),
                    html.Br(),
                    html.P("Nível:", style={'fontWeight': 'bold'}),
                    dcc.Checklist(
                        options=[
                            {'label': 'Mestrado', 'value': 'mestrado'},
                            {'label': 'Doutorado', 'value': 'doutorado'},
                            {'label': 'IC', 'value': 'ic'},
                            {'label': 'TCC concluída', 'value': 'tcc-conc'},
                            {'label': 'Especialização concluída', 'value': 'conc-esp'},
                        ],
                        id='filtro-orientacao-3',
                        inline=False,
                        inputStyle={"margin-right": "10px"},
                    )
                ], style={
                    'backgroundColor': '#D9D9D9',
                    'padding': '15px',
                    'border': '1px solid black',
                    'borderRadius': '5px'
                }),
            ], style={'width': '30%'}),

            html.Div([
                html.Div([
                    html.H4("Registro"),
                    dcc.Checklist(
                        options=[
                            {'label': 'Patente', 'value': 'patente'},
                            {'label': 'Software', 'value': 'software'},
                        ],
                        id='filtro-registro',
                        inline=False,
                        inputStyle={"margin-right": "10px"},
                        className="checklist-style"
                    )
                ], style={'backgroundColor': '#D9D9D9', 'padding': '10px', 'marginBottom': '10px',
                          'border': '1px solid black', 'borderRadius': '5px'}),

                html.Div([
                    html.H4("Publicações"),
                    dcc.Checklist(
                        options=[
                            {'label': 'De Livros com ISBN', 'value': 'livros'},
                            {'label': 'De Capítulos com ISBN', 'value': 'capitulos'},
                            {'label': 'De Trabalhos em Eventos', 'value': 'eventos'},
                            {'label': 'Em Revistas ou Periódicos', 'value': 'cientificas'},
                        ],
                        id='filtro-publicacoes',
                        inline=False,
                        inputStyle={"margin-right": "10px"},
                        className="checklist-style"
                    )
                ], style={'backgroundColor': '#D9D9D9', 'padding': '10px', 'marginBottom': '10px',
                          'border': '1px solid black', 'borderRadius': '5px'}),

                html.Div([
                    html.H4("Outros"),
                    dcc.Checklist(
                        options=[
                            {'label': 'Eventos Organizados', 'value': 'eventos_organizados'},
                            {'label': 'Produções Técnicas ou Artísticas', 'value': 'tecnica'},
                            {'label': 'Ano de Titulação do Doutorado', 'value': 'ano_de_conclusao'}
                        ],
                        id='filtro-outros',
                        inline=False,
                        inputStyle={"margin-right": "10px"},
                        className="checklist-style"
                    )
                ], style={'backgroundColor': '#D9D9D9', 'padding': '10px', 'border': '1px solid black',
                          'borderRadius': '5px'}),
            ], style={'width': '30%', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'space-between'}),

        ], style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'backgroundColor': '#6EA1C2',
            'padding': '40px',
            'minHeight': 'calc(100vh - 180px)'
        }),

        html.Div([
            html.Div("Ano de inicio:", style={'color': 'white', 'marginRight': '20px'}),
            dcc.Dropdown(
                options=[{'label': int(year), 'value': year} for year in
                         range((int(datetime.now().year) - 10), (int(datetime.now().year) + 1))],
                placeholder="Selecione um ano",
                style={
                    'width': '200px',
                    'marginRight': '20px',
                    'position': 'relative',
                    'zIndex': '1000'
                },
                id='input-ano-inicio'
            ),
            html.Div("Ano de termino:", style={'color': 'white', 'marginRight': '20px'}),
            dcc.Dropdown(
                options=[{'label': int(year), 'value': year} for year in
                         range((int(datetime.now().year) - 10), (int(datetime.now().year) + 1))],
                placeholder="Selecione um ano",
                style={
                    'width': '200px',
                    'marginRight': '20px',
                    'position': 'relative',
                    'zIndex': '1000'
                },
                id='input-ano-termino'
            ),
            html.Button("Marcar Tudo", id="btn-marcar-tudo", style={
                'backgroundColor': '#28a745',
                'color': 'white',
                'padding': '10px 20px',
                'borderRadius': '10px',
                'border': 'none',
                'cursor': 'pointer',
                'fontWeight': 'bold',
                'marginRight': '20px'
            }),
            html.Button("Extrair Informações do Lattes", id='btn-extrair', style={
                'backgroundColor': '#28a745',
                'color': 'white',
                'padding': '10px',
                'borderRadius': '10px',
                'border': 'none',
                'cursor': 'pointer',
                'fontWeight': 'bold'
            })
        ], style={
            'backgroundColor': '#001F3F',
            'padding': '20px',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'
        }),

        dcc.Loading(id='loading-output', type='default', children=html.Div(id='output-message'), fullscreen=True,
                    style={'backgroundColor': 'rgba(0, 0, 0, 0.5)'}),
    ]),
    dcc.Location(id='redirect-div-after-process', refresh=True)
])


@callback(
    Output('output-message', 'children', allow_duplicate=True),
    Output('store-lista-dfs', 'data', allow_duplicate=True),
    Output('error-modal', 'is_open', allow_duplicate=True),
    Output('modal-error-message', 'children', allow_duplicate=True),
    Input('btn-extrair', 'n_clicks'),
    State('store-uploaded-data', 'data'),
    State('input-ano-inicio', 'value'),
    State('input-ano-termino', 'value'),
    State('filtro-orientacao-1', 'value'),
    State('filtro-orientacao-2', 'value'),
    State('filtro-orientacao-3', 'value'),
    State('filtro-registro', 'value'),
    State('filtro-publicacoes', 'value'),
    State('filtro-outros', 'value'),
    prevent_initial_call=True
)
def processar_resultado(n_clicks, uploaded_file_data_dict, ano_inicio, ano_termino,
                        o1, o2, o3, registro, publicacoes, outros):
    logger.info("[.] Processando resultados com base nas seleções da página de filtros")

    if n_clicks is None or n_clicks < 1:
        raise PreventUpdate

    if not uploaded_file_data_dict:
        return "", no_update, True, "Por favor, carregue um arquivo na tela inicial."

    if not ano_inicio or not ano_termino:
        return "", no_update, True, "Por favor, selecione ano de início e término."

    try:
        tipo_extracao = uploaded_file_data_dict.get('tipo', 'programas')
        arquivo_base = uploaded_file_data_dict.get('conteudo_base64')
        if not arquivo_base:
            return no_update, True, "Erro interno: conteúdo do arquivo ausente."

        conteudo_bytes = base64.b64decode(arquivo_base)
        storage_lattes = StorageLattes(arquivo_base=BytesIO(conteudo_bytes))
        storage_lattes.leitor_dos_resultados()

        metricas_para_leitor = []

        if o1 and 'orientacao' in o1:
            if o2 and 'concluido' in o2:
                if o3 and 'mestrado' in o3:
                    metricas_para_leitor.append('O.P MESTRADO CONC.')
                if o3 and 'doutorado' in o3:
                    metricas_para_leitor.append('O.P DOUTORADO CONC.')
                if o3 and 'ic' in o3:
                    metricas_para_leitor.append('ORIENTAÇÕES I.C')
                if o3 and 'tcc-conc' in o3:
                    metricas_para_leitor.append('ORIENTAÇÕES CONC. TCC')
                if o3 and 'conc-esp' in o3:
                    metricas_para_leitor.append('ORIENTAÇÕES CONC. ESPECIALIZAÇÃO')
            if o2 and 'andamento' in o2:
                if o3 and 'mestrado' in o3:
                    metricas_para_leitor.append('O.P MESTRADO AND.')
                if o3 and 'doutorado' in o3:
                    metricas_para_leitor.append('O.P DOUTORADO AND.')

        if o1 and 'coorientacao' in o1:
            if o2 and 'concluido' in o2:
                if o3 and 'mestrado' in o3:
                    metricas_para_leitor.append('C.O MESTRADO CONC.')
                if o3 and 'doutorado' in o3:
                    metricas_para_leitor.append('C.O DOUTORADO CONC.')
            if o2 and 'andamento' in o2:
                if o3 and 'mestrado' in o3:
                    metricas_para_leitor.append('C.O MESTRADO AND.')
                if o3 and 'doutorado' in o3:
                    metricas_para_leitor.append('C.O DOUTORADO AND.')

        if registro:
            if 'patente' in registro:
                metricas_para_leitor.append('PATENTES')
            if 'software' in registro:
                metricas_para_leitor.append('REGISTROS DE SW')

        if publicacoes:
            if 'livros' in publicacoes:
                metricas_para_leitor.append('LIVROS ISBN')
            if 'capitulos' in publicacoes:
                metricas_para_leitor.append('CAPÍTULOS ISBN')
            if 'eventos' in publicacoes:
                metricas_para_leitor.append('PUB. TRAB. EVENTOS')
            if 'cientificas' in publicacoes:
                metricas_para_leitor.append('PUBLICAÇÕES CIENTÍFICAS')

        if outros:
            if 'eventos_organizados' in outros:
                metricas_para_leitor.append('EVENTOS ORGANIZADOS')
            if 'tecnica' in outros:
                metricas_para_leitor.append('PUB. TEC. E ART.')
            if 'ano_de_conclusao' in outros:
                metricas_para_leitor.append('ANO_TITULACAO')

        metricas_para_leitor = list(set(metricas_para_leitor))
        if not metricas_para_leitor:
            return no_update, no_update, True, "Selecione pelo menos uma métrica para continuar."

        logger.info(f"[.] Métricas finais: {metricas_para_leitor}")
        leitor = Leitor()
        lista_dfs = leitor.gerar_estrutura_de_csv_programas(ano_inicio=ano_inicio, ano_termino=ano_termino,
                                    metricas=metricas_para_leitor)
        logger.info(f"Dados para armazenar no store (tipo {type(lista_dfs)}): {lista_dfs}")
        try:
            logger.info(f"Como JSON string? {json.dumps(lista_dfs)[:500]}")  # primeiros 500 chars
        except Exception as e:
            logger.error(f"Erro convertendo dados para JSON: {e}")

        dict_para_store = lista_dfs.copy() if isinstance(lista_dfs, dict) else {}
        dict_para_store['_meta'] = {
            'metricas': metricas_para_leitor,
            'ano_inicio': ano_inicio,
            'ano_termino': ano_termino
        }

        return "", dict_para_store, False, ""

    except Exception as e:
        logger.error(f"[X] Erro ao gerar resultados: {str(e)}\n{traceback.format_exc()}")
        return no_update, no_update, True, f"Erro durante a extração: {e}"

@callback(
    Output('store-lista-dfs', 'data', allow_duplicate=True),
    Input('filtro-orientacao-1', 'value'),
    Input('filtro-orientacao-2', 'value'),
    Input('filtro-orientacao-3', 'value'),
    Input('filtro-registro', 'value'),
    Input('filtro-publicacoes', 'value'),
    Input('filtro-outros', 'value'),
    prevent_initial_call=True
)
def limpar_dados_ao_mudar_filtros(o1, o2, o3, registro, publicacoes, outros):
    return {'_meta': {'metricas': []}}


@callback(
    Output('redirect-div-after-process', 'pathname'),
    Input('store-lista-dfs', 'data'),
    prevent_initial_call=True
)
def redirecionar_apos_processamento(store_data):
    if not store_data:
        raise PreventUpdate

    try:
        # Se for dict, verificar se existe ao menos uma chave além de '_meta'
        if isinstance(store_data, dict):
            other_keys = [k for k in store_data.keys() if k != '_meta']
            for k in other_keys:
                v = store_data.get(k)
                if v:
                    logger.info("Redirecionando automaticamente para /visualizacoes após processamento.")
                    return "/visualizacoes"

            meta = store_data.get('_meta')
            metricas = []
            if isinstance(meta, dict):
                metricas = meta.get('metricas', []) or []
            elif isinstance(meta, str):
                try:
                    import json as _json
                    metricas = _json.loads(meta).get('metricas', []) or []
                except Exception:
                    metricas = []

            if metricas:
                logger.info("Redirecionando automaticamente para /visualizacoes após processamento (métricas presentes).")
                return "/visualizacoes"

    except Exception as e:
        logger.warning(f"Erro ao avaliar dados de store para redirecionamento: {e}")

    raise PreventUpdate


@callback(
    Output('store-redirecionamento-realizado', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    prevent_initial_call=True
)
def resetar_redirecionamento(pathname):
    if pathname == '/filters':
        logger.info("Redirecionamento resetado para /filters.")
        return False
    raise PreventUpdate

@callback(
    Output('store-lista-dfs', 'data', allow_duplicate=True),
    Input('url', 'pathname'),
    State('store-lista-dfs', 'data'),
    prevent_initial_call=True
)
def normalizar_meta_ao_entrar_em_filtros(pathname, store_data):
    """Normaliza `_meta.metricas` no `store-lista-dfs` ao abrir a página de filtros.
    Intersecta a lista gravada em `_meta` com as colunas realmente presentes nos DataFrames
    salvos no store, evitando que métricas antigas ou removidas continuem visíveis.
    """
    if not pathname or pathname != '/filtros':
        raise PreventUpdate

    if not store_data or not isinstance(store_data, dict):
        raise PreventUpdate

    # Extrai metricas atuais do _meta (pode ser dict ou string)
    meta = store_data.get('_meta')
    metricas = []
    if isinstance(meta, dict):
        metricas = meta.get('metricas', []) or []
    elif isinstance(meta, str):
        try:
            metricas = json.loads(meta).get('metricas', []) or []
        except Exception:
            metricas = []

    if not metricas:
        raise PreventUpdate

    # Coleta colunas disponíveis nos DataFrames do store
    available = set()
    for k, v in store_data.items():
        if k == '_meta':
            continue
        try:
            if isinstance(v, str):
                df = pd.read_json(StringIO(v), orient='split')
            elif isinstance(v, dict):
                df = pd.DataFrame(v)
            else:
                df = pd.read_json(StringIO(str(v)), orient='split')
            available.update([c for c in df.columns if isinstance(c, str)])
        except Exception:
            continue

    # Interseção
    novas_metricas = [m for m in metricas if m in available]

    novo_store = {}
    for k, v in store_data.items():
        if k == '_meta':
            continue
        try:
            if isinstance(v, str):
                df = pd.read_json(StringIO(v), orient='split')
            elif isinstance(v, dict):
                df = pd.DataFrame(v)
            else:
                df = pd.read_json(StringIO(str(v)), orient='split')

            # formato padrão
            novo_store[k] = df.to_json(orient='split')
        except Exception:
            continue

    # grava o _meta normalizado
    novo_store['_meta'] = {'metricas': novas_metricas}
    logger.info(f"_meta normalizado e store regravado ao entrar em /filtros: {novas_metricas}")
    return novo_store


@callback(
    Output('filtro-orientacao-1', 'value'),
    Output('filtro-orientacao-2', 'value'),
    Output('filtro-orientacao-3', 'value'),
    Output('filtro-registro', 'value'),
    Output('filtro-publicacoes', 'value'),
    Output('filtro-outros', 'value'),
    Input('btn-marcar-tudo', 'n_clicks'),
    State('filtro-orientacao-1', 'value'),
    prevent_initial_call=True
)
def alternar_marcar_tudo(n_clicks, orientacao_1_valores):
    if orientacao_1_valores:
        return (
            [],
            [],
            [],
            [],
            [],
            []
        )
    else:
        return (
            ['coorientacao', 'orientacao'],
            ['concluido', 'andamento'],
            ['mestrado', 'doutorado', 'ic', 'tcc-conc', 'conc-esp'],
            ['patente', 'software'],
            ['livros', 'capitulos', 'eventos', 'cientificas'],
            ['eventos_organizados','tecnica']
        )
