import pandas as pd
import time
from flask import Flask, request, jsonify, Response
import matplotlib.pyplot as plt
import re
import io


app = Flask(__name__)
df = pd.read_csv("main.csv")
count = 0
visitA = 0
visitB = 0

@app.route('/')
def home():
    with open("index.html") as f:
        html = f.read()
    with open("index2.html") as f:
        html2 = f.read()
    global count
    global visitA
    global visitB
    count += 1
    if count <= 10:
        if count%2 == 0:
            return html
        else:
            return html2
    else: 
        if visitA > visitB:
            return html
        else:
            return html2
    
@app.route('/browse.html')
def hi_handler():
    global df
    title = "<h1>dataset</h1>"
    return title + df.to_html()

@app.route('/donate.html')
def donate():
    try:
        var = request.args['form']
        if var == "A":
            global visitA
            visitA += 1
        if var == "B":
            global visitB
            visitB += 1
        return "<h1>hi</h1>"
    except:
        return "<h1>hello</h1>"

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^[a-z0-9]+@[a-z]+\.[a-z]{2,3}$", email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        with open("emails.txt", "r") as f:
            num_subscribed = len(f.readlines())
        return jsonify(f"thanks, you're subscriber number {num_subscribed}!")
    return jsonify("Please provide valid email address") # 3

visit = {}
visit_ip = []
@app.route('/browse.json')
def slow():
    global visit
    global df
    global visit_ip
    visit_ip.append(request.remote_addr)
    if request.remote_addr not in visit:
        visit[request.remote_addr] = time.time()
        return jsonify(df.to_dict('index'))
    else:
        visit_time = time.time()
        if visit_time - visit[request.remote_addr] > 60:
            visit[request.remote_addr] = visit_time
            return jsonify(df.to_dict('index'))
        else:
            return Response("Please Come Back After 1 Minute", status = 429, headers = {'Retry-After':'60'})

@app.route('/visitors.json')
def visitor():
    global visit_ip
    return jsonify(visit_ip)


@app.route('/dashboard_1.svg')
def dashboard_1():
    # create the plot
    if not request.args.get("bins", default="", type=str)=="100":
        fig, ax = plt.subplots(figsize=(3,2))
        points = pd.Series(sorted(df['PTS']))
        points.plot.line(ax=ax, ylim=0, drawstyle="steps-post")
        ax.set_ylabel("Points")
        plt.tight_layout()
        # send it back
        f = io.StringIO() # FAKE TEXT FILE
        fig.savefig(f, format="svg")
        plt.close() # just closes the most recent fig
        return Response(f.getvalue(),
                            headers={"Content-Type": "image/svg+xml"})

    # create the plot
    else:
        fig, ax = plt.subplots(figsize=(3,2))
        age = pd.Series(sorted(df['Age']))
        age.plot.hist(ax=ax,bins=100)
        ax.set_ylabel("Age")
        plt.tight_layout()
        # send it back
        f = io.StringIO() # FAKE TEXT FILE
        fig.savefig(f, format="svg")
        plt.close() # just closes the most recent fig
        return Response(f.getvalue(),
                            headers={"Content-Type": "image/svg+xml"})

@app.route('/dashboard_2.svg')
def dashboard_2():
    # pd.Series().plot.scatter
    fig, ax = plt.subplots(figsize=(3,2))
    # assist = pd.Series(df['AST'])

    # assist = assist.reset_index()

    df.plot.scatter(x='PTS', y='AST', ax=ax,ylim=0)
    ax.set_ylabel("Assist Time")
    plt.tight_layout()
    # send it back
    f = io.StringIO() # FAKE TEXT FILE
    fig.savefig(f, format="svg")
    plt.close() # just closes the most recent fig
    return Response(f.getvalue(),
                          headers={"Content-Type": "image/svg+xml"})




if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
