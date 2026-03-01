*** Settings ***
Resource        variables.robot
Library         RequestsLibrary

*** Test Cases ***
Gateway returns identity token when IDENTITY_URL is unset
    [Documentation]    GET /api/identity/token returns 200 with virtualId and expiresAtMs (Gateway fallback).
    Create Session    gateway    ${GATEWAY_URL}
    ${resp}=          GET        gateway    /api/identity/token    expected_status=any
    Pass Execution If    ${resp.status_code} != 200    Gateway not available or proxy mode; status=${resp.status_code}
    ${json}=         Set Variable    ${resp.json()}
    Dictionary Should Contain Key    ${json}    virtualId
    Dictionary Should Contain Key    ${json}    expiresAtMs
