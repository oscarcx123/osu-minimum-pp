import time
import random
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s %(levelname)s %(message)s',
    datefmt = '%Y-%m-%dT%H:%M:%S')

def random_sleep():
    seconds = random.randint(1, 3)
    logging.info(f"[Info] Sleep for {seconds}s")
    time.sleep(seconds)

# https://stackoverflow.com/questions/5914627/prepend-line-to-beginning-of-a-file
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)

# get pp information 
def get_pp_info():
    mode_name = ["osu", "taiko", "fruits", "mania"]

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    date = datetime.today().strftime('%Y-%m-%d')

    df = pd.read_csv("pp_data.csv")
    if len(df.index) > 0 and df["Date"].iloc[-1] == date:
        return False

    result = [date]


    for i in range(0, 4):
        random_sleep()
        logging.info(f"Getting pp for {mode_name[i]} #9,999")
        url = f"https://osu.ppy.sh/rankings/{mode_name[i]}/performance"
        payload = {"page": "200"}
        r = requests.get(url=url, params=payload, headers=headers)
        if r.status_code != 200:
            raise requests.exceptions.HTTPError("The response code is not 200. Something's wrong!")
        webdata = r.text
        soup = BeautifulSoup(webdata,"lxml")
        pp = soup.find_all("td", class_ = "ranking-page-table__column")[-4].text.replace(" ", "").replace("\n", "").replace(",", "")
        logging.info(f"pp = {pp}")
        result.append(pp)

    for i in range(0, 4):
        random_sleep()
        logging.info(f"Getting pp for {mode_name[i]} #999")
        url = f"https://osu.ppy.sh/rankings/{mode_name[i]}/performance"
        payload = {"page": "20"}
        r = requests.get(url=url, params=payload, headers=headers)
        if r.status_code != 200:
            raise requests.exceptions.HTTPError("The response code is not 200. Something's wrong!")
        webdata = r.text
        soup = BeautifulSoup(webdata,"lxml")
        pp = soup.find_all("td", class_ = "ranking-page-table__column")[-4].text.replace(" ", "").replace("\n", "").replace(",", "")
        logging.info(f"pp = {pp}")
        result.append(pp)

    res_str = ",".join(result)

    with open("pp_data.csv", "a") as f:
        f.write('\n')
        f.write(res_str)
    
    logging.info("get_pp_info done!")
    return True

def generate_chart():
    logging.info("Generating interactive chart...")

    # Load data
    df = pd.read_csv("pp_data.csv")


    # Create figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Standard4), name="Standard4", visible="legendonly"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Taiko4), name="Taiko4", visible="legendonly"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.CtB4), name="CtB4", visible="legendonly"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Mania4), name="Mania4"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Standard3), name="Standard3", visible="legendonly"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Taiko3), name="Taiko3", visible="legendonly"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.CtB3), name="CtB3", visible="legendonly"))
    fig.add_trace(go.Scatter(x=list(df.Date), y=list(df.Mania3), name="Mania3", visible="legendonly"))

    # Set title
    fig.update_layout(title_text="osu! 4&3-digit rank minimum pp requirement")

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