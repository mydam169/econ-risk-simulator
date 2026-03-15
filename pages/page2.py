from dash import html, dcc, Input, Output, callback
import dash

dash.register_page(__name__,
                   path='/page-2',
                   name='Portfolio Choice',
                   title='Page 2')

layout = html.Div([
    html.H1("Portfolio Choice", className="mt-4"),
    html.P("To be buiilt"),
    ])