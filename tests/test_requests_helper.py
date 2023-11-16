import pytest
from unittest.mock import Mock
from tools.requests_helper import check_for_error_code, json_from_response


class TestResponseFunctions:
    """Class to test response handling functions."""

    def test_check_for_error_code_with_200(self):
        """Test check_for_error_code function with a status code of 200 (OK)."""
        mock_response = Mock()
        mock_response.status_code = 200
        # No exception should be raised for a 200 status code
        try:
            check_for_error_code(mock_response)
        except Exception:
            pytest.fail("Unexpected Exception raised.")

    def test_check_for_error_code_with_non_200(self):
        """Test check_for_error_code function with a non-200 status code."""
        mock_response = Mock()
        mock_response.status_code = 404
        with pytest.raises(Exception) as e_info:
            check_for_error_code(mock_response)
        assert "Could not evaluate status code." in str(e_info.value)

    def test_json_from_response_with_valid_json(self):
        """Test json_from_response function with a valid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        expected_json = {"key": "value"}
        mock_response.json.return_value = expected_json
        result = json_from_response(mock_response)
        assert result == expected_json

    def test_json_from_response_with_invalid_json(self):
        """Test json_from_response function with a response that doesn't contain valid JSON."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")
        with pytest.raises(Exception) as e_info:
            json_from_response(mock_response)
        assert "Could not retrieve JSON from response." in str(e_info.value)

    def test_json_from_response_with_non_200_status(self):
        """Test json_from_response function with a non-200 status code."""
        mock_response = Mock()
        mock_response.status_code = 404
        with pytest.raises(Exception) as e_info:
            json_from_response(mock_response)
        assert "Could not evaluate status code." in str(e_info.value)

