import json
from concurrent.futures import ThreadPoolExecutor
from tools.langchain_helper import entry_point, daily_synopsis


def lambda_handler(event, context):
    try:
        # Check if event is a string and convert it to a dictionary
        if isinstance(event, str):
            event = json.loads(event)

        # Extract parameters from the event argument
        temperature = event.get('temperature', 1)  # Default value is 0.25 if not provided
        model = event.get('model', 'gpt-4-1106-preview')  # Default model if not provided
        verbose = event.get('verbose', True)  # Default to False if not provided
        # gpt_daily_synopsis = entry_point(temperature=temperature, model=model, verbose=verbose)

        # gpt_daily_synopsis = daily_synopsis(temperature=temperature, model=model, verbose=verbose)
        # Run Playwright in a separate thread
        # Using ThreadPoolExecutor to run the function in a separate thread and get the result
        with ThreadPoolExecutor() as executor:
            future = executor.submit(daily_synopsis, temperature, model, verbose)
            gpt_daily_synopsis = future.result()  # This will wait until the function is finished and return its result

        return {
            'statusCode': 200,
            'body': json.dumps({'results': gpt_daily_synopsis})
        }

    except Exception as e:
        # Handle any exceptions that occurred during processing
        print(e)  # Logging the exception can be helpful for debugging
        raise Exception("Daily Synopsis Error: Status Code 500")
        # # Return an error response
        # return {
        #     'statusCode': 500,
        #     'body': json.dumps({'error': str(e)})
        # }


if __name__ == '__main__':
    response = lambda_handler({}, {})
    print(response)

