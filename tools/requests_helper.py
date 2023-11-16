def check_for_error_code(response):
    """
    Checks the status code of a response object.

    This function examines the status code of the given response. If the status code is not 200 (OK),
    it raises an exception. If the status code cannot be evaluated for any reason, a different
    exception is raised indicating that the status code could not be evaluated.

    Args:
        response: A response object, typically from a request, which should contain a 'status_code' attribute.

    Raises:
        Exception: If the status code is not 200 or if the status code cannot be evaluated.
    """
    try:
        status_code = response.status_code
        if status_code != 200:
            raise Exception(f"Status code is {status_code}")
    except Exception as e:
        raise Exception('Could not evaluate status code.')


def json_from_response(response):
    """
    Extracts JSON from a response object after checking its status code.

    This function first calls 'check_for_error_code' to ensure that the response has a 200 status code.
    Then, it attempts to parse and return the JSON content from the response. If the response does not
    contain valid JSON or if the status code check fails, an exception is raised.

    Args:
        response: A response object, typically from a request, which should contain a 'json' method and a 'status_code' attribute.

    Returns:
        The parsed JSON content of the response, if available.

    Raises:
        Exception: If the response does not contain valid JSON or if the status code is not 200.
    """
    check_for_error_code(response)
    try:
        return response.json()
    except Exception as e:
        raise Exception('Could not retrieve JSON from response.')
