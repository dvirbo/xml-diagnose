import logging

logging.basicConfig(level=logging.DEBUG)

def update_alert(client, identifier, updated_alert_data):
    """Update the alert using the SOAP service."""
    try:
        update_response = client.service.updateAlert(
            alertIdentifier=identifier, 
            alert=updated_alert_data
        )
        if update_response and update_response.alertResult:
            logging.info('AlertResult: %s', update_response.alertResult)
        return update_response
    except Exception as e:
        print('[ERROR] Failed to update alert:', e)
        return None

def change_alert_status(client, alert_identifiers, status_identifier, force_status=False, additional_comments="", alert_result_list=None):
    """
    Change the status of one or more alerts using the SOAP service.
    """
    try:
        response = client.service.changeAlertStatus(
            alertsIdentifiers=alert_identifiers,
            statusIdentifier=status_identifier,
            forceStatus=force_status,
            additionalComments=additional_comments,
            alertResultList=alert_result_list
        )

        logging.info('Alert status changed: %s', response)
        return response
    except Exception as e:
        logging.error('Failed to change alert status: %s', e)
        return None
    


def add_notes_request(client, alert_identifier, notes, is_confidential=False):
    """
    Add notes to an alert using the SOAP service.

    :param client: Zeep client instance
    :param alert_identifier: The alert identifier (string)
    :param notes: List of note strings to add
    :param is_confidential: Boolean flag for confidentiality
    :return: SOAP response
    """
    try:
        response = client.service.addNotes(
            alertIdentifier=alert_identifier,
            notes=notes,
            isConfidential=is_confidential
        )
        print('[SUCCESS] Notes added:', response)
        return response
    except Exception as e:
        print('[ERROR] Failed to add notes:', e)
        return None
    
def prepare_updated_alert_data(alert_response):
    """Prepare the alert data dictionary for update.""" 
    # Ensure all mandatory fields are included and properly formatted
    updated_data = {
        'alertAISCallXML': alert_response.alert.alertAISCallXML or '',
        'alertDate': alert_response.alert.alertDate,
        'alertIdentifier': alert_response.alert.alertIdentifier,
        'alertTypeIdentifier': alert_response.alert.alertTypeIdentifier,
        'alertTypeVersion': alert_response.alert.alertTypeVersion,
        'attributes': alert_response.alert.attributes,
        'buIdentifier': alert_response.alert.buIdentifier,
        'details': alert_response.alert.details,
        'ownerIdentifier': alert_response.alert.ownerIdentifier,
        'score': 23,  # Example updated score
        'statusIdentifier': alert_response.alert.statusIdentifier,
        'useZippedXml': alert_response.alert.useZippedXml,
        'xml': alert_response.alert.xml,
        'zippedXml': alert_response.alert.zippedXml
    }
    return updated_data