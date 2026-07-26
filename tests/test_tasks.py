def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["status"] == "ToDo"
    assert body["priority"] == "Medium"
    assert body["description"] == ""
    assert body["assignee"] is None
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "priority": "Urgent"})
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Task", "unknown_field": "value"})
    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low one", "priority": "Low"})
    client.post("/tasks", json={"title": "High one", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "High one"
    assert body[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "Updated title"})
    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated title"
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/nonexistent-id", json={"title": "New title"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_invalid_transition_inprogress_to_todo_returns_422(client):
    create_response = client.post("/tasks", json={"title": "Task in progress", "status": "InProgress"})
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    patch_response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})

    assert patch_response.status_code == 422
    assert "Invalid status transition from InProgress to ToDo" in patch_response.json()["detail"]


def test_patch_blank_title_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"title": "   "})

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, title must not be blank"


def test_patch_unknown_field_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"unknown_field": "value"})

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Extra inputs are not permitted"

def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"
def test_create_task_with_valid_due_date_returns_201(client):
    response = client.post("/tasks", json={"title": "Buy milk", "due_date": "2025-12-31"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["due_date"] == "2025-12-31"


def test_create_task_without_due_date_returns_201_with_null_due_date(client):
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["due_date"] is None


def test_create_task_invalid_due_date_format_returns_422(client):
    response = client.post("/tasks", json={"title": "Buy milk", "due_date": "31-12-2025"})
    assert response.status_code == 422


def test_patch_update_due_date_returns_200(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"due_date": "2025-12-31"})
    assert response.status_code == 200
    assert response.json()["due_date"] == "2025-12-31"


def test_patch_clear_due_date_returns_200_with_null(client):
    create_response = client.post("/tasks", json={"title": "Task with due date", "due_date": "2025-12-31"})
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    response = client.patch(f"/tasks/{task_id}", json={"due_date": None})
    assert response.status_code == 200
    assert response.json()["due_date"] is None


def test_overdue_filter_returns_task_with_past_due_date_and_not_done(client):
    client.post("/tasks", json={"title": "Past due task", "due_date": "2020-01-01"})
    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Past due task"
    assert body[0]["due_date"] == "2020-01-01"
    assert body[0]["status"] == "ToDo"


def test_overdue_filter_excludes_task_with_future_due_date(client):
    client.post("/tasks", json={"title": "Future task", "due_date": "2030-01-01"})
    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    assert response.json() == []


def test_overdue_filter_excludes_done_task_even_with_past_due_date(client):
    client.post("/tasks", json={"title": "Done past due", "due_date": "2020-01-01", "status": "Done"})
    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    assert response.json() == []


def test_overdue_filter_excludes_task_with_no_due_date(client):
    client.post("/tasks", json={"title": "No due date task"})
    response = client.get("/tasks", params={"overdue": "true"})

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_without_overdue_param_returns_all_tasks(client):
    client.post("/tasks", json={"title": "Past due task", "due_date": "2020-01-01"})
    client.post("/tasks", json={"title": "Future task", "due_date": "2030-01-01"})
    client.post("/tasks", json={"title": "No due date task"})
    response = client.get("/tasks")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 3
    titles = {task["title"] for task in body}
    assert titles == {"Past due task", "Future task", "No due date task"}


def test_search_matches_title_case_insensitive(client):
    client.post("/tasks", json={"title": "Buy MILK"})
    client.post("/tasks", json={"title": "Read book"})

    response = client.get("/tasks", params={"search": "milk"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Buy MILK"


def test_search_matches_description(client):
    client.post("/tasks", json={"title": "Grocery run", "description": "Need to buy eggs and bread"})
    client.post("/tasks", json={"title": "Office work", "description": "Finish the report"})

    response = client.get("/tasks", params={"search": "eggs"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Grocery run"


def test_search_no_match_returns_200_and_empty_list(client):
    client.post("/tasks", json={"title": "Task one"})
    client.post("/tasks", json={"title": "Task two"})

    response = client.get("/tasks", params={"search": "xyz123nonsense"})
    assert response.status_code == 200
    assert response.json() == []


def test_search_empty_string_returns_all_tasks(client):
    client.post("/tasks", json={"title": "First task"})
    client.post("/tasks", json={"title": "Second task"})

    response = client.get("/tasks", params={"search": ""})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    titles = {task["title"] for task in body}
    assert titles == {"First task", "Second task"}


def test_search_combined_with_status_filter(client):
    client.post("/tasks", json={"title": "Search title"})
    client.post("/tasks", json={"title": "Search done", "status": "Done"})
    client.post("/tasks", json={"title": "Other task"})

    response = client.get("/tasks", params={"status": "ToDo", "search": "search"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Search title"
    assert body[0]["status"] == "ToDo"


def test_search_combined_with_priority_filter(client):
    client.post("/tasks", json={"title": "Search high", "priority": "High"})
    client.post("/tasks", json={"title": "Search low", "priority": "Low"})
    client.post("/tasks", json={"title": "Other task", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High", "search": "search"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Search high"
    assert body[0]["priority"] == "High"
