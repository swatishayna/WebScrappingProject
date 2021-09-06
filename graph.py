import pandas as pd
from matplotlib.figure import Figure

def bar(session,table_name):
    query = "select * from "+table_name
    rows = session.execute(query)
    x = []
    [x.append(i[5]) for i in rows.all()]
    print(x)
    df_rating = pd.DataFrame(x, columns=['ratings'], dtype = 'float32')
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = df_rating['ratings']
    axis.scatter(xs)
    return fig





