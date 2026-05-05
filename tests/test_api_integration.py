import os
import sqlite3
import time
from typing import Any

import pytest
import requests


UNIVERSITY_ID = 1
CAMPUS_ID = 3
CAREER_ID = 10
STUDY_PLAN_ID = 48
ACADEMIC_TERM_ID = 101
TIMEOUT_SECONDS = 30


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        pytest.skip(f"Missing required environment variable: {name}")
    return value


@pytest.fixture(scope="session")
def supabase_url() -> str:
    return required_env("SUPABASE_URL").rstrip("/")


@pytest.fixture(scope="session")
def publishable_key() -> str:
    return required_env("SUPABASE_PUBLISHABLE_KEY")


@pytest.fixture(scope="session")
def access_token(supabase_url: str, publishable_key: str) -> str:
    response = requests.post(
        f"{supabase_url}/auth/v1/token?grant_type=password",
        headers={"apikey": publishable_key, "Content-Type": "application/json"},
        json={
            "email": required_env("CLAUSTRUM_EMAIL"),
            "password": required_env("CLAUSTRUM_PASS"),
        },
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body.get("access_token"), str)
    assert body["access_token"]
    return body["access_token"]


@pytest.fixture(scope="session")
def auth_headers(publishable_key: str, access_token: str) -> dict[str, str]:
    return {
        "apikey": publishable_key,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="session")
def anon_headers(publishable_key: str) -> dict[str, str]:
    return {
        "apikey": publishable_key,
        "Authorization": f"Bearer {publishable_key}",
        "Content-Type": "application/json",
    }


@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE selected_schedule_group (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT NOT NULL,
            course_name TEXT NOT NULL,
            campus_id INTEGER,
            group_code TEXT NOT NULL,
            credits INTEGER NOT NULL,
            weekly_hours INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    yield conn
    conn.close()


def rpc(
    supabase_url: str,
    headers: dict[str, str],
    function_name: str,
    payload: dict[str, Any],
) -> requests.Response:
    return requests.post(
        f"{supabase_url}/rest/v1/rpc/{function_name}",
        headers=headers,
        json=payload,
        timeout=TIMEOUT_SECONDS,
    )


def assert_keys_and_types(item: dict[str, Any], expected: dict[str, type | tuple[type, ...]]) -> None:
    assert expected.keys() <= item.keys()
    for key, expected_type in expected.items():
        assert isinstance(item[key], expected_type), f"{key} must be {expected_type}"


def get_schedule_courses(supabase_url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    response = rpc(
        supabase_url,
        headers,
        "get_schedule_courses",
        {
            "p_user_id": None,
            "p_academic_term_id": ACADEMIC_TERM_ID,
            "p_campus_id": CAMPUS_ID,
            "p_study_plan_id": STUDY_PLAN_ID,
            "p_academic_unit_id": CAREER_ID,
            "p_include_other_campuses": False,
            "p_show_all_courses": True,
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data
    return data


def selected_group_lookups(courses: list[dict[str, Any]], limit: int = 2) -> list[dict[str, Any]]:
    lookups: list[dict[str, Any]] = []
    seen_courses: set[str] = set()

    for course in courses:
        groups = course.get("groups") or []
        if not groups or course["course_code"] in seen_courses:
            continue
        group = groups[0]
        lookups.append(
            {
                "courseCode": course["course_code"],
                "campusId": group.get("campus_id") or course.get("campus_id"),
                "groupCode": group["group_code"],
            }
        )
        seen_courses.add(course["course_code"])
        if len(lookups) == limit:
            break

    assert len(lookups) == limit
    return lookups


def save_schedule(
    supabase_url: str,
    headers: dict[str, str],
    name: str,
    group_lookups: list[dict[str, Any]],
) -> dict[str, Any]:
    response = rpc(
        supabase_url,
        headers,
        "save_user_schedule",
        {
            "p_name": name,
            "p_academic_term_id": ACADEMIC_TERM_ID,
            "p_group_lookups": group_lookups,
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    return body[0]


def delete_schedule(supabase_url: str, headers: dict[str, str], schedule_id: int) -> None:
    response = requests.delete(
        f"{supabase_url}/rest/v1/saved_schedule?id=eq.{schedule_id}",
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code in {200, 204}, response.text


def test_catalog_flow_contract(supabase_url: str, auth_headers: dict[str, str]) -> None:
    universities_response = requests.get(
        f"{supabase_url}/rest/v1/v_universities?select=id,name,short_name&id=eq.{UNIVERSITY_ID}",
        headers=auth_headers,
        timeout=TIMEOUT_SECONDS,
    )
    assert universities_response.status_code == 200, universities_response.text
    universities = universities_response.json()
    assert isinstance(universities, list)
    assert universities
    assert_keys_and_types(universities[0], {"id": int, "name": str, "short_name": str})
    assert universities[0]["id"] == UNIVERSITY_ID
    assert universities[0]["name"].strip()

    campuses_response = rpc(
        supabase_url,
        auth_headers,
        "get_campuses_for_university",
        {"p_university_id": UNIVERSITY_ID},
    )
    assert campuses_response.status_code == 200, campuses_response.text
    campuses = campuses_response.json()
    assert isinstance(campuses, list)
    assert campuses
    assert any(campus["id"] == CAMPUS_ID for campus in campuses)
    assert all(
        assert_keys_and_types(campus, {"id": int, "university_id": int, "code": str, "name": str}) is None
        for campus in campuses
    )

    careers_response = rpc(
        supabase_url,
        auth_headers,
        "get_academic_units_for_campus",
        {"p_campus_id": CAMPUS_ID},
    )
    assert careers_response.status_code == 200, careers_response.text
    careers = careers_response.json()
    assert isinstance(careers, list)
    assert careers
    assert any(career["id"] == CAREER_ID for career in careers)
    assert all(
        assert_keys_and_types(career, {"id": int, "code": str, "name": str}) is None
        for career in careers
    )

    plans_response = rpc(
        supabase_url,
        auth_headers,
        "get_study_plans_for_academic_unit",
        {"p_academic_unit_id": CAREER_ID},
    )
    assert plans_response.status_code == 200, plans_response.text
    plans = plans_response.json()
    assert isinstance(plans, list)
    assert plans
    assert any(plan["id"] == STUDY_PLAN_ID for plan in plans)
    assert all(
        assert_keys_and_types(
            plan,
            {
                "id": int,
                "academic_unit_id": int,
                "external_plan_id": int,
                "name": str,
            },
        ) is None
        for plan in plans
    )


def test_schedule_courses_contract_and_response_time(
    supabase_url: str,
    auth_headers: dict[str, str],
) -> None:
    started = time.perf_counter()
    courses = get_schedule_courses(supabase_url, auth_headers)
    elapsed_ms = (time.perf_counter() - started) * 1000

    assert elapsed_ms < 5000
    course = next(item for item in courses if item.get("groups"))
    assert isinstance(course["offering_id"], int)
    assert isinstance(course["course_code"], str)
    assert course["course_code"].strip()
    assert isinstance(course["course_name"], str)
    assert course["course_name"].strip()
    assert isinstance(course["credits"], int)
    assert course["credits"] >= 0
    assert isinstance(course["weekly_hours"], int)
    assert course["weekly_hours"] >= 0
    assert course["academic_term_id"] == ACADEMIC_TERM_ID
    assert course["campus_id"] == CAMPUS_ID

    group = course["groups"][0]
    assert isinstance(group["group_id"], int)
    assert isinstance(group["group_code"], str)
    assert group["group_code"].strip()
    assert isinstance(group["meetings"], list)


def test_insert_selected_groups_in_sqlite_and_calculate_totals(
    supabase_url: str,
    auth_headers: dict[str, str],
    db_connection,
) -> None:
    courses = get_schedule_courses(supabase_url, auth_headers)
    cursor = db_connection.cursor()

    inserted = 0
    for course in courses:
        groups = course.get("groups") or []
        if not groups:
            continue
        group = groups[0]
        cursor.execute(
            """
            INSERT INTO selected_schedule_group (
                course_code,
                course_name,
                campus_id,
                group_code,
                credits,
                weekly_hours
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                course["course_code"],
                course["course_name"],
                group.get("campus_id") or course.get("campus_id"),
                group["group_code"],
                course["credits"],
                course["weekly_hours"],
            ),
        )
        inserted += 1
        if inserted == 2:
            break

    db_connection.commit()
    cursor.execute(
        "SELECT COUNT(*), SUM(credits), SUM(weekly_hours) FROM selected_schedule_group"
    )
    count, total_credits, total_weekly_hours = cursor.fetchone()

    assert count == 2
    assert total_credits > 0
    assert total_weekly_hours > 0


def test_save_schedule_and_load_group_lookups_persists_selection(
    supabase_url: str,
    auth_headers: dict[str, str],
) -> None:
    courses = get_schedule_courses(supabase_url, auth_headers)
    group_lookups = selected_group_lookups(courses)
    schedule = save_schedule(
        supabase_url,
        auth_headers,
        f"QA Pytest {int(time.time())}",
        group_lookups,
    )

    try:
        assert isinstance(schedule["id"], int)
        assert isinstance(schedule["name"], str)
        assert schedule["name"].startswith("QA Pytest")
        assert schedule["academic_term_id"] == ACADEMIC_TERM_ID
        assert isinstance(schedule["created_at"], str)
        assert isinstance(schedule["updated_at"], str)

        response = rpc(
            supabase_url,
            auth_headers,
            "get_user_saved_schedule_group_lookups",
            {"p_saved_schedule_id": schedule["id"]},
        )
        assert response.status_code == 200, response.text
        saved_items = response.json()
        assert len(saved_items) == len(group_lookups)
        for item in saved_items:
            assert {"course_code", "campus_id", "group_code"} <= item.keys()
            assert isinstance(item["course_code"], str)
            assert isinstance(item["campus_id"], int)
            assert isinstance(item["group_code"], str)
    finally:
        delete_schedule(supabase_url, auth_headers, schedule["id"])


def test_delete_saved_schedule_removes_it(
    supabase_url: str,
    auth_headers: dict[str, str],
) -> None:
    courses = get_schedule_courses(supabase_url, auth_headers)
    schedule = save_schedule(
        supabase_url,
        auth_headers,
        f"QA Delete {int(time.time())}",
        selected_group_lookups(courses, limit=1),
    )

    delete_schedule(supabase_url, auth_headers, schedule["id"])

    response = requests.get(
        f"{supabase_url}/rest/v1/saved_schedule?select=id&id=eq.{schedule['id']}",
        headers=auth_headers,
        timeout=TIMEOUT_SECONDS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_save_schedule_requires_authentication(
    supabase_url: str,
    anon_headers: dict[str, str],
) -> None:
    response = rpc(
        supabase_url,
        anon_headers,
        "save_user_schedule",
        {
            "p_name": "No Auth Schedule",
            "p_academic_term_id": ACADEMIC_TERM_ID,
            "p_group_lookups": [
                {"courseCode": "CI0202", "campusId": CAMPUS_ID, "groupCode": "01"}
            ],
        },
    )

    assert response.status_code in {401, 403, 404}


def test_save_schedule_rejects_empty_name(
    supabase_url: str,
    auth_headers: dict[str, str],
) -> None:
    courses = get_schedule_courses(supabase_url, auth_headers)
    response = rpc(
        supabase_url,
        auth_headers,
        "save_user_schedule",
        {
            "p_name": "   ",
            "p_academic_term_id": ACADEMIC_TERM_ID,
            "p_group_lookups": selected_group_lookups(courses, limit=1),
        },
    )

    assert response.status_code == 400
    assert "nombre" in response.text.lower()


def test_save_schedule_rejects_invalid_groups(
    supabase_url: str,
    auth_headers: dict[str, str],
) -> None:
    response = rpc(
        supabase_url,
        auth_headers,
        "save_user_schedule",
        {
            "p_name": "Invalid Groups",
            "p_academic_term_id": ACADEMIC_TERM_ID,
            "p_group_lookups": [
                {"courseCode": "NOEXISTE999", "campusId": CAMPUS_ID, "groupCode": "ZZ"}
            ],
        },
    )

    assert response.status_code == 400
    assert "grupos validos" in response.text.lower()


def test_partial_invalid_groups_are_saved_as_current_behavior(
    supabase_url: str,
    auth_headers: dict[str, str],
) -> None:
    courses = get_schedule_courses(supabase_url, auth_headers)
    group_lookups = selected_group_lookups(courses, limit=1)
    group_lookups.append(
        {"courseCode": "NOEXISTE999", "campusId": CAMPUS_ID, "groupCode": "ZZ"}
    )
    schedule = save_schedule(
        supabase_url,
        auth_headers,
        f"QA Partial {int(time.time())}",
        group_lookups,
    )

    try:
        response = rpc(
            supabase_url,
            auth_headers,
            "get_user_saved_schedule_group_lookups",
            {"p_saved_schedule_id": schedule["id"]},
        )
        assert response.status_code == 200, response.text
        saved_items = response.json()
        assert len(saved_items) == 1
    finally:
        delete_schedule(supabase_url, auth_headers, schedule["id"])
