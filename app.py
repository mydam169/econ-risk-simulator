from dash import Dash, html, page_container, page_registry
import dash_bootstrap_components as dbc

app = Dash(
    __name__,
    use_pages=True,
    suppress_callback_exceptions=True
)

app.title = "Risk Explorer – Decision Making Under Risk"

# Top navigation
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page["name"], href=page["relative_path"]))
        for page in page_registry.values()
        if page["module"] != "pages.not_found_404"     # hide 404 from nav
    ],
    brand="Home",
    brand_href="/",
    color="light",
    dark=False,
    className="mb-4",
)

app.layout = html.Div([
    navbar,
    # This container automatically shows the active page
    page_container,
])


if __name__ == "__main__":
    app.run(debug=True, port=8050)