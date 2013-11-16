from topps import app

app.config.from_object('topps.config.db')
app.config.from_object('topps.config.app')

app.run(debug=True)