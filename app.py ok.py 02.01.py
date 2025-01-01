import streamlit as st
import pandas as pd
import plotly.express as px

# Título do app
st.title("Indicadores de Dados de Entregas")

# Opção para carregar uma base de dados (CSV ou Excel)
uploaded_file = st.file_uploader("Carregue sua base de dados (CSV ou Excel)", type=["csv", "xlsx"])

# Inicialização do DataFrame
df = None

# Carregar os dados
if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1]

    # Leitura da base de dados dependendo da extensão
    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension == 'xlsx':
        df = pd.read_excel(uploaded_file)

    st.write("Dados Carregados:")
    st.write(df)
else:
    st.write("Nenhum arquivo carregado. Por favor, carregue uma planilha.")

# Verifica se o DataFrame foi carregado corretamente antes de realizar qualquer operação
if df is not None:
    # Garantir que as colunas de data estejam no formato datetime
    for column in ['DATA DO ACIONAMENTO', 'DATA REAL DA COLETA', 'DATA PROGRAMADA DA ENTREGA', 
                   'DATA REAL DE ENTREGA', 'DATA REPROGRAMAÇÃO', 'DATA DE ENTREGA DA REVERSA']:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors='coerce')

    # Substituindo valores nulos ou ausentes nas colunas de data
    df.fillna(method='ffill', inplace=True)

    # Sidebar com opções de navegação
    option = st.sidebar.selectbox(
        "Selecione o gráfico para visualizar",
        ("Status de Entrega", "SLA de Entrega", "Quantidade de Reserva Pedido ao Longo do Tempo")
    )

    # Cores solicitadas para o gráfico de Status de Entrega
    color_map_status = {
        'CANCELADO': '#808080',    # cinza escuro
        'COLETADO': '#D3D3D3',     # cinza claro
        'CONCLUÍDO': '#A9A9A9',    # cinza médio
        'EXTRAVIO': '#8B0000',     # vermelho escuro
        'IMPRODUTIVA': '#D60000',  # vermelho claro
    }

    # Gráficos baseados na seleção do usuário
    if option == "SLA de Entrega":
        st.header("SLA de Entrega: Dentro do Prazo vs Fora do Prazo")

        # Dados para o gráfico de SLA
        sla_data = {
            'Status SLA': ['No Prazo', 'Fora do Prazo'],
            'Qtd': [3703, 5],
            'Porcentagem': ['99,87%', '0,13%']
        }
        sla_df = pd.DataFrame(sla_data)

        # Gráfico de pizza para SLA
        fig_sla_pizza = px.pie(sla_df,
                               names='Status SLA',
                               values='Qtd',
                               title='Classificação de Entregas (Dentro vs Fora do Prazo)',
                               color='Status SLA',
                               color_discrete_map={
                                   'No Prazo': '#808080',  # cinza médio
                                   'Fora do Prazo': '#8B0000'  # vermelho escuro
                               },
                               labels={'Qtd': 'Quantidade', 'Status SLA': 'Classificação'},
                               hole=0.3)  # Cria um gráfico de pizza com "furo" no centro
        st.plotly_chart(fig_sla_pizza)

        st.write(""" 
            O gráfico de pizza mostra a distribuição das entregas dentro e fora do prazo. 
            A grande maioria das entregas estão dentro do prazo ('No Prazo'), representando 99,87% do total, 
            enquanto uma pequena fração está fora do prazo ('Fora do Prazo'), com apenas 0,13%.
        """)

    elif option == "Status de Entrega":
        st.header("Análise de Status de Entrega")
        
        # Dados para o gráfico de Status de Entrega
        status_data = {
            'Status de Entrega': ['CANCELADO', 'COLETADO', 'CONCLUÍDO', 'EXTRAVIO', 'IMPRODUTIVA'],
            'Qtd': [3, 211, 3437, 21, 36],
            'Porcentagem': ['0,08%', '5,69%', '92,69%', '0,57%', '0,97%']
        }
        status_df = pd.DataFrame(status_data)

        # Gráfico de barras para Status de Entrega
        fig_status = px.bar(status_df,
                            x='Status de Entrega',
                            y='Qtd',
                            title='Distribuição do Status da Entrega',
                            color='Status de Entrega',
                            color_discrete_map=color_map_status,
                            labels={'Qtd': 'Quantidade', 'Status de Entrega': 'Status'},
                            text='Porcentagem')

        # Ajustando a largura das colunas
        fig_status.update_traces(marker=dict(line=dict(width=1)))
        fig_status.update_layout(bargap=0.2)  # Ajusta o espaçamento entre as barras
        st.plotly_chart(fig_status)

        st.write(""" 
            O gráfico de barras mostra a quantidade de entregas em cada status. A categoria 'Concluído' é a mais predominante, 
            com 92,69% das entregas, seguida por 'Coletado' com 5,69%. 'Extravio', 'Improdutiva' e 'Cancelado' têm pequenas 
            quantidades em comparação com as demais.
        """)

    elif option == "Quantidade de Reserva Pedido ao Longo do Tempo":
        st.header("Quantidade de Reserva Pedido ao Longo do Tempo")

        # Garantir que as datas estejam no formato correto
        if 'DATA DO ACIONAMENTO' in df.columns:
            df['Data do Acionamento'] = pd.to_datetime(df['DATA DO ACIONAMENTO'], errors='coerce')

            # Contagem de reservas por data
            reservas_por_data = df.groupby(df['Data do Acionamento'].dt.date).size().reset_index(name='Quantidade')

            # Gráfico de linha para quantidade de reservas
            fig_reservas = px.line(reservas_por_data,
                                   x='Data do Acionamento',
                                   y='Quantidade',
                                   title='Quantidade de Reserva Pedido ao Longo do Tempo',
                                   labels={'Quantidade': 'Quantidade de Reservas', 'Data do Acionamento': 'Data'},
                                   line_shape="linear",  # Linha simples
                                   markers=False)  # Sem marcadores
            fig_reservas.update_traces(line=dict(color='#A9A9A9'))  # Cinza médio
            st.plotly_chart(fig_reservas)

            st.write(""" 
                O gráfico de linha mostra a evolução das reservas ao longo do tempo, utilizando a cor cinza. 
                É possível observar as variações nas quantidades de pedidos e identificar picos e quedas nas reservas.
            """)
        else:
            st.write("A coluna 'DATA DO ACIONAMENTO' não foi encontrada nos dados.")

    # Conclusão
    st.header("Conclusão")
    st.write(""" 
        A análise realizada fornece insights sobre o status das entregas. 
        O gráfico de pizza mostra que a maioria das entregas estão no status 'Concluído', 
        com uma pequena quantidade nas categorias 'Coletado', 'Improdutiva', 'Extravio' e 'Cancelado'. 
        O gráfico de barras complementa essas informações, oferecendo uma visão clara da quantidade de entregas por status.
        Além disso, a análise da quantidade de reservas ao longo do tempo mostra as flutuações nas reservas, 
        permitindo entender melhor o comportamento ao longo do período.
    """)
