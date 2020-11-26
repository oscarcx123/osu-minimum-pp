import time
import random
import requests
import logging
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(message)s',
    datefmt = '%Y-%m-%dT%H:%M:%S')

def random_sleep():
    seconds = random.randint(1, 2)
    logging.info(f"[Info] Sleep for {seconds}s")
    time.sleep(seconds)

# https://stackoverflow.com/questions/5914627/prepend-line-to-beginning-of-a-file
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

# get pp information from https://osudaily.net/ppbrowser.php
def get_pp_info():
    mode_name = ["Standard", "Taiko", "CtB", "Mania"]

    url = "https://osudaily.net/data/getPPRank.php"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    result = [datetime.today().strftime('%Y-%m-%d')]


    for i in range(0, 4):
        random_sleep()
        logging.info(f"Getting pp for {mode_name[i]}")
        payload = {"t": "rank", "v": "9999", "m": str(i)}
        r = requests.get(url=url, params=payload, headers=headers)
        if r.status_code != 200:
            raise requests.exceptions.HTTPError("The response code is not 200. Something's wrong!")
        result.append(r.text)

    res_str = ",".join(result)

    with open("pp_data.csv", "a") as f:
        f.write('\n')
        f.write(res_str)
    
    logging.info("get_pp_info done!")

def generate_chart():
    logging.info("Generating interactive chart...")

    # Load data
    df = pd.read_csv("pp_data.csv")


    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Standard), name="Standard"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Taiko), name="Taiko"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.CtB), name="CtB"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Mania), name="Mania"))

    # Set title
    fig.update_layout(title_text="osu! 4-digit rank minimum pp requirement")

    # Add range slider
    # https://plotly.com/python/range-slider/
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                    dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                    dict(count=1,
                        label="YTD",
                        step="year",
                        stepmode="todate"),
                    dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    fig.write_html(file="index.html", include_plotlyjs=False)

    # use cdn instead of including the js library
    line_prepender("index.html", "<script src=\"https://cdn.plot.ly/plotly-latest.min.js\"></script>")

    logging.info("generate_chart done!")

get_pp_info()
generate_chart()