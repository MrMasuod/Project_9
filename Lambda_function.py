import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YourDynamoDBTableName')  # Replace 'YourDynamoDBTableName' with your table name

def put_data_in_dynamodb(event):
    # Parse JSON input containing timestamp, temperature value, and probe number
    timestamp = event.get('timestamp')
    temperature = event.get('temperature')
    probe_number = event.get('probe_number')

    # Convert Unix timestamp to a human-readable date and time
    dt_object = datetime.fromtimestamp(timestamp)
    date_string = dt_object.strftime('%Y-%m-%d')  # Extracting date in 'YYYY-MM-DD' format
    
    # Prepare item to be stored in DynamoDB
    item = {
        'Date': date_string,
        'Timestamp': str(timestamp),  # Convert timestamp to string for DynamoDB
        'Temperature': temperature,
        'ProbeNumber': probe_number
    }
    try:
        table.put_item(Item=item)
        print("Data successfully stored in DynamoDB.")
    except Exception as e:
        print(f"Error storing data in DynamoDB: {e}")
    return {
        'statusCode': 200,
        'body': 'Data processed and stored in DynamoDB.'
    }
    
def get_full_day_average(date):
    # Get all items for the specified date
    response = table.query(
        KeyConditionExpression=Key('Date').eq(date)
    )
    
    temperature_sum = 0
    count = 0
    for item in response['Items']:
        temperature_sum += item['Temperature']
        count += 1
    
    if count == 0:
        return None
    
    return temperature_sum / count

def get_last_hour_average():
    # Get timestamp of one hour ago
    one_hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp())
    
    # Query items within the last hour
    response = table.query(
        KeyConditionExpression=Key('Timestamp').gte(str(one_hour_ago))
    )
    
    temperature_sum = 0
    count = 0
    for item in response['Items']:
        temperature_sum += item['Temperature']
        count += 1
    
    if count == 0:
        return None
    
    return temperature_sum / count

def get_last_saved_temp():
    # Query the latest item
    response = table.scan(
        Limit=1,
        ScanIndexForward=False
    )
    
    if 'Items' in response and len(response['Items']) > 0:
        item = response['Items'][0]
        return {
            'Temperature': item['Temperature'],
            'Timestamp': item['Timestamp']
        }
    else:
        return None

def delete_data_for_date(date):
    # Get all items for the specified date
    response = table.query(
        KeyConditionExpression=Key('Date').eq(date)
    )
    
    # Delete each item for the specified date
    for item in response['Items']:
        table.delete_item(
            Key={
                'Date': item['Date'],
                'Timestamp': item['Timestamp']
            }
        )
    
    return "Data for date {} deleted.".format(date)

def lambda_handler(event, context):
    action = event.get('action')
    
    if action == 'put_data':
        # Perform action to put data in DynamoDB
        put_data_in_dynamodb(event)
        return {
            'statusCode': 200,
            'body': 'Data successfully stored in DynamoDB.'
        }
    elif action == 'get_full_day_average':
        # Fetch full day average
        full_day_avg = get_full_day_average(event.get('date'))  # Provide 'date' in the event payload
        if full_day_avg is not None:
            return {
                'statusCode': 200,
                'body': {
                    'full_day_avg': full_day_avg
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': 'Data not found for the specified date.'
            }
    elif action == 'get_last_hour_average':
        # Fetch last hour average
        last_hour_avg = get_last_hour_average()
        if last_hour_avg is not None:
            return {
                'statusCode': 200,
                'body': {
                    'last_hour_avg': last_hour_avg
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': 'No data available for the last hour.'
            }
    elif action == 'get_last_saved_temp':
        # Fetch last saved temperature
        last_saved_temp = get_last_saved_temp()
        if last_saved_temp is not None:
            return {
                'statusCode': 200,
                'body': {
                    'last_saved_temp': last_saved_temp
                }
            }
        else:
            return {
                'statusCode': 404,
                'body': 'No data available.'
            }
    elif action == 'delete_data_for_date':
        # Delete data for a specific date
        delete_result = delete_data_for_date(event.get('date'))  # Provide 'date' in the event payload
        return {
            'statusCode': 200,
            'body': delete_result
        }
    else:
        return {
            'statusCode': 400,
            'body': 'Invalid action specified.'
        }
