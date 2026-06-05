import dash
from dash import html, dcc, Input, Output, no_update, callback_context, State
import dash_bootstrap_components as dbc
import logging
from io import BytesIO
import pandas as pd
from Read_Data.constants import MENSAGENS_TUTORIAL

# Configuração básica de logs
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Configurar o logger
logger = logging.getLogger('dash_app')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=False
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='store-uploaded-data', storage_type='session'),
    dcc.Store(id='store-lista-dfs', storage_type='session'),
    dcc.Store(id='step-tutorial-store', data=0),
    dcc.Store(id='store-redirecionamento-realizado', data=False),
    dcc.Store(id='redirect-trigger-store', data=False),

    dbc.Modal(
        [
            dbc.ModalHeader("ERRO", style={'fontWeight': 'bold', 'color': 'red'}),
            dbc.ModalBody(id="modal-error-message", style={'fontWeight': 'bold'}),
            dbc.ModalFooter(dbc.Button("Fechar", id="close-modal", className="ml-auto")),
        ],
        id="error-modal",
        is_open=False,
    ),

    dbc.Modal(
        [
            html.Div([
                dcc.Download(id="download-template"),
                html.Button("Baixar modelo", id="download-template-button", style={"display": "none"})
            ]),

            dbc.ModalHeader(
                "TUTORIAL",
                style={'fontWeight': 'bold', 'color': 'red'}
            ),
            dbc.ModalBody(
                dcc.Markdown(
                    id="modal-tutorial-message"
                )
            ),
            dbc.ModalFooter(
                dbc.Row([
                    dbc.Col(
                        dbc.Button("Voltar", id="back-button-tutorial", n_clicks=0),
                        width="auto",
                        style={"textAlign": "left"}
                    ),
                    dbc.Col(width=True),
                    dbc.Col(html.Span("Passo 1 de 5", id="step_tutorial"),
                            width="auto",
                            style={"textAlign": "center", 'margin-top': '1%', 'color': '#495057'}),
                    dbc.Col(width=True),
                    dbc.Col(
                        dbc.Button("Próximo", id="next-button-tutorial", n_clicks=0),
                        width="auto",
                        style={"textAlign": "right", 'marginRight': '10px'}
                    ),
                ],
                        className="w-100")
            )
        ],
        id="tutorial-modal",
        is_open=False,
    ),

    dash.page_container
])

@app.callback(
    Output('tutorial-modal', 'is_open'),
    Output('modal-tutorial-message', 'children'),
    Output('step_tutorial', 'children'),
    Output('step-tutorial-store', 'data'),
    Output('back-button-tutorial', 'disabled'),
    Output('next-button-tutorial', 'children'),
    Input('open-tutorial-link', 'n_clicks'),
    Input('next-button-tutorial', 'n_clicks'),
    Input('back-button-tutorial', 'n_clicks'),
    State('step-tutorial-store', 'data'),
    prevent_initial_call=True
)
def toggle_tutorial_modal_and_update_step(open_clicks, next_clicks, back_clicks, step):
    total_steps = len(MENSAGENS_TUTORIAL)
    ctx = callback_context

    if not ctx.triggered:
        return no_update, no_update, no_update, no_update, no_update, no_update

    trigger_id = ctx.triggered_id

    is_open = no_update
    message = no_update
    step_text = no_update
    new_step = no_update
    back_disabled = no_update
    next_button_text = no_update

    if trigger_id == "open-tutorial-link" and open_clicks:
        is_open = True
        message = MENSAGENS_TUTORIAL[0]
        step_text = "Passo 1 de 5"
        new_step = 0
        back_disabled = True
        next_button_text = "Próximo"
    elif trigger_id == "next-button-tutorial" and next_clicks:
        if step < total_steps - 1:
            new_step = step + 1
            is_open = True
            message = MENSAGENS_TUTORIAL[new_step]
            step_text = f"Passo {new_step + 1} de {total_steps}"
            back_disabled = (new_step == 0)
            next_button_text = "Finalizar" if new_step == total_steps - 1 else "Próximo"
        else:
            is_open = False
            new_step = 0
            back_disabled = True
            next_button_text = "Próximo"
    elif trigger_id == "back-button-tutorial" and back_clicks:
        if step > 0:
            new_step = step - 1
            is_open = True
            message = MENSAGENS_TUTORIAL[new_step]
            step_text = f"Passo {new_step + 1} de {total_steps}"
            back_disabled = (new_step == 0)
            next_button_text = "Finalizar" if new_step == total_steps - 1 else "Próximo"
        else:
            return no_update, no_update, no_update, no_update, no_update, no_update

    return is_open, message, step_text, new_step, back_disabled, next_button_text

@app.callback(
    Output("download-template", "data"),
    Input("download-template-button", "n_clicks"),
    prevent_initial_call=True
)
def download_template(n_clicks):
    if n_clicks:
        df_template = pd.DataFrame({
            'Nome Completo': ['Exemplo Nome'],
            'Link Lattes': ['http://lattes.cnpq.br/1234567890123456']
        })
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df_template.to_excel(writer, sheet_name='Pesquisadores', index=False)
        writer.close()
        output.seek(0)
        return dcc.send_bytes(output.getvalue(), "modelo_extrator_lattes.xlsx")
    return no_update

@app.callback(
    Output('error-modal', 'is_open'),
    Input('close-modal', 'n_clicks'),
    State('error-modal', 'is_open'),
    prevent_initial_call=True
)
def close_error_modal(n_clicks, is_open):
    if n_clicks:
        return False
    return no_update

if __name__ == '__main__':
    app.run(debug=False) # host='10.0.83.49', para rodar local na máquina da UPE

