import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YourDynamoDBTableName')  # Replace 'YourDynamoDBTableName' with your table name

def put_data_in_dynamodb(event):
    timestamp = event.get('timestamp')
    temperature = event.get('temperature')
    probe_number = event.get('probe_number')

    # Convert Unix timestamp to a human-readable date and time
    dt_object = datetime.fromtimestamp(timestamp)
    date_string = dt_object.strftime('%Y-%m-%d')  # Extracting date in 'YYYY-MM-DD' format
    time_string = dt_object.strftime('%H:%M:%S')  # Extracting time in 'HH:MM:SS' format

    # Prepare item to be stored in DynamoDB
    item = {
        'Date': date_string,
        'Timestamp': str(timestamp),
        'Time': time_string,
        'Temperature': temperature,
        'ProbeNumber': probe_number
    }

    # Put item into DynamoDB table
    try:
        table.put_item(Item=item)
        return {
            'statusCode': 200,
            'body': 'Data successfully stored in DynamoDB.'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error storing data in DynamoDB: {e}"
        }

def get_latest_data():
    try:
        response = table.scan(
            Limit=1,
            ScanIndexForward=False,  # Sort in descending order of Timestamp
            ProjectionExpression="Temperature, Timestamp"  # Select only required attributes
        )
        
        if 'Items' in response and len(response['Items']) > 0:
            item = response['Items'][0]
            return {
                'statusCode': 200,
                'body': {
                    'Temperature': item['Temperature'],
                    'Timestamp': item['Timestamp']
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': 'No data available.'
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error fetching data from DynamoDB: {e}"
        }

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'PUT':
        return put_data_in_dynamodb(event)
    elif http_method == 'GET':
        return get_latest_data()
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid HTTP method.'
        }
