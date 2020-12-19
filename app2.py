import os

import chardet
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import statsmodels
from dash.dependencies import Input, Output, State
from dash_bootstrap_components._components.Row import Row
from flask import Flask
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from flask_sqlalchemy import SQLAlchemy
from PIL import Image
from scipy import stats
from statsmodels.regression.linear_model import OLSResults

##################### Read data ###############################################################
dirname = os.path.dirname(__file__)
dataG=pd.read_csv('./res/data/Irca_Departamnetos.csv', sep=';', encoding='latin-1')
dataG=dataG[['Año','Departamento','Municipio','IRCA Promedio 2019','Categoría']]
dataG.columns=['Year','Deparment','City','IRCA','Risk']
dataG_years=list(dataG[['Year','Deparment']].sort_values('Year', ascending=True)['Year'].unique())


data=pd.read_excel('./res/data/IRCA_DB2.xlsx')
data.drop('Unnamed: 0',axis=1,inplace=True)
data['Year']=data['Year'].astype(str)
data['Month']=data['Month'].astype(str)
data['Date'] = data[['Year', 'Month']].apply(lambda x: '-'.join(x), axis=1)
data['Date']=pd.to_datetime(data['Date'], format='%Y%m', errors='ignore')
data=data[['Date','Year','Month','Deparment','City','Samples','IRCA','Risk']]


cat=pd.read_excel('./res/data/IRCA_DB_POB_CAT.xlsx')
cat=cat[['Departamento','Municipio','POB2019','CATEGORIA']]
cat.columns=['Deparment','City','Population','Category']
cat=cat.drop_duplicates()
dic = {
  1: "Class 1",
  2: "Class 2",
  3: "Class 3",
  4: "Class 4",
  5: "Class 5",
  6: "Class 6",
  "ESP":"Special"
}
minerals = ('ARENAS NEGRAS',
            'ASFALTITA',
            'AZUFRE',
            'BARITA',
            'COBRE',
            'FELDESPATOS',
            'MANGANESO',
            'MARMOL',
            'MARMOL EN RAJÓN (RETAL DE MÁRMOL)',
            'MINERAL DE MAGNESIO (MAGNESITA)',
            'NIOBIO',
            'NIQUEL',
            'ORO',
            'PIEDRA ARENISCA-PIEDRA BOGOTANA',
            'PLATINO',
            'PUZOLANAS',
            'ROCA FOSFORICA',
            'SERPENTINA (BLOQUE MENOR A 1 M3)',
            'TALCO',
            'VOLFRAMIO')
cat=cat.replace({"Category": dic})
lisCat=list(cat[['Deparment','Category']].sort_values('Category')['Category'].unique())
lisDepa=list(cat[['Deparment','Category']].sort_values('Deparment')['Deparment'].unique())
data['City']=data['City'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
data=data.merge(cat[['City','Population','Category']],on='City',how='left')
data=data[~data['Category'].isnull()]

##################### Filters ###############################################################

fil_dataG=dcc.Dropdown(
    id="filter-dataG-Year",
    options=[{'label': str(x), 'value': str(x)} for x in dataG_years],
    value='2010', 
    searchable=False,
    style = {'width':'230px'} 
)  



fil_data_yeaG=dcc.Dropdown(
    id="filter-data-YearG",
    options=[{'label': str(x), 'value': str(x)} for x in dataG_years],
    value='2010', 
    searchable=False 
)  


fil_data_catG1=dcc.Dropdown(
    id="filter-data-CatG1",
    options=[{'label': str(x), 'value': str(x)} for x in lisCat],
    value='Class 1', 
    searchable=False 
)

fil_data_catG2=dcc.Dropdown(
    id="filter-data-CatG2",
    options=[{'label': str(x), 'value': str(x)} for x in lisCat],
    value='Class 1', 
    searchable=False 
)



fil_data_cat=dcc.Dropdown(
    id="filter-data-Cat",
    options=[{'label': str(x), 'value': str(x)} for x in lisCat],
    value='Class 1', 
    searchable=False 
)

fil_data_dep=dcc.Dropdown(
    id="filter-data-Dep",
    options=[{'label': str(x), 'value': str(x)} for x in lisDepa],
    value='2010', 
    searchable=False 
)

fil_data_cit=dcc.Dropdown(
    id="filter-data-Cit",
    searchable=False 
)


fil_data_expP=dcc.Dropdown(
    id="filter-data-expP",
    options=[{'label': str(x), 'value': str(x)} for x in minerals],
    value='Class 1', 
    searchable=False 
)

inputPopulation=dbc.InputGroup([dbc.InputGroupAddon("Quantity", addon_type="prepend"),
dbc.Input(id="quantity",placeholder="Write quantity to extract", type="number")])



##################### Tables ###############################################################

table_dataG=dt.DataTable(
    id='table-dataG',
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'center'
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    }
)



def createTable(df):
    table=dt.DataTable(
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    style_cell={
        'whiteSpace': 'normal',
        'height': 'auto',
        'textAlign': 'center'
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold'
    })
    return table


##################### Graph Elements ###############################################################


def grphfcity(data):
    # Box plot 
    boxp = px.box(data, x="Year", y="IRCA")
    boxp.update_traces(quartilemethod="exclusive") 
    # Time line plot
    linep = px.line(data, x="Date",y="IRCA")
    linep.update_xaxes(tickangle=-90)
    return boxp,linep


def col_irca(year):
    # Import Departments IRCA values
    with open('./res/data/Irca_Departamnetos.csv', 'rb') as f:
        result = chardet.detect(f.readline())
    df = pd.read_csv('./res/data/Irca_Departamnetos.csv',delimiter=";",dtype={'Divi_dpto': object, 'Divi_muni': object},encoding=result['encoding'])
    df = df.rename(columns={'Año':'YEAR','Departamento':'NOM_DPTO','Divi_dpto':'COD_DPTO','Municipio':'NOM_MPIO','Divi_muni':'COD_MPIO','IRCA Promedio 2019':'IRCA','Categoría':'CATEGORY'})
    # Import Municipios coordinates
    with open('./res/data/DIVIPOLA_Municipios.csv', 'rb') as f1:
            result2 = chardet.detect(f1.readline())
    # Change columns names        
    df_mun = pd.read_csv('./res/data/DIVIPOLA_Municipios.csv',delimiter=";",dtype={'COD_DPTO': object, 'COD_MPIO': object},encoding=result2['encoding'])

    df_merge=df[['YEAR','COD_MPIO','IRCA','CATEGORY']].merge(df_mun,on='COD_MPIO')

    df_group = df_merge[df_merge['YEAR']==year]


    fig = px.scatter_mapbox(df_group, lat="LATITUD", lon="LONGITUD", color="IRCA", size="IRCA",
                    color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=4,
                    text='NOM_MPIO',labels={'LATITUD':'Lat.','LONGITUD':'Lon.','NOM_MPIO':'City'},
                    mapbox_style="carto-positron")
    fig.update_layout(autosize=True)
    return fig

saMap=col_irca(2010)

CMap=html.Div(dcc.Graph(id='Colombia-map',figure=saMap))


base=dataG[dataG['Year'].astype(str)=='2010']
datPie=base.copy()
datPie['Risk'] = datPie['Risk'].replace({'Bajo':'Low','Medio':'Medium','Alto':'High','Sin información':'No information','Sin riesgo':'Without risk'})
datPie['percentage']=1
datPie=datPie.groupby('Risk').count().reset_index()
datPie=datPie[['Risk','percentage']]
datPie['percentage']=datPie['percentage']/sum(datPie['percentage'])
piecha=dcc.Graph(id='pie-chart',figure={'data': [go.Pie(labels=list(datPie['Risk'].astype(str)), values=list(datPie['percentage']), hole=.2,title='Risk in Water Quality')]})

dataviocha=data[(data['Year'].astype(str)=='2010')&(data['Category']=='Class 1')]
viocha=dcc.Graph(id='violin-chart',figure=px.violin(dataviocha, y="IRCA", x="Category", box=True, points="all",hover_data=dataviocha.columns))

dataCity=data[(data['Category'].astype(str)=='Class 1')&(data['Deparment'].astype(str)=='Antioquia')&(data['City'].astype(str)=='Armenia')]
boxp = px.box(dataCity, x="Year", y="IRCA")
boxp.update_traces(quartilemethod="exclusive") 
boxCity=dcc.Graph(id='box-city',figure=boxp)

linep = px.line(dataCity, x="Date",y="IRCA")
linep.update_xaxes(tickangle=-90)
lineCity=dcc.Graph(id='line-city',figure=linep)


##################### Elements Disposition ###############################################################

# title=html.Div([html.H1('Colombia IRCA Data Analysis'),html.Br()])
title_line1=html.Div([html.H2('Deparments'),html.Br()])
cardCMap = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Risk Map Water Quality in Colombia", className="card-title"),
            CMap
        ]
    )
)
cardfil_dataG = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(dbc.Col(dbc.Row([dbc.Col(html.H4("Filter Results by Year")),
            dbc.Col(fil_dataG)]),width={"size": 6, "offset": 3}))
        ]
    )
)
cardpiecha = dbc.Card(
    dbc.CardBody(
        [
            html.H4("Risk Distribution in Colombia", className="card-title"),
            piecha
        ]
    )
)

line1=html.Div(
    [html.Br(),dbc.Row(dbc.Col(html.Div(cardfil_dataG))),html.Br(),dbc.Row([
    dbc.Col(html.Div(cardCMap,style={'textAlign': 'center'}),align='center',width=7),
    dbc.Col(html.Div(cardpiecha))])])

title_line2=html.Div([html.H2('Categories'),html.Br()])
filters_line2 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Group Selection", className="card-title"),
            html.Div([html.Br(),
                html.H6('Select Year:'),
                dbc.Row([html.Div(fil_data_yeaG, style={'width': '90%'})],justify="center"),
                html.Br(),
                html.H6('Select Group 1:'),
                dbc.Row([html.Div(fil_data_catG1, style={'width': '90%'})],justify="center"),
                html.Br(),
                html.H6('Select Group 2:'),
                dbc.Row([html.Div(fil_data_catG2, style={'width': '90%'})],justify="center"),
                html.Br(),
                dbc.Button("Process", id="compare-groups", color="primary")
            ])
        ]
    )
)



cardReComp = dbc.Card([
    dbc.CardHeader("Comparison of Means"),
    dbc.CardBody(id="result-comparison",children=[
        html.H5("Result Test", className="card-title"),
        html.P("Pvalue=0.000",className="card-text")]),
    dbc.CardFooter(id="result-comparison-text",children=["There is not diference beteewen the mean of groups"]),
])


line2Content = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Group Comparison", className="card-title"),
            html.Br(),
            dbc.Row(html.Div(cardReComp,style={'width': '50%'}),align='center',justify="center"),
            viocha
        ]
    )
)


line2=html.Div([html.Br(),
dbc.Row([
    dbc.Col(dbc.Row([html.Div(filters_line2,style={'width': '80%','textAlign': 'center'})],justify="center"),align='center',width=4),
    dbc.Col(html.Div(line2Content,style={'width': '95%','textAlign': 'center'}))],
    justify="center", 
    align="center"),
    html.Br()])


title_line3=html.Div([html.H2('Cities'),html.Br()])
filters_line3 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("City Selection", className="card-title"),
            html.Div([html.Br(),
                html.H6('Select Category:'),
                dbc.Row([html.Div(fil_data_cat, style={'width': '90%'})],justify="center"),
                html.Br(),
                html.H6('Select Deparment:'),
                dbc.Row([html.Div(fil_data_dep, style={'width': '90%'})],justify="center"),
                html.Br(),
                html.H6('Select City:'),
                dbc.Row([html.Div(fil_data_cit, style={'width': '90%'})],justify="center"),
                html.Br(),
                dbc.Button("Process", id="plot-data", color="primary")
            ])
        ]
    )
)
line3Content = dbc.Card(
    dbc.CardBody(
        [
            html.H3("IRCA Behavior Over the Years", className="card-title"),
            boxCity,
            lineCity
        ]
    )
)
line3=html.Div([html.Br(),
dbc.Row([
    dbc.Col(dbc.Row([html.Div(filters_line3,style={'width': '80%','textAlign': 'center'})],justify="center"),align='center',width=4),
    dbc.Col(html.Div(line3Content,style={'width': '95%','textAlign': 'center'}))],
    justify="center", 
    align="center"),
    html.Br()])


title_line4=html.Div([html.H2('Indentification of Risk Level in Water Quality'),html.Br()])
filters_line4 = dbc.Card(
    dbc.CardBody(
        [
            html.H3("Predict Risk Level Using the Following Variables", className="card-title"),
            html.Div([html.Br(),
                html.H6('Select the mineral to extract:'),
                dbc.Row([html.Div(fil_data_expP, style={'width': '90%'})],justify="center"),
                html.Br(),
                html.H6('Define the quantity to extract:'),
                dbc.Row([html.Div(inputPopulation, style={'width': '90%'})],justify="center"),
                html.Br(),
                dbc.Button("Predict", id="predict-risk", color="primary")
            ])
        ]
    )
)


clasification = html.Div(id='message')
line4=html.Div([html.Br(),
dbc.Row([
    dbc.Col(dbc.Row([html.Div(filters_line4,style={'width': '90%','textAlign': 'center'})],justify="center"),align='center',width=6),
    dbc.Col(html.Div(clasification,style={'width': '90%','textAlign': 'center'}))],
    justify="center", 
    align="center"),
    html.Br()])



tabs = dbc.Tabs(
    [
        dbc.Tab(id='tab1', label="Map Risk"),
        dbc.Tab(id='tab2', label="Categories"),
        dbc.Tab(id='tab3', label="Cities"),
        dbc.Tab(id='tab4', label="Indentification of Risk Level in Water Quality"),
    ], id="tabs",
)

tabCon=html.Div(id="tab-content")

allCon=dbc.Row([html.Div([tabs,tabCon],style={'width': '95%','textAlign': 'center'})],justify="center", align="center")

##################### Login ###############################################################

imgB=Image.open("./res/img/icon.jpg")
bran=html.Img(src=imgB, height="120px")
email_input = dbc.FormGroup(
    [
        dbc.Input(id="user", placeholder="Enter email")
    ]
)
password_input = dbc.FormGroup(
    [
        dbc.Input(type="password",id="password",placeholder="Enter password")
    ]
)
submit=dbc.Button("Sign in", id='login-button', color="primary")
logIn=dbc.Button("login visitor", id='visitor', color="success")

login = html.Div([dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(html.Div(bran,style={'width': '78%'}),align='center',justify="center"),
            html.Br(),
            dbc.Form([
            dbc.Row(html.Div(email_input,style={'width': '90%'}),align='center',justify="center"),
            dbc.Row(html.Div(password_input,style={'width': '90%'}),align='center',justify="center"),
            dbc.Row(html.Div([dbc.Button("You do not have an account, click here", id='create-acount', color="link")],style={'width': '90%'}),align='center',justify="center"),
            html.Br(),
            dbc.Row(html.Div([submit,' ',logIn],style={'width': '90%'}),align='center',justify="center")])
        ]
    )
)],style={'width': '40%','textAlign': 'center'})


loginbody = html.Div([html.Div(style={"height": "24vh"}),dbc.Container([ 
dbc.Row([
            login
            ], justify="center", align="center"
            )
]),html.Div(style={"height": "23vh"})])



##################### User Registration ###############################################################


name_input_new = dbc.FormGroup(
    [
        dbc.Input(id="name", placeholder="Enter your name")
    ]
)

email_input_new = dbc.FormGroup(
    [
        dbc.Input(id="new_user", placeholder="Enter email")
    ]
)
password_input_new = dbc.FormGroup(
    [
        dbc.Input(type="password",id="new_password",placeholder="Enter password")
    ]
)
registrer=dbc.Button("Register", id='register-button', color="primary")

resgister = html.Div([dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(html.Div(bran,style={'width': '78%'}),align='center',justify="center"),
            html.Br(),
            dbc.Form([
            dbc.Row(html.Div(name_input_new,style={'width': '90%'}),align='center',justify="center"),
            dbc.Row(html.Div(email_input_new,style={'width': '90%'}),align='center',justify="center"),
            dbc.Row(html.Div(password_input_new,style={'width': '90%'}),align='center',justify="center"),
            dbc.Row(html.Div(registrer,style={'width': '90%'}),align='center',justify="center")])
        ]
    )
)],style={'width': '40%','textAlign': 'center'})

resgisterbody = html.Div(id='registrer-body',children=html.Div([html.Div(style={"height": "23vh"}),dbc.Container([ 
dbc.Row([
            resgister
            ], justify="center", align="center"
            )
]),html.Div(style={"height": "23vh"})]))


img='https://correlation1-public.s3-us-west-2.amazonaws.com/training/asset_2_2x.png' 

teamgroup = {'team1':['David Vanegas','Ingeniería Mecatrónica','Bogotá','https://ca.slack-edge.com/T01FBG4QQQH-U01EUT5MEBG-e8a680e24200-512'],
'team2':['Javier Quilismal','Ingeniería Mecánica','Bogotá','https://ca.slack-edge.com/T01FBG4QQQH-U01EYGJD8BX-2124d7dfea27-192'],
'team3':['Laura Lucía García','Actuaria','Bucaramanga','https://ca.slack-edge.com/T01FBG4QQQH-U01EUTFB83Y-10d400fb9ef4-512'],
'team4':['Oscar Trujillo','Ingeniería Mecánica - Biomedica','Bogotá','https://ca.slack-edge.com/T01FBG4QQQH-U01EUTF2T0E-7d3d823bd1f6-512'],
'team5':['Sandra Ropero','Estadística','Melbourne - Australia','https://ca.slack-edge.com/T01FBG4QQQH-U01FE8MS1BK-e1ec27e1d28a-512'],
'team6':['Sergio Herrera','Ingeniería Industrial','Ibagué','https://media-exp1.licdn.com/dms/image/C4D03AQGMfaTLL6HWUA/profile-displayphoto-shrink_400_400/0/1596310733503?e=1613606400&v=beta&t=3TN3bIFwlU5oY4JrcLFBhUgyqxpTXS14xzPeX0ng0aM']
}

def cardteam(team):
    card = dbc.Col(dbc.Card(
        [
            dbc.CardImg(src=team[3], top=True),
            dbc.CardBody(
                [
                    html.H5(team[0], className="card-title"),
                    html.P(
                        team[2] + " / " + team[1],
                        className="card-text",
                    )
                ]
            ),
        ],
        style={"width": "12rem"},className="card border-primary mb-3"
    ),width="auto")
    return card
cards =[]
for key in teamgroup:
    cards.append(cardteam(teamgroup[key]))
navbar = dbc.Nav([dbc.Row([dbc.Col(html.Div(html.Img(src=img,height="70px"),className="collapse navbar-collapse"),width={"size": 1, "order": 1,},),
    dbc.Col(html.Button("TEAM 15",className="btn btn-info mx-5",id="collapse-button"), width={"size": 2, "order": 12},),
    dbc.Col(html.H1("Colombia IRCA Data Analysis", className="mx-lg-5"),width={"size": 7, "order": 12},),
    dbc.Col(html.Button("Logout",className="btn btn-info mx-5",id="logout"),width={"size": 2, "order": 12,},)],no_gutters=True,style={'width': '100%'})
    ],className="navbar navbar-expand-lg navbar-dark bg-dark")
collapse = dbc.Collapse(
            dbc.Row(dbc.Col(dbc.Row(cards, no_gutters=True,),width={"size": 11, "offset": 2},)),
            id="collapse",
        )
head = html.Div([
    navbar,
    collapse 
],style={'textAlign': 'center'})

content=html.Div(id='page-content',children=loginbody)

maincontent=html.Div(html.Div([head,html.Br(),allCon],style={'width': '100%'}),id="maincontent")

##################### App Configuration ###############################################################

server= Flask(__name__)
app = dash.Dash(server=server,external_stylesheets=[dbc.themes.CERULEAN])

app.config.suppress_callback_exceptions = True
#app.secret_key = os.urandom(24)
app.server.secret_key = os.urandom(24)


# app = dash.Dash(server=server,external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
app.title = 'WaterQ'
app.layout=html.Div(content)

app.layout=html.Div(content)
app.server.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:team15@localhost/waterq'
app.server.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app.server)
login_manager = LoginManager()
login_manager.init_app(app.server)

##################### Modelo base de datos ###############################################################
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70))
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))
    def __init__(self,name,email,password,):
        self.name = name
        self.email = email
        self.password = password
db.create_all()

##################### Callbacks ###############################################################

@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    [Output('Colombia-map', 'figure'),Output('pie-chart','figure')],
    [Input('filter-dataG-Year', 'value')])
def update_table_dataG(value):
    base=dataG[dataG['Year']==int(value)]
    if len(base)>0:
        loSaMap=col_irca(int(value))
        datPie=base.copy()
        datPie['Risk'] = datPie['Risk'].replace({'Bajo':'Low','Medio':'Medium','Alto':'High','Sin información':'No information','Sin riesgo':'Without risk'})
        datPie['percentage']=1
        datPie=datPie.groupby('Risk').count().reset_index()
        datPie=datPie[['Risk','percentage']]
        datPie['percentage']=datPie['percentage']/sum(datPie['percentage'])
        pie={'data': [go.Pie(labels=list(datPie['Risk'].astype(str)), values=list(datPie['percentage']), hole=.2,title='Risk in Water Quality')]}
        return loSaMap, pie
    else:
        return None,None


@app.callback(
    [Output('result-comparison', 'children'),
    Output('result-comparison-text', 'children'),
    Output('violin-chart', 'figure')],
    [Input('compare-groups', 'n_clicks')],
    [State('filter-data-YearG', 'value'),
    State('filter-data-CatG1', 'value'),
    State('filter-data-CatG2', 'value'),])
def update_output(n_clicks, value1,value2,value3):
    if not str(value2)==str(value3):
        dataviocha=data[(data['Year'].astype(str)==str(value1))&( (data['Category'].astype(str)==str(value2)) | (data['Category'].astype(str)==str(value3)) )]
        g1=dataviocha[dataviocha['Category'].astype(str)==str(value2)]
        g2=dataviocha[dataviocha['Category'].astype(str)==str(value3)]
        statistic, pvalue=stats.ttest_ind(g1.dropna(axis=0)['IRCA'].astype(float),g2.dropna(axis=0)['IRCA'].astype(float),equal_var=False)
        chil1=[html.H5("Result Test", className="card-title"),html.P("Pvalue="+str(pvalue),className="card-text")]
        if pvalue<0.05:
            chil2=["There is diference beteewen the mean of groups"]
        else:
            chil2=["There is not diference beteewen the mean of groups"]
        figure=px.violin(dataviocha, y="IRCA", x="Category", box=True, points="all",hover_data=dataviocha.columns)
        return chil1,chil2,figure
    else:
        chil1=[html.H5("Result Test", className="card-title"),html.P("Pvalue=0.000",className="card-text")]
        chil2=["There is not diference beteewen the mean of groups"]
        dataviocha=data[(data['Year'].astype(str)==str(value1))&(data['Category'].astype(str)==str(value2))]
        figure=px.violin(dataviocha, y="IRCA", x="Category", box=True, points="all",hover_data=dataviocha.columns)
        return chil1,chil2,figure



@app.callback(
    [Output('filter-data-Dep', 'options'),Output('filter-data-Dep', 'value')],
    [Input('filter-data-Cat', 'value')])
def update_Depa(value):
    base=data[data['Category'].astype(str)==str(value)]
    base=list(base.sort_values('Deparment')['Deparment'].unique())
    new_options=[{'label': str(x), 'value': str(x)} for x in base]
    new_value=base[0]
    return new_options, new_value

@app.callback(
    [Output('filter-data-Cit', 'options'),Output('filter-data-Cit', 'value')],
    [Input('filter-data-Dep', 'value')],
    [State('filter-data-Cat', 'value')])
def update_City(value1,value2):
    base=data[(data['Deparment'].astype(str)==str(value1))&(data['Category'].astype(str)==str(value2))]
    base=list(base.sort_values('City')['City'].unique())
    new_options=[{'label': str(x), 'value': str(x)} for x in base]
    new_value=base[0]
    return new_options, new_value


@app.callback(
    [Output('box-city', 'figure'),
    Output('line-city', 'figure')],
    [Input('plot-data', 'n_clicks')],
    [State('filter-data-Cit', 'value'),
    State('filter-data-Cat', 'value'),
    State('filter-data-Dep', 'value')])
def update_contet_line3(n_clicks,value1,value2,value3):
    base=data[(data['City'].astype(str)==str(value1))&(data['Category'].astype(str)==str(value2))&(data['Deparment'].astype(str)==str(value3))]
    if len(base)>0:
        boxp,linep=grphfcity(base)
        return boxp,linep
    else:
        dataCity=data[(data['Category'].astype(str)=='Class 1')&(data['Deparment'].astype(str)=='Antioquia')&(data['City'].astype(str)=='Armenia')]
        boxp = px.box(dataCity, x="Year", y="IRCA")
        boxp.update_traces(quartilemethod="exclusive") 
        linep = px.line(dataCity, x="Date",y="IRCA")
        linep.update_xaxes(tickangle=-90)
        return boxp,linep

def predictRisk(cantidad,recurso):
    model = OLSResults.load("./res/data/model1.pickle")
    value=model.predict(pd.DataFrame({'Cantidad': cantidad, 'Recurso': recurso}, index=[0]))[0]
    risk=''
    if value<=5:
        risk='Without risk'
    elif value>5 and value<=14:
        risk='Low'
    elif value>14 and value<=35:
        risk='Medium'
    elif value>35 and value<=80:
        risk='High'
    elif value>80:
        risk='Sanitary unfeasible'
    return value,risk

@app.callback(
    Output('message', 'children'),
    [Input('predict-risk', 'n_clicks')],
    [State('filter-data-expP', 'value'),
    State('quantity', 'value')])
def update_contet_line4(n_clicks,value1,value2):
    value,risk=predictRisk(value2,value1)
    value = round(value,2)
    if value>100:
        value = 100
    if risk=="Without risk" or risk=="Low":
        children= dbc.Card([dbc.CardHeader("Safe"),
        dbc.CardBody([html.H5("IRCA value: "+str(value)+" Risk type: "+risk, className="card-title"),
        html.P("There is not risk",className="card-text")])],
        color="success", inverse=True)
    elif risk=="Medium":
        children= dbc.Card([dbc.CardHeader("Warning"),
        dbc.CardBody([html.H5("IRCA value: "+str(value)+" Risk type: "+risk, className="card-title"),
        html.P("There is  risk",className="card-text")])],
        color="warning", inverse=True)
    elif risk=="High" or risk=="Sanitary unfeasible":
        children= dbc.Card([dbc.CardHeader("Danger"),
        dbc.CardBody([html.H5("IRCA value: "+str(value)+" Risk type: "+risk, className="card-title"),
        html.P("There is  risk",className="card-text")])],
        color="danger", inverse=True)
    else:
        children= None
    return children


@app.callback(
    Output("tab-content", "children"), 
    [Input("tabs", "active_tab")])
def display_tab_content(active_tab):
    
    if active_tab == "tab-0":
        return line1
    elif active_tab == "tab-1":
        return line2
    elif active_tab == "tab-2":
        return line3
    elif active_tab == "tab-3":
        return line4
    elif active_tab == None:
        return line1
    return "Something went wrong..."+str(active_tab)

@app.callback(Output('page-content', 'children'),
              [Input('login-button', 'n_clicks'),
              Input('create-acount', 'n_clicks'),
              Input('visitor', 'n_clicks')],
              [State('user', 'value'),
               State('password', 'value')])
def success(n_clicks1,n_clicks2,n_clicks3, input1, input2):
    ctx = dash.callback_context
    if not ctx.triggered:
        object_id = 'No clicks yet'
    else:
        object_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if object_id=='login-button':
        if not n_clicks1==None:
            if n_clicks1 >= 1:
                user = User.query.filter_by(email=input1).first()
                print(user)
                if str(user.password) == str(input2):
                    login_user(user)
                    return maincontent
                else:
                    return loginbody
            else: 
                return loginbody
        else:
            return loginbody
    elif object_id=='create-acount':
        if not n_clicks2==None:
            if n_clicks2 >= 1:
                return resgisterbody
            else: 
                return loginbody
        else:
            return loginbody
    elif object_id=='visitor':
        return maincontent
    else:
        return loginbody


@app.callback(Output('registrer-body', 'children'),
              [Input('register-button', 'n_clicks')],
              [State('name', 'value'),
               State('new_user', 'value'),
               State('new_password', 'value')])
def register(n_clicks, input1, input2, input3):
    ctx = dash.callback_context
    if not ctx.triggered:
        object_id = 'No clicks yet'
    else:
        object_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if object_id=='register-button':
        if not n_clicks==None:
            if n_clicks >= 1:
                new_user = User(input1,input2,input3)
                db.session.add(new_user)
                db.session.commit()
                return loginbody
            else: 
                return loginbody
        else:
            return loginbody
    raise dash.exceptions.PreventUpdate

@app.callback(Output('maincontent', 'children'),
              [Input('logout', 'n_clicks')],)
def logout(n_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        object_id = 'No clicks yet'
    else:
        object_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if object_id=='logout':
        if not n_clicks==None:
            if n_clicks >= 1:
                # logout_user()
                return loginbody
            else: 
                return loginbody
        else:
            return loginbody
    raise dash.exceptions.PreventUpdate

if __name__== '__main__':
    app.run_server(debug=False)
