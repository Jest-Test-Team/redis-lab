*** Settings ***
Resource        variables.robot
Library         RequestsLibrary

*** Test Cases ***
Identity returns token
    [Documentation]    GET /identity/token returns 200 with virtual_id.
    Create Session    identity    ${IDENTITY_URL}
    ${resp}=          GET        identity    /identity/token    expected_status=any
    Pass Execution If    ${resp.status_code} in [502, 503, 0]    Identity service not available
    Should Be Equal As Numbers    ${resp.status_code}    200
    ${json}=         Set Variable    ${resp.json()}
    Dictionary Should Contain Key    ${json}    virtual_id
    Dictionary Should Contain Key    ${json}    expires_at_ms
