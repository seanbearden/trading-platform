def check_for_error_code(response):
    try:
        status_code = response.status_code
        if status_code != 200:
            raise Exception(f"Status code is {status_code}")
    except Exception as e:
        raise Exception('Could not evaluate status code.')


def json_from_response(response):
    check_for_error_code(response)
    try:
        return response.json()
    except Exception as e:
        raise Exception('Could not retrieve JSON from response.')
