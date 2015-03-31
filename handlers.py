from flask import Flask, jsonify, request
import jedi

app = Flask( __name__ )
@app.route( '/healthy' )
def healthy():
    return jsonify()


@app.route( '/ready' )
def ready():
    return jsonify()


@app.route( '/completion', methods=['POST'] )
def completion():
    script = _GetJediScript( request.get_json() )
    return jsonify( {
        'completions': [
            {
                'name':        completion.name,
                'description': completion.description,
                'docstring':   completion.docstring()
            } for completion in script.completions() ]
        } )


def _GetJediScript( request_data ):
    filename = request_data[ 'filepath' ]
    contents = request_data[ 'contents' ]
    line     = request_data[ 'line_num' ]
    column   = request_data[ 'column_num' ]

    return jedi.Script( contents, line, column, filename )
