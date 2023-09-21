import cx_Oracle
import dash
import pandas as pd
from dash import Dash, Input, Output, html, dcc, callback
from dash.dash_table import DataTable

#CONECÇÃO................................................................
username = 'NOME'
password = 'SUA SENHA'
host = 'IP'
port = '....'
dns = 'Domain Name System'

#EXMPLO DE SELECT..........................................................
query = '''SELECT PCPRODUT.CODPROD, PCPRODUT.DESCRICAO, PCPRODUT.EMBALAGEM,  PCTABPR.PVENDA1, 
PCDESCONTO.percdesc, to_char(PCDESCONTO.dtinicio,'dd/mm/yyyy'), to_char(PCDESCONTO.dtfim,'dd/mm/yyyy'), 
PCDESCONTO.qtini, PCDESCONTO.qtfim FROM PCDESCONTO LEFT JOIN PCPRODUT ON PCDESCONTO.CODPROD = 
PCPRODUT.CODPROD LEFT JOIN PCTABPR ON PCDESCONTO.CODPROD = PCTABPR.CODPROD WHERE PCTABPR.NUMREGIAO = 1 AND 
PCDESCONTO.DTFIM >= SYSDATE ORDER BY PCPRODUT.DESCRICAO ASC '''


def consultar_e_imprimir_tabela():
    try:

        connection = cx_Oracle.connect(username, password, f'{host}:{port}/{dns}')
        cursor = connection.cursor()

        cursor.execute(query)

        results = []
        for row in cursor:
            results.append(row)

        cursor.close()
        connection.close()

        df = pd.DataFrame(results)
        df.columns = ['CODIGO DO PRODUTO', 'NOME DO PRODUTO', 'EMBALAGEM', 'PREÇO', 'PERCENTUAL DE DESCONTO', 'INICIO',
                      'FIM DA PROMOÇÃO', 'QUANTIDADE INICIAL', 'QUANTIDADE FINAL']
        df['PERCENTUAL DE DESCONTO'] = df['PERCENTUAL DE DESCONTO'].apply(lambda x: f'{x:.2f}%')
        df['PREÇO'] = df['PREÇO'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

        columns_initial = [{'name': str(col), 'id': str(col)} for col in df.columns]

        data_initial = df.to_dict('records')

        return data_initial, columns_initial

    except Exception as e:
        print("Erro ao consultar e imprimir a tabela:", e)


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Input(id="search_input", type="text", placeholder="Pesquisar por produto...", autoComplete="off"),
    html.Button("Executar Consulta", id="button_id"),
    DataTable(id="result_table_div")
])


def update_search_options(search_term):
    try:

        connection = cx_Oracle.connect(username, password, f'{host}:{port}/{dns}')
        cursor = connection.cursor()

        cursor.execute(query)

        results = [{'label': row[1], 'value': row[0]} for row in cursor]

        cursor.close()
        connection.close()

        return results
    except Exception as e:
        return []


@app.callback(
    Output("result_table_div", "data"),
    Output("result_table_div", "columns"),
    Input("button_id", "n_clicks"),
    Input("search_input", "value"),
)
def execute_query(n_clicks, search_term):
    if n_clicks is None:
        return consultar_e_imprimir_tabela()

    try:
        connection = cx_Oracle.connect(username, password, f'{host}:{port}/{dns}')
        cursor = connection.cursor()

        search_term = search_term.replace(" ", "%")

        query_busca = '''SELECT PCPRODUT.CODPROD, PCPRODUT.DESCRICAO, PCPRODUT.EMBALAGEM,  PCTABPR.PVENDA1, 
        PCDESCONTO.percdesc, to_char(PCDESCONTO.dtinicio,'dd/mm/yyyy'), to_char(PCDESCONTO.dtfim,'dd/mm/yyyy'), 
        PCDESCONTO.qtini, PCDESCONTO.qtfim FROM PCDESCONTO LEFT JOIN PCPRODUT ON PCDESCONTO.CODPROD = 
        PCPRODUT.CODPROD LEFT JOIN PCTABPR ON PCDESCONTO.CODPROD = PCTABPR.CODPROD WHERE PCTABPR.NUMREGIAO = 1 AND 
        PCDESCONTO.DTFIM >= SYSDATE ORDER BY PCPRODUT.DESCRICAO ASC '''

        if search_term:
            query_busca = f'''SELECT PCPRODUT.CODPROD, PCPRODUT.DESCRICAO, PCPRODUT.EMBALAGEM,  PCTABPR.PVENDA1, 
            PCDESCONTO.percdesc, to_char(PCDESCONTO.dtinicio,'dd/mm/yyyy'), to_char(PCDESCONTO.dtfim,'dd/mm/yyyy'), 
            PCDESCONTO.qtini, PCDESCONTO.qtfim FROM PCDESCONTO LEFT JOIN PCPRODUT ON PCDESCONTO.CODPROD = 
            PCPRODUT.CODPROD LEFT JOIN PCTABPR ON PCDESCONTO.CODPROD = PCTABPR.CODPROD WHERE PCTABPR.NUMREGIAO = 1 
            AND PCDESCONTO.DTFIM >= SYSDATE AND (PCPRODUT.DESCRICAO LIKE UPPER('%{search_term}%')) 
            ORDER BY PCPRODUT.DESCRICAO ASC'''

        cursor.execute(query_busca)

        results = []
        for row in cursor:
            results.append(row)

        cursor.close()
        connection.close()

        df = pd.DataFrame(results)
        df.columns = ['CODIGO DO PRODUTO', 'NOME DO PRODUTO', 'EMBALAGEM', 'PREÇO', 'PERCENTUAL DE DESCONTO', 'INICIO',
                      'FIM DA PROMOÇÃO', 'QUANTIDADE INICIAL', 'QUANTIDADE FINAL']
        df['PERCENTUAL DE DESCONTO'] = df['PERCENTUAL DE DESCONTO'].apply(lambda x: f'{x:.2f}%')
        df['PREÇO'] = df['PREÇO'].apply(lambda x: f'R$ {x:.2f}'.replace('.', ','))

        columns = [{'name': str(col), 'id': str(col)} for col in df.columns]

        data = df.to_dict('records')

        return data, columns
    except Exception as e:
        return [], [{'name': 'Erro', 'id': 'Erro'}]

#ABRIR O SERVIDOR LOCAL.................
if __name__ == '__main__':
    app.run_server(debug=True)
