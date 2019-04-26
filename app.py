# import libs
import dash_table
import pandas as pd 
import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import plotly.graph_objs as go 



# get data

# authenticate and connect to the API
client_id = '8d4156b6c6b9410bbe7e3d6be1833219'
client_secret = 'e6b227a3b2a943e1a739bf84329df156'

client_credentials_manager = SpotifyClientCredentials(client_id, client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)



# init app
app = dash.Dash(__name__)



app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
         <title>Spotify Analysis</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
             {%renderer%} 
        </footer>
    </body>
</html>
'''

app.layout = html.Div( children = [

    html.H1(children = 'Spotify Analysis', style={'paddingLeft': 30,} ),

    html.Div(dcc.Input(id='input-box', type='text', placeholder=['Atrists Name'], value = ''), style={'paddingLeft': 30, 'width': '50%'},),

    dcc.Dropdown(id='album-names', placeholder =['Select a Album'],  value='',
                    style={'paddingLeft': 30, 'width': '50%'},),

    html.Div(id = 'table-id',children=[], style={'padding':'20px', 'margin':'10px'}),

    html.Div(id = 'charts', children=[]),



])

@app.callback(
    Output('album-names', 'options'),
    [Input('input-box', 'value')])
def get_albums(value):
    result = sp.search(value, type='artist')  # search query
    artist_id = result['artists']['items'][0]['id']
    sp_albums = sp.artist_albums(artist_id)
    album_names = []
    album_id = []
    for i in range(len(sp_albums)):
        album_names.append(sp_albums['items'][i]['name'])
        album_id.append(sp_albums['items'][i]['id'])
    album_dropdown = dict(zip(album_names, album_id))
    options=[{'label': i, 'value': j} for i,j in album_dropdown.items()]
    return options

# def copy_df(df):
#     global df_g
#     df_g = df.copy()

@app.callback(
    Output('table-id', 'children'),
    [Input('album-names', 'value')])
def update_layout(value):
    data = sp.album_tracks(value)['items']
    album = pd.DataFrame(data)
    songs_id = list(album.id)
    df = getTrackFeatures(songs_id)
    print(df.info())
    layout = []
    layout.append(dash_table.DataTable(id='table',
                                columns=[{"name": i, "id": i} for i in df.columns],
                                data=df.to_dict("rows"),
                                ))
    gfx = update_graphs(df)
    c = layout + gfx
    return c

# def get_df():
#     return df_g

# @app.callback(
#     Output('charts', 'children'),
#     [Input('album-names', 'value')])
def update_graphs(df):
    # data = sp.album_tracks(value)['items']
    # album = pd.DataFrame(data)
    # songs_id = list(album.id)
    # df = getTrackFeatures(songs_id)
    graphs = []
    df.drop(columns=['name', 'release_date'],inplace=True)
    for i in df.columns:
        graphs.append(
        dcc.Graph(id='graph_' + i,
                  figure={
                      'data': [
                          {'x': df[i], 'type':'histogram', 'histnorm':'probability', }
                      ],
                      'layout': go.Layout(
                          title=i,
                      )
                  }),
        )
    return graphs

def getTrackFeatures(song_id):
    df_list = []
    for i in song_id:
        meta = sp.track(i)
        features = sp.audio_features(i)

        # Meta
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']

        # Features
        key = features[0]['key']
        mode = features[0]['mode']
        acousticness = features[0]['acousticness']
        danceability = features[0]['danceability']
        energy = features[0]['energy']
        valence = features[0]['valence']
        instrumentalness = features[0]['instrumentalness']
        liveness = features[0]['liveness']
        loudness = features[0]['loudness']
        speechiness = features[0]['speechiness']
        tempo = features[0]['tempo']
        time_signature = features[0]['time_signature']
        df_list.append({
            'name': name,
            # 'album': album,
            # 'artist': artist,
            'release_date': release_date,
            'length': length,
            'popularity': popularity,
            'key': key,
            'mode': mode,
            'acousticness': acousticness,
            'danceability': danceability,
            'energy': energy,
            'valence': valence,
            'instrumentalness': instrumentalness,
            'liveness': liveness,
            'loudness': loudness,
            'speechiness': speechiness,
            'tempo': tempo,
            'time_signature': time_signature
        })

    df_features = pd.DataFrame(df_list,
                               columns=['name',
                                        # 'album',
                                        # 'artist',
                                        'release_date', 'length', 'popularity', 'key',
                                        'mode',
                                        'acousticness', 'danceability', 'energy', 'valence', 'instrumentalness',
                                        'liveness',
                                        'loudness', 'speechiness', 'tempo', 'time_signature'])
    return df_features


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)
