from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px

app = Dash(__name__)

#url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=683788'
frames=[]
for i in range (1,13):
    url = "https://raw.githubusercontent.com/djunga/DATA608/main/tree"+str(i)+".csv"
    frames.append(pd.read_csv(url))

df2 = pd.concat(frames)[["spc_common", "borough", "health", "steward"]]
df1 = df2[["spc_common", "borough", "health"]] # question 1

def getData1(x):
    boroughs=["Brooklyn", "Bronx", "Manhattan", "Queens", "Staten Island"]
    conditions=["Good", "Fair", "Poor"]
    data=[]
    for b in boroughs:
        arr = []
        for c in conditions:
            prop=len(x.loc[(x.borough==b) & (x.health==c)]) / len(x)
            data.append([b,c,round(prop, 2)])
    y = pd.DataFrame(data, columns=["borough", "condition", "prop"])

    return y

def getData2(x):
    x = x.dropna(subset=["steward", "spc_common"])
    data=[]
    health=["Good", "Fair", "Poor"]
    steward=["4orMore", "3or4", "1or2", "None"]
    for h in health:
        perc = []
        for s in steward:
            perc.append(len(x.loc[(x.steward==s) & (x.health==h)]) / len(x))
        data.append(perc)
    return data

app.layout = html.Div([
    html.Div([
        dcc.Dropdown(list(df2.spc_common.unique()), value='pin oak', id="dropdown"),
        dcc.Graph(id="graph1")
    ], style={'padding': 10, 'flex': 1}),
    html.Div([
        dcc.RadioItems(list(df2.borough.unique()), value="Brooklyn", id="radio"),
        dcc.Graph(id="graph2")
    ], style={'padding': 10, 'flex': 1})
], style={'display': 'flex', 'flex-direction': 'row'})

# Graph 1, the bar plot
@app.callback(
    Output(component_id='graph1', component_property='figure'),
    Input(component_id='dropdown', component_property="value")
)
def update_barplot(species):
    filtered=df1[df2.spc_common == species]
    fig = px.bar(getData1(filtered), x="borough", y="prop", color="condition", 
    range_y=[0.0,1.0],
    barmode="group",
    template="plotly_dark",
    labels = {
        "borough": "borough",
        "prop": "Proportion",
        "condition": "Condition"
    },
    title=species.title() + " Health in NYC")

    fig.update_layout(xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
    )

    return fig

# Graph 2, the heatplot
@app.callback(
    Output(component_id='graph2', component_property='figure'),
    Input(component_id='radio', component_property="value"),
    Input(component_id='dropdown', component_property="value")
)
def update_heatplot(borough, species):
    filtered = df2.loc[(df2.borough==borough) & (df2.spc_common==species)]
    health=["Good", "Fair", "Poor"]
    steward=["4orMore", "3or4", "1or2", "None"]
    fig = px.imshow(getData2(filtered),
                labels=dict(x="Steward", y="Health", color="Percent of Trees"),
                x=steward,y=health)
    fig.update_xaxes(side="top")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
