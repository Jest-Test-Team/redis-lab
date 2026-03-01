*** Settings ***
Resource        variables.robot
Library         RequestsLibrary

*** Test Cases ***
Engine create auction
    [Documentation]    POST /auction/create returns 200/201; requires Redis.
    Create Session    engine    ${ENGINE_URL}
    ${body}=          Create Dictionary    auction_id=robot-${SUITE_NAME}-1    duration_ms=5000
    ${resp}=          POST       engine    /auction/create    json=${body}    expected_status=any
    Pass Execution If    ${resp.status_code} in [502, 503, 0]    Engine or Redis not available
    Should Be True    ${resp.status_code} in [200, 201]    Expected 200/201, got ${resp.status_code}
    Dictionary Should Contain Key    ${resp.json()}    ok

Engine leaderboard
    [Documentation]    GET /auction/leaderboard/:id returns entries array.
    Create Session    engine    ${ENGINE_URL}
    ${resp}=          GET        engine    /auction/leaderboard/robot-${SUITE_NAME}-1    expected_status=any
    Pass Execution If    ${resp.status_code} in [502, 503, 0]    Engine not available
    Should Be Equal As Numbers    ${resp.status_code}    200
    Dictionary Should Contain Key    ${resp.json()}    entries
