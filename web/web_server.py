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


# ###############################
# Error Handler
# ###############################
@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html') # redirect to index.html

if __name__ == '__main__':
    app.run(debug=True)