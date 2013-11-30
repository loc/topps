from flask import Flask

app = Flask(__name__)
app.config.from_object('topps.config.db_app')

scraper = Flask(__name__)
scraper.config.from_object('topps.config.db_scraper')

import topps.views