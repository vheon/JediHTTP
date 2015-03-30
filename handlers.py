from flask import Flask, jsonify
import jedi

app = Flask( __name__ )
@app.route( '/healthy' )
def healthy():
    return jsonify()


@app.route( '/ready' )
def ready():
    return jsonify()
