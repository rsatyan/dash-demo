import dash_html_components as html
import dash_core_components as dcc


def Header(app):
    return html.Div([get_menu()])


def get_menu():
    menu = html.Div([
            dcc.Link(
                'Overview',
                href="/overview.py",
                className="tab first"
            ),
            dcc.Link(
                'Banking (Corporate)',
                href="/corporate_bank.py",
                className="tab"
            ),
            dcc.Link(
                'Banking (IBD)',
                href="/ibd_bank.py",
                className="tab"
            ),
            dcc.Link(
                'Business Banking',
                href="/business_bank.py",
                className="tab"
            ),
            dcc.Link(
                'Consumer Banking & Payments',
                href="/cbp.py",
                className="tab"
            ),
            dcc.Link(
                'BUK',
                href="/buk.py",
                className="tab"
            ),
        ],
        className="row all-tab"
    )

    return menu

def make_dash_table(df):
    table = []
    for index, row in df.iterrows():
        html_row=[]
        for i in range(len(row)):
            html_row.append(html.Td([row[i]]))
        table.append(html.Tr(html_row))
    return table