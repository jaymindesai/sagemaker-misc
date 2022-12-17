from flask import Flask, Response, request
import json
import en_core_web_sm
import logging

# Load model
_nlp_model = en_core_web_sm.load()

# The flask app for serving predictions
app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping():
    """
    Implements the health check
    """
    status = 200 if _nlp_model is not None else 503
    return Response(status=status)


@app.route('/invocations', methods=['POST'])
def invoke():
    """
    Implements the invoke/transform endpoint that performs inference
    """
    try:
        logging.debug("Invocation request received")
        input_json = request.get_json()
        input_data = input_json['input']
        doc = _nlp_model(input_data)
        entities = [(entity.text, entity.label_) for entity in doc.ents]
        response_json = json.dumps({
            'output': entities
        })
        return Response(response=response_json, status=200, mimetype='application/json')
    except Exception as e:
        logging.error("Error occurred: {}".format(e))
        return Response(status=500)
