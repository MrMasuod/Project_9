const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient();
const tableName = 'YourDynamoDBTableName'; // Replace 'YourDynamoDBTableName' with your table name

function putDataInDynamoDB(event) {
  if (event.resource === '/log_temp' && event.httpMethod === 'PUT') {
    const requestBody = JSON.parse(event.body);

    const timestamp = requestBody.timestamp;
    const temperature = requestBody.temperature;
    const probeNumber = requestBody.probe_number;

    const dtObject = new Date(timestamp * 1000);
    const dateString = dtObject.toISOString().slice(0, 10);
    const timeString = dtObject.toTimeString().slice(0, 8);

    const item = {
      'Date': dateString,
      'Timestamp': timestamp.toString(),
      'Time': timeString,
      'Temperature': temperature,
      'ProbeNumber': probeNumber
    };

    const params = {
      TableName: tableName,
      Item: item
    };

    return dynamodb.put(params).promise()
      .then(() => {
        return {
          statusCode: 200,
          body: 'Data successfully stored in DynamoDB.'
        };
      })
      .catch((error) => {
        return {
          statusCode: 500,
          body: `Error storing data in DynamoDB: ${error}`
        };
      });
  } else {
    return {
      statusCode: 404,
      body: 'Resource not found or incorrect HTTP method.'
    };
  }
}

function getAPITestStatus(event) {
  if (event.resource === '/api_test' && event.httpMethod === 'GET') {
    return {
      statusCode: 200,
      body: 'API is working.'
    };
  } else {
    return {
      statusCode: 404,
      body: 'Resource not found or incorrect HTTP method.'
    };
  }
}

function getLatestTemperature(event) {
  if (event.resource === '/get_latest_temp' && event.httpMethod === 'GET') {
    const params = {
      TableName: tableName,
      Limit: 1,
      ScanIndexForward: false,
      ProjectionExpression: 'Temperature, Timestamp'
    };

    return dynamodb.scan(params).promise()
      .then((data) => {
        if (data.Items && data.Items.length > 0) {
          const item = data.Items[0];
          return {
            statusCode: 200,
            body: {
              'Temperature': item.Temperature,
              'Timestamp': item.Timestamp
            }
          };
        } else {
          return {
            statusCode: 404,
            body: 'No data available.'
          };
        }
      })
      .catch((error) => {
        return {
          statusCode: 500,
          body: `Error fetching data from DynamoDB: ${error}`
        };
      });
  } else {
    return {
      statusCode: 404,
      body: 'Resource not found or incorrect HTTP method.'
    };
  }
}

exports.handler = async (event) => {
  const resourcePath = event.resource;
  const httpMethod = event.httpMethod;

  if (httpMethod === 'PUT') {
    return putDataInDynamoDB(event);
  } else if (resourcePath === '/api_test' && httpMethod === 'GET') {
    return getAPITestStatus(event);
  } else if (resourcePath === '/get_latest_temp' && httpMethod === 'GET') {
    return getLatestTemperature(event);
  } else {
    return {
      statusCode: 400,
      body: 'Invalid HTTP method or resource path.'
    };
  }
};
