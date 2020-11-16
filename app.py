import uuid
import boto3
from boto3.dynamodb.conditions import Key, Attr
from chalice import Chalice
from chalice import CORSConfig
from chalice import Response

app = Chalice(app_name='assignment_newsbytes')

cors_config = CORSConfig(
    allow_origin='*',
    allow_headers=['X-Special-Header', 'Authorization'],
    max_age=600,
    expose_headers=['X-Special-Header'],
    allow_credentials=True
)

SECRET_KEY = "4f58135e-2af4-4c48-8d70-9fdbba9b7f26"  # Generated using uuid

dynamodb = boto3.resource('dynamodb')
hashedUrlTable = dynamodb.Table('hashedUrlTable')


def make_response(status, data_type, msg, data, code):
    response = {'status': status, 'data_type': data_type, 'message': msg, "data": data, 'code': code}
    return response


@app.route('/', methods=['GET'])
def index():
    return "Hello World"


@app.route('/encodeurl', methods=['POST'], cors=cors_config)
def encodeURL():
    json_body = app.current_request.json_body
    url = json_body["url"]
    secret_hash = str(uuid.uuid4())
    body = {
        "token": secret_hash,
        "tokenURL": 'https://4utnah6h34.execute-api.ap-south-1.amazonaws.com/api/decodeurl?token=' + secret_hash,
        'actualURL': url,
        "clicks": 0
    }

    hashedUrlTable.put_item(
        Item=body
    )
    return Response(make_response("success", "object", "successfully encoded", body, 200))


@app.route('/decodeurl', methods=['GET'], cors=cors_config)
def decodeURL():
    query_params = app.current_request.query_params
    secret_hash = query_params['token']
    response = hashedUrlTable.get_item(Key={'token': secret_hash})
    if 'Item' in response:
        response['Item']['clicks'] += 1
        hashedUrlTable.put_item(
            Item=response['Item']
        )
    else:
        return Response(make_response("success", "object", "Requested resource was not found", {}, 404))
    return Response(status_code=301, body='', headers={'Location': response['Item']['actualURL']})


@app.route('/getinfo', methods=['GET'], cors=cors_config)
def getInfo():
    query_params = app.current_request.query_params
    secret_hash = query_params['token']
    response = hashedUrlTable.get_item(Key={'token': secret_hash})
    if 'Item' in response:
        body = response['Item']
    else:
        return Response(make_response("success", "object", "Requested resource was not found", {}, 404))
    return Response(make_response("success", "object", "successfully fetched", body, 200))
