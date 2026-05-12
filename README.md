# Task Planning API

## Overview
Task Planning API is a backend system for managing tasks in a **tree-based structure** within projects.  
It supports task hierarchy, deadlines, and status tracking to better organize related work.

---

## System Design Stages

1. System Vision  
2. Functional Requirements  
3. Non-Functional Requirements  
4. Domain Model  
5. API Endpoints  

---

## 1) System Vision

### Purpose
The system enables users to manage tasks in a hierarchical (tree-based) structure with deadlines and statuses, making it easier to organize related tasks within a project.

### Users
- Initially: single user  
- Future: multi-user (teams)

### Task Characteristics
- Tasks are **manual** (future: automatic)
- Tasks have statuses:
  - `todo`
  - `in_progress`
  - `done`
- Tasks can:
  - have a parent
  - have multiple children
- Tasks belong to a project
- Tasks include:
  - deadline
  - priority
  - content
  - owner (`owner_id`)

### Project
- Has an owner (User)
- Has members (Users)
- Contains tasks

---

## 2) Functional Requirements

- User can create a task  
- User can assign or change a parent task  
- User can change task status (`todo`, `in_progress`, `done`)  
  - Parent task can be changed to `done` only when all direct child tasks are `done`
  - A `done` parent task can be reopened to `todo` or `in_progress`
  - After reopening a parent task, child task statuses can be changed again
- User can view task hierarchy  
- User can delete a task  
  - Children tasks will have `parent_id = null`  
- User can list all tasks in a project  
- User can list tasks by parent - Not implemented yet  
- User can assign an owner to project (`owner_id`)
- User can remove project owner (`owner_id = null`)
- User can assign an owner to task (`owner_id`)
- User can remove task owner (`owner_id = null`)
- User can add project members
- User can remove project members

---

## 3) Non-Functional Requirements / Business Rules

- Deleting a parent task does **not** delete children
- Child tasks remain assigned to the same project
- Parent task must be manually updated to `done`
- System must prevent cycles in task hierarchy
- Pagination default is 10 items per page
- System should handle large task trees efficiently
- Project owner assignment is optional (`owner_id` can be `null`)
- If project owner is provided, user must exist
- Deleting a user sets `project.owner_id = null`
- Project member can be added only when both project and user exist
- Duplicate project membership is rejected (`409 Conflict`)
- Membership removal is strict and returns `404` when project or membership does not exist
- Task owner assignment rule:
  - when task has `project_id`, owner must exist and be a member of this project
  - when task has no `project_id`, any existing user can be assigned as owner
- Task status rules:
  - a parent task cannot be changed to `done` while any direct child task is not `done`
  - a task with status `done` cannot receive new child tasks
  - a child task under a `done` parent cannot be changed back to `todo` or `in_progress`
  - a `done` parent can be reopened to `todo` or `in_progress`; after reopening, children can change status again
- Task update request does not accept explicit `null` for `priority`, `deadline`, or `status`; omit fields to keep values unchanged

---

## 4) Domain Model

### Entities

#### User
```json
{
  "id": "int",
  "name": "string"
}
```

#### Project
```json
{
  "id": "int",
  "name": "string",
  "owner_id": "int | null"
}
```

#### Task
```json
{
  "id": "int",
  "name": "string",
  "content": "string",
  "status": "todo | in_progress | done",
  "priority": "blocker | critical | major | minor",
  "deadline": "datetime",
  "parent_id": "int | null",
  "project_id": "int",
  "owner_id": "int | null"
}
```
`owner_id` for task is implemented and validated by project assignment rules.

#### ProjectMember
```json
{
  "user_id": "int",
  "project_id": "int"
}
```
Constraint: (`user_id`, `project_id`) must be unique.

### Relationships
- User ↔ Project (many-to-many via `ProjectMember`)
- User → Project (owner)
- User → Task (owner)
- Project → Task (one-to-many)
- Task → Task (self-relation, parent → children)

---

## 5) API Endpoints
### Tasks
#### Create Task
`POST /tasks`
```json
{
  "name": "Task name",
  "content": "desc",
  "project_id": 1,
  "parent_id": null,
  "deadline": "2026-03-20T10:00:00",
  "priority": "minor",
  "owner_id": 1
}
```
`owner_id` in create payload is supported.

Rules:
- `parent_id` must reference an existing task.
- Creating a child task under a `done` parent is rejected because new tasks start as `todo`.

#### Get Task
`GET /tasks/{id}`

#### List Tasks
`GET /tasks`

#### Filter Tasks
`GET /tasks?search=report&sort=deadline&order=desc&page=1&limit=10`  
`status` and `project_id` filters are planned and currently not implemented.

#### Update Task
`PATCH /tasks/{id}`
```json
{
  "content": "desc",
  "deadline": "2026-03-20T10:00:00",
  "priority": "major",
  "status": "in_progress",
  "owner_id": 1
}
```
Task owner update is supported.

Rules:
- Changing `parent_id` to a `done` parent is rejected.
- Changing a parent task to `done` is allowed only when all direct child tasks are already `done`.
- Changing a `done` parent back to `todo` or `in_progress` is allowed.
- Changing a child task under a `done` parent back to `todo` or `in_progress` is rejected.
- Send `status`, `priority`, and `deadline` only when changing them; explicit `null` is rejected.

#### Delete Task
`DELETE /tasks/{id}`

### Projects
#### Create Project
`POST /projects`
```json
{
  "name": "Telecom",
  "owner_id": 1
}
```

#### Assign Owner
`PATCH /projects/{id}`
```json
{
  "owner_id": 1
}
```
#### Get Members
`GET /projects/{id}/members`
Responses:
- `200 OK`: returns project members
- `404 Not Found`: project does not exist

Notes:
- Members are returned ordered by `user_id` ascending for deterministic output.

#### Add Member
`POST /projects/{id}/members`
```json
{
  "user_id": 1
}
```
Responses:
- `200 OK`: member added, returns created membership
- `404 Not Found`: project or user does not exist
- `409 Conflict`: user is already a member of this project

#### Remove Member
`DELETE /projects/{id}/members/{user_id}`
Responses:
- `204 No Content`: membership removed
- `404 Not Found`: project does not exist or membership is missing

#### Get Project
`GET /projects/{id}`

#### List Projects
`GET /projects`

#### Delete Project
`DELETE /projects/{id}`

### Users
#### Create User
`POST /users`
```json
{
  "name": "John"
}
```

#### Get User
`GET /users/{id}`

#### List Users
`GET /users`

#### Delete User
`DELETE /users/{id}`

### Error Response Contract
Business and application errors use a stable response shape:

```json
{
  "code": "membership_not_found",
  "detail": "Project membership with user id '1' does not exist in project id '1'"
}
```

Decision:
- `code` is the stable machine-readable contract for API integrations
- `detail` is the human-readable explanation and may change over time

Why this decision was made:
- tests should validate stable public API contract, not fragile message wording
- frontend and other API consumers can branch on `code` safely
- `detail` can be improved or rewritten without breaking integrations

Guidelines:
- assert `status_code` and `code` in integration tests for business errors
- avoid asserting exact `detail` text unless the message itself is part of the contract
- keep `code` values intentional and stable across refactors


## Current MVP Scope

- Implemented: Users, Projects, and Tasks CRUD.
- Implemented: Task hierarchy rules (no cycle, no self-parent, project consistency).
- Implemented: Shared list contract (`search`, `sort`, `order`, `page`, `limit`).
- Implemented: Project owner assignment validation and owner cleanup on user deletion.
- Implemented: Add project member endpoint with duplicate-membership validation.
- Implemented: Get project members endpoint.
- Implemented: Remove project member endpoint with strict not-found validation.
- Implemented: Task owner assignment with project membership validation.
- Planned: Additional task filters (`status`, `project_id`) and list-by-parent endpoint.

## Missing / Things To Consider Next

- Authorization rules: who can update/delete project or task.
- Membership policy: should project owner be required to be a member.
- Task owner assignment without project allows any existing user.
- Deployment readiness for cloud: env configuration, migration strategy, health checks, and logging/monitoring.


## Future Enhancements
- Smart risk alerts based on project activity and deadlines
- Progress estimation using velocity metrics
- Historical analysis of estimation vs actual effort
- AI-powered project insights and explanations