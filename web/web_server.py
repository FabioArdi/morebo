from flask import Flask, render_template

app = Flask(__name__)

# ###############################
# HTML Endpoints
# ###############################
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/movies")
def movies():
    return render_template("movies.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ###############################
# API Endpoints
# ###############################
@app.route("/api/?")
def do_sth():
    return "Endpoint not implemented!"


if __name__ == '__main__':
    app.run(debug=True)