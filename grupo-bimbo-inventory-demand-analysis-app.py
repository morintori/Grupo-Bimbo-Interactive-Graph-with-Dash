from dash import Dash, html, dcc, ctx
import plotly.express as px
import pandas as pd
import dask.dataframe as dd
from dash.dependencies import Input,Output
import numpy as np
np.set_printoptions(threshold=np.inf)

df = dd.read_csv('data agg.csv')
df = df.rename(columns={'Demanda_uni_equil':'Adjusted Demand','cluster':'Product Cluster','Semana':'Week',\
                        'State_ID':'State'})
product_list = pd.read_csv('products_w_clusters.csv')
clusters_prod = product_list['cluster'].unique()
product_names = np.sort(product_list['NombreProducto'].unique())
state_list=pd.read_csv('State_labels.csv')
state_list=state_list.rename(columns={'State':'State Name'})
state_list = state_list.rename(columns={'State_ID':'State'})

semana_list = [3,4,5,6,7,8,9,10,11]

sum_fig_df = df[['Week','Adjusted Demand']].groupby(['Week']).sum().reset_index().compute()
summary_fig = px.bar(sum_fig_df,x='Week',y='Adjusted Demand')
summary_fig.update_layout(title = 'Adjusted Demand by Week', title_x=0.5)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


app.layout = html.Div([
    html.H2(children='Grupo Bimbo Demand'),
    html.H6('Product Clusters/States in the bar chart can be clicked to display its distribution in the pie chart'
            ', the products in the pie chart can be clicked to display its demand over time. The dropdown menu '
            'below for product names can be chosen to display its time series. Below that, product clusters can be '
            'chosen to see its component products'),
    html.Div([

        html.Div([
            html.H6('Choose Product Cluster or State Here'),
            dcc.Dropdown(
                ['Product Cluster','State'],
                'Product Cluster',
                id='crossfilter-xaxis-column',
            ),
            # dcc.RadioItems(
            #     ['Linear', 'Log'],
            #     'Linear',
            #     id='crossfilter-xaxis-type',
            #     labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            # )
        ],
            style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            # dcc.Dropdown(
            #     df['Indicator Name'].unique(),
            #     'Life expectancy at birth, total (years)',
            #     id='crossfilter-yaxis-column'
            # ),

        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-bar',
            clickData={'points': [{'label': '22'}]}
        ),
        dcc.Slider(
            # df['Semana'].min().compute(),
            # df['Semana'].max().compute(),
            3,
            11,
            step=None,
            id='crossfilter-Semana-slider',
            # value=df['Semana'].max(),
            value=11,
            marks={str(Semana): str(Semana) for Semana in semana_list}
        ),

    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
    html.Div([
        dcc.Graph(id='cluster-pie',
                  clickData={'points': [{'label': '0'}]},
                  hoverData={'points': [{'label': '0'}]}
                  ),
        html.Pre(id='product name'),
        dcc.RadioItems(
            ['Linear', 'Log'],
            'Linear',
            id='crossfilter-yaxis-type',
            labelStyle={'display': 'inline-block', 'marginTop': '5px'}
        ),

        dcc.Graph(id='time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),

    # html.Div(
    #     dcc.Slider(
    #     # df['Semana'].min().compute(),
    #     # df['Semana'].max().compute(),
    #     3,
    #     11,
    #     step=None,
    #     id='crossfilter-Semana-slider',
    #     # value=df['Semana'].max(),
    #     value = 11,
    #     marks={str(Semana): str(Semana) for Semana in semana_list}
    # ), style={'width': '49%', 'padding': '0px 20px 20px 20px'}),
    # generate_table(df),
    html.Div(className='row',children=[
        html.Div([
            dcc.Graph(
                id='summary-bar',
                figure= summary_fig
            ),
            html.H6('Select Product Name to View Demand Over Time Here'),
            dcc.Dropdown(product_names,id='time-series-select',\
                      placeholder='Search Product Name Here'),
            html.H6('Product Cluster',id='display_type'),

            dcc.Dropdown(clusters_prod,id='product_cluster'),
            html.Hr(),
            html.Pre(id = 'display_product_names',style = styles['pre'])
            ], className = 'twelve columns'),
        ])
    # html.Div(children = [
    #     html.Pre(id = 'display_product_names',style = styles['pre'])
    #     ], className = 'twelve columns'),
])
# @app.callback(
#     Output('summary-bar','figure'),
#     Input('crossfilter-xaxis-column','value')
# )
# def update_summary(type):

# @app.callback(
#     Output('display_type','children'),
#     Input('crossfilter-xaxis-column','value')
# )
# def change_label(value):
#
#     return value

# @app.callback(
#     Output('product_cluster','options'),
#     Input('crossfilter-xaxis-column','value')
# )
# def fill_dropdown(value):
#
#     if value == 'Product Cluster':
#         fill_list = clusters_prod
#     elif value == 'State':
#         fill_list = state_list['State Name'].unique()
#     return fill_list

@app.callback(
    Output('display_product_names','children'),
    Input('product_cluster','value'),
)
def show_cluster(value):
    prodInClust = product_list[product_list['cluster']==value]['NombreProducto'].unique()

    return '{}'.format(prodInClust)

@app.callback(
    Output('crossfilter-indicator-bar','figure'),
    Input('crossfilter-Semana-slider','value'),
    Input('crossfilter-xaxis-column','value')
)
def update_graph(semana,x_type):
    dff = df[df['Week'] == semana][[x_type,'Adjusted Demand']].groupby(x_type)\
        .sum().reset_index().compute()
    # print(dff.columns)
    fig = px.bar(dff,x=x_type,y='Adjusted Demand',title = 'Demand By ' + x_type,height = 700)
    if x_type == 'Product Cluster':
        fig.update_xaxes(title=x_type, type='linear',dtick = 1)
    elif x_type =='State':
        fig.update_xaxes(title=x_type, tickmode='array', tickvals = state_list['State'].values.tolist(),\
                         ticktext= state_list['State Name'].values.tolist())

    fig.update_yaxes(title='Adjusted Demand', type='log')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 30, 'r': 0}, title_x=0.5,hovermode='closest')
    return fig

def create_pie(dff,title):
    fig = px.pie(dff,
                 # names='NombreProducto',
                 names = 'Producto_ID',
                 values='Adjusted Demand',
                 height = 700
                 )
    # fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
    #                    xref='paper', yref='paper', showarrow=False, align='left',
    #                    text=title)
    fig.update_traces(textposition='inside')
    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide',margin=dict(t=50, l=25, r=25, b=25),\
                      title ='Distribution of Product Demand in ' + title)

    return fig

def create_time_series(dff,axis_type,title):

    fig = px.scatter(dff,x='Week',y='Adjusted Demand')
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False,tickmode='linear',dtick=1)
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 30}, title = 'Product Demand Time Series',\
                      title_x = 0.5)
    return fig

@app.callback(
    Output('product name','children'),
    Input('cluster-pie','hoverData'),
)
def display_product_name(hoverData):
    # print(hoverData)
    product_ID = hoverData['points'][0]['label']
    # print(type(product_ID))
    # print(product_list[product_list['Producto_ID']==product_ID])
    product_name = product_list[product_list['Producto_ID']==int(product_ID)]['NombreProducto'].item()
    return str(product_name)

# @app.callback(
#     Output('time-series','figure'),
#     Input('time-series-select','value'),
#     Input('crossfilter-yaxis-type', 'value')
# )
# def update_ts(productName,axis_type):
#
#     product_id = product_list[product_list['NombreProducto']==productName]['Producto_ID'].item()
#     # print(product_id)
#     dff =df[df['Producto_ID']==int(product_id)]
#
#     dff = dff[[ 'Week', 'Adjusted Demand']].groupby(['Week']).sum().reset_index().compute()
#
#     product_name= product_list[product_list['Producto_ID']==int(product_id)]['NombreProducto'].item()
#     return create_time_series(dff,axis_type,product_name)

@app.callback(
    Output('time-series','figure'),
    Input('cluster-pie','clickData'),
    Input('time-series-select','value'),
    Input('crossfilter-yaxis-type', 'value')
)
def update_ts(clickData,dropData,axis_type):
    trig_id = ctx.triggered_id if not None else 1
    if trig_id == 'time-series-select':
        product_nm = ctx.triggered[0]['value']
        product_id = product_list[product_list['NombreProducto']==product_nm]['Producto_ID'].item()
    else:
        product_id = clickData['points'][0]['label']
    # print(product_id)
    dff =df[df['Producto_ID']==int(product_id)]

    dff = dff[[ 'Week', 'Adjusted Demand']].groupby(['Week']).sum().reset_index().compute()

    product_name= product_list[product_list['Producto_ID']==int(product_id)]['NombreProducto'].item()
    return create_time_series(dff,axis_type,product_name)


@app.callback(
    Output('cluster-pie', 'figure'),
    Input('crossfilter-indicator-bar', 'clickData'),
    Input('crossfilter-Semana-slider','value'),
    Input('crossfilter-xaxis-column','value')
    # Input('crossfilter-xaxis-column', 'value'),
    # Input('crossfilter-xaxis-type', 'value'))
)
def update_pie(clickData,semana,x_type):

    cluster_name = clickData['points'][0]['label']

    dff = df[df['Week'] == semana]
    dff = dff[dff[x_type] == cluster_name][['Producto_ID', 'Adjusted Demand']].compute()
        # .sort_values(by=['Adjusted Demand'], ascending=False).compute()
    if x_type == 'State':
        cluster_name = state_list[state_list['State']==int(cluster_name)]['State Name'].item()

    title = '<b>{} {}</b><br>week:{}'.format(x_type,cluster_name, semana)
    return create_pie(dff,title)
# @app.callback(
#     Output()
# )
if __name__=='__main__':
    app.run_server(debug=True)