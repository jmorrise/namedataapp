import logging
import numpy as np
from src.bigquery import test_queries

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/query')
def query():
    default_names = ["George", "Ronald", "Lyndon", "William", "John"]
    names = request.args.getlist("name") or default_names
    names = [n.capitalize() for n in names]
    years, logps = test_queries.get_log_probs(names)
    probs = np.exp(logps)
    query_data = list(zip([str(y) for y in years], probs/np.sum(probs)))
    title = ", ".join(names)
    return render_template(
        'query.html', names=names, title=title,query_data=query_data)

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
