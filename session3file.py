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


# CloudWatch logs
# Latest temp get function
# Implement packet setup for nodered
# Alarms if values exceed the ranges
# Delete Day logs Function
# API key integration to make it more secure
# Adding call request limit ?
# Setup Device Temo Get Function, Securely and One Way
