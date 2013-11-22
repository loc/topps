from flask import Flask
app = Flask(__name__)

app.config.from_object('topps.config.db')

import topps.views