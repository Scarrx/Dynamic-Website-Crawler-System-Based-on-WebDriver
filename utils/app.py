import json

from flask import Flask, request
from flask_cors import CORS

DEBUG = True
app = Flask(__name__)
cors = CORS(app)
receipt = {'recept': True, 'data': []}


@app.route('/', methods=['GET', 'POST'])
def get_anthing():

    data = json.loads(request.get_data())
    data['kind'] = 'element'
    if receipt['recept']:
        receipt['data'].append(data)
        # print(data['seleniumXpath'])
    return "yes"


print(app.url_map)

if __name__ == "__main__":
    app.run(ssl_context='adhoc')
