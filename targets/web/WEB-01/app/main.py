from flask import Flask

app = Flask(__name__)


@app.get("/")
def index():
    return """
    <!doctype html>
    <html>
    <head>
        <title>NightBreach WEB-01</title>
    </head>
    <body>
        <h1>NightBreach Web Server</h1>
        <p>Welcome to the WEB-01 practice target.</p>
    </body>
    </html>
    """


@app.get("/robots.txt")
def robots():
    return """
    User-agent: *
    Disallow: /internal/
    """


@app.get("/internal/")
def internal():
    return """
    <!doctype html>
    <html>
    <head>
        <title>Internal</title>
    </head>
    <body>
        <h1>Internal Area</h1>
        <p>WEB-01 discovery successful.</p>
    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
