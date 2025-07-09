import unittest
from unittest.mock import patch, MagicMock
from update_alert_rest import process_alert, _update_custom_fields

class TestUpdateAlertRest(unittest.TestCase):

    @patch('update_alert_rest.requests.Session')
    def test_process_alert_success(self, mock_session):
        # Mock session and response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "customFields": [
                {"identifier": "Mispar_tkina", "value": ""},
                {"identifier": "Mispar_divuah", "value": ""},
                {"identifier": "status_divuah", "value": ""}
            ]
        }
        mock_session.return_value.get.return_value = mock_response
        mock_session.return_value.post.return_value = MagicMock(status_code=200)

        # Input data
        report_data = {
            "alert_id": "12345",
            "mispar_tkina": "67890",
            "status_divuah": "תקין"
        }

        # Call the function
        result = process_alert(mock_session.return_value, report_data)

        # Assertions
        self.assertTrue(result)
        mock_session.return_value.get.assert_called_once_with(
            'http://ifs-lab-2025:8080/ActOne/api/v1/work-items/12345'
        )
        mock_session.return_value.post.assert_called_once()

    @patch('update_alert_rest.requests.Session')
    def test_process_alert_missing_fields(self, mock_session):
        # Input data with missing fields
        report_data = {
            "alert_id": "12345",
            "mispar_tkina": ""
        }

        # Call the function
        result = process_alert(mock_session.return_value, report_data)

        # Assertions
        self.assertFalse(result)
        mock_session.return_value.get.assert_not_called()
        mock_session.return_value.post.assert_not_called()

    @patch('update_alert_rest.requests.Session')
    def test_process_alert_fetch_failure(self, mock_session):
        # Mock session and response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_session.return_value.get.return_value = mock_response

        # Input data
        report_data = {
            "alert_id": "12345",
            "mispar_tkina": "67890",
            "status_divuah": "תקין"
        }

        # Call the function
        result = process_alert(mock_session.return_value, report_data)

        # Assertions
        self.assertFalse(result)
        mock_session.return_value.get.assert_called_once()
        mock_session.return_value.post.assert_not_called()

    @patch('update_alert_rest.requests.Session')
    def test_process_alert_update_failure(self, mock_session):
        # Mock session and response
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            "customFields": [
                {"identifier": "Mispar_tkina", "value": ""},
                {"identifier": "Mispar_divuah", "value": ""},
                {"identifier": "status_divuah", "value": ""}
            ]
        }
        mock_post_response = MagicMock()
        mock_post_response.status_code = 500
        mock_session.return_value.get.return_value = mock_get_response
        mock_session.return_value.post.return_value = mock_post_response

        # Input data
        report_data = {
            "alert_id": "12345",
            "mispar_tkina": "67890",
            "status_divuah": "תקין"
        }

        # Call the function
        result = process_alert(mock_session.return_value, report_data)

        # Assertions
        self.assertFalse(result)
        mock_session.return_value.get.assert_called_once()
        mock_session.return_value.post.assert_called_once()

    def test_update_custom_fields_success(self):
        # Input data
        alert = {
            "customFields": [
                {"identifier": "Mispar_tkina", "value": ""},
                {"identifier": "Mispar_divuah", "value": ""},
                {"identifier": "status_divuah", "value": ""}
            ]
        }
        field_updates = {
            "Mispar_tkina": "67890",
            "Mispar_divuah": "12345",
            "status_divuah": "תקין"
        }

        # Call the function
        updated_alert, updated_fields = _update_custom_fields(alert, field_updates)

        # Assertions
        self.assertEqual(len(updated_fields), 3)
        self.assertEqual(updated_alert["customFields"][0]["value"], "67890")
        self.assertEqual(updated_alert["customFields"][1]["value"], "12345")
        self.assertEqual(updated_alert["customFields"][2]["value"], "תקין")

    def test_update_custom_fields_no_custom_fields(self):
        # Input data
        alert = {"customFields": []}
        field_updates = {
            "Mispar_tkina": "67890",
            "Mispar_divuah": "12345",
            "status_divuah": "תקין"
        }

        # Call the function
        updated_alert, updated_fields = _update_custom_fields(alert, field_updates)

        # Assertions
        self.assertEqual(len(updated_fields), 0)
        self.assertEqual(updated_alert["customFields"], [])

    def test_update_custom_fields_partial_update(self):
        # Input data
        alert = {
            "customFields": [
                {"identifier": "Mispar_tkina", "value": ""},
                {"identifier": "Mispar_divuah", "value": ""}
            ]
        }
        field_updates = {
            "Mispar_tkina": "67890",
            "status_divuah": "תקין"
        }

        # Call the function
        updated_alert, updated_fields = _update_custom_fields(alert, field_updates)

        # Assertions
        self.assertEqual(len(updated_fields), 1)
        self.assertEqual(updated_alert["customFields"][0]["value"], "67890")
        self.assertEqual(updated_alert["customFields"][1]["value"], "")


if __name__ == '__main__':
    unittest.main()