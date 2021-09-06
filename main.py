import crochet
crochet.setup()
from flask import Flask , render_template, jsonify, request, redirect, url_for,Response
from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.signalmanager import dispatcher
import time
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from webscrap.webscrap.spiders.flipspider import ReviewspiderSpider
from writedata import write
import graph
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

app = Flask(__name__)

output_data = []
crawl_runner = CrawlerRunner()

# By Deafult Flask will come into this when we run the file
@app.route('/')
def index():
	return render_template("index.html")


@app.route('/', methods=['POST'])
def submit():
    if request.method == 'POST':
        s = request.form['url']  # Getting the Input Amazon Product URL
        page_number = int(request.form['page'])

        global baseURL
        baseURL = s
        global expected_pageno
        expected_pageno = page_number
        print(expected_pageno)

        # This will remove any existing file with the same name
        if os.path.exists("D:/data science/ineuron/Project/python project/projectscrapping/webscrap/reviews.json"):
            os.remove("D:/data science/ineuron/Project/python project/projectscrapping/webscrap/reviews.json")


        return redirect(url_for('scrape'),)  # Passing to the Scrape function


@app.route("/scrape")
def scrape():
    global baseURL
    global output_data

    secure_connect_bundlezip = 'D:\data science\ineuron\Databases\Cassandra\secure-connect-scrappingdata.zip'
    client_id = 'xzwnPGxiZZZdvZHEGQeUjxEM'
    client_Secret = 'Iwr4DW-qeDFYgf,x1BtjHufBMgZE59r7pbHHeIvHPRx0p_h3OHLsssxDTU3_L_yK4DF0bouiFg0.2vxr.Z,1Dp3i5Kx2xZ4p7qqvINt,sJEco0fgMkRrZ7UaCf7-x2N2'
    keyspace = "flipkart"
    table_name = baseURL.split("/")[3][:5]
    def connect(secure_connect_bundlezip, client_id, client_Secret):
        cloud_config = {
            'secure_connect_bundle': secure_connect_bundlezip
        }
        auth_provider = PlainTextAuthProvider(client_id, client_Secret)
        cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
        global session
        session = cluster.connect()
        print(session)

    connect(secure_connect_bundlezip, client_id, client_Secret)

    # use exiting database database
    def connect_db():
        query = "USE flipkart"
        session.execute(query)

    connect_db()

    table_info =  session.execute("select table_name  from system_schema.tables where keyspace_name = 'flipkart'")
    tablelist = []
    [tablelist.append(i.table_name) for i in table_info.all()]

    if table_name not in tablelist:
        scrape_with_crochet(baseURL=baseURL)
        time.sleep(10)
        session.execute("""CREATE TABLE {z} (id int primary key,name TEXT,rating TEXT,heading TEXT,date TEXT,area TEXT,type TEXT)""".format(z = table_name))
        for x in output_data:
            data = []
            for i in x.values():
                if type(i) == list:
                    data.extend(i)
                else:
                    data.append(i)
            query = "INSERT INTO {} (id ,name,rating ,heading,date,area,type)VALUES(%s,%s,%s,%s,%s,%s,%s)".format(table_name)
            session.execute(query, data)
        # write data to csv
        write(output_data)

        print("Records updated in Cassandra")
    else:
        rows = session.execute("""SELECT * from {s}""".format(s = table_name))
        if len(rows.all()) < expected_pageno * 10:
            scrape_with_crochet(baseURL=baseURL)
            time.sleep(10)
            try:
                for x in output_data[len(rows.all())+1 : (expected_pageno * 10)]:
                    data = []
                    for i in x.values():
                        if type(i) == list:
                            data.extend(i)
                        else:
                            data.append(i)
                    query = "INSERT INTO {} (id ,name,rating ,heading,date,area,type)VALUES(%s,%s,%s,%s,%s,%s,%s)".format(
                        table_name)
                    session.execute(query, data)
            except:
                print('Error Occurred')
        # write data to csv
        write(output_data)
        rows = session.execute("""SELECT * from {s}""".format(s=table_name))
        [output_data.append(i) for i in rows.all()]
        print("Records Fetched successfully")


    return jsonify(output_data)



@crochet.run_in_reactor
def scrape_with_crochet(baseURL):

    dispatcher.connect(_crawler_result, signal=signals.item_scraped)
    eventual = crawl_runner.crawl(ReviewspiderSpider, category=baseURL,expected_pageno = expected_pageno)
    return eventual



def _crawler_result(item, response, spider):
    output_data.append(dict(item))


# @app.route("/graph", methods=['GET'])
# def graph():
#     return redirect(url_for('plot_png'))
#
#
# @app.route('/a', methods=['GET'])
# def plot_png():
#     fig = graph.bar()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')




if __name__ == "__main__":
    app.run(debug=True)