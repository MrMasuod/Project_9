import json
def lambda_handler(event, context):
  timestamp = json.loads(event['body'])['timestamp]
  probe_number = json.loads(event['body'])['probe_number]
  temperature = json.loads(event['body'])['temperature]

  dt_object = datetime.fromtimestamp(timestamp)
  date_string = dt_object.strftime('%Y-%m-%d')  # Extracting date in 'YYYY-MM-DD' format
  time_string = dt_object.strftime('%H:%M:%S')  # Extracting time in 'HH:MM:SS' format
  # Prepare item to be stored in DynamoDB
  item = {
    'probe': probe_number
    'timestamp': str(timestamp),
    'Time': time_string,
    'Temperature': temperature,
     'Date': date_string
    }

def get_latest_temperature(event):
    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('Dixell_Temp_2')
        
        probes = set()  # Set to store unique probe values
        response = table.scan(
            ProjectionExpression="#pk",
            ExpressionAttributeNames={"#pk": "probe"},
        )

        for item in response['Items']:
            probes.add(item['probe'])

        latest_items = {}
        for probe in probes:
            response = table.query(
                Limit=1,
                ScanIndexForward=False,
                TableName='Dixell_Temp_"',
                KeyConditionExpression="#pk = :pkval",
                ExpressionAttributeNames={"#pk": "probe"},
                ExpressionAttributeValues={":pkval": probe},
            )

            if 'Items' in response and len(response['Items']) > 0:
                latest_items[probe] = response['Items'][0]

        return {
            'statusCode': 200,
            'body': latest_items
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error fetching data from DynamoDB: {e}"
        }


# CloudWatch logs
# Latest temp get function
# Implement packet setup for nodered
# Alarms if values exceed the ranges
# Delete Day logs Function
# API key integration to make it more secure
# Adding call request limit ?
# Setup Device Temo Get Function, Securely and One Way
