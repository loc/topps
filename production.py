from topps import app

app.config.from_object('topps.config.app')

app.run(host="127.0.0.1", port=5000)