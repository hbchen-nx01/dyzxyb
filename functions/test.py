import json

def handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Netlify function is working!"}),
        "headers": {
            "Content-Type": "application/json"
        }
    }