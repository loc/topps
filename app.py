from flask import Flask, request, session

app = Flask(__name__)
app.config.from_object('config.db')

print app.config["USERNAME"]
