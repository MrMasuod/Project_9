import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YourDynamoDBTableName')  # Replace 'YourDynamoDBTableName' with your table name

def put_data_in_dynamodb(event):
    if event['resource'] == '/log_temp' and event['httpMethod'] == 'PUT':
        # Extracting data from the PUT request body
        request_body = event['body']
        # Parse request_body and extract required attributes (e.g., timestamp, temperature, probe_number)
        
        # Example: Extracting timestamp, temperature, and probe_number from JSON payload
        timestamp = request_body.get('timestamp')
        temperature = request_body.get('temperature')
        probe_number = request_body.get('probe_number')

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
    else:
        return {
            'statusCode': 404,
            'body': 'Resource not found or incorrect HTTP method.'
        }

def get_api_test_status(event):
    if event['resource'] == '/api_test' and event['httpMethod'] == 'GET':
        # Respond with a message indicating the API is working
        return {
            'statusCode': 200,
            'body': 'API is working.'
        }
    else:
        return {
            'statusCode': 404,
            'body': 'Resource not found or incorrect HTTP method.'
        }

def get_latest_temperature(event):
    if event['resource'] == '/get_latest_temp' and event['httpMethod'] == 'GET':
        try:
            response = table.scan(
                Limit=1,
                ScanIndexForward=False,
                ProjectionExpression="Temperature, Timestamp"
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
    else:
        return {
            'statusCode': 404,
            'body': 'Resource not found or incorrect HTTP method.'
        }

def lambda_handler(event, context):
    resource_path = event.get('resource')
    http_method = event.get('httpMethod')
    
    if http_method == 'PUT':
        return put_data_in_dynamodb(event)
    elif resource_path == '/api_test' and http_method == 'GET':
        return get_api_test_status(event)
    elif resource_path == '/get_latest_temp' and http_method == 'GET':
        return get_latest_temperature(event)
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid HTTP method or resource path.'
        }
