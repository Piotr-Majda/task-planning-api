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
  - owner (`owner_id`) - Not implemented yet

### Project
- Has an owner (User)
- Has members (Users) - Not implemented yet
- Contains tasks

---

## 2) Functional Requirements

- User can create a task  
- User can assign or change a parent task  
- User can change task status (`todo`, `in_progress`, `done`)  
  - Only if all subtasks are `done` - Not implemented yet  
- User can view task hierarchy  
- User can delete a task  
  - Children tasks will have `parent_id = null`  
- User can list all tasks in a project  
- User can list tasks by parent - Not implemented yet  
- User can assign an owner to project (`owner_id`)
- User can remove project owner (`owner_id = null`)
- User can assign an owner to task (`owner_id`) - Not implemented yet
- User can remove task owner (`owner_id = null`) - Not implemented yet
- User can add and remove project members - Not implemented yet

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
- Task owner assignment should follow the same rule as project owner - Not implemented yet

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
`owner_id` for task is planned and currently not implemented.

#### ProjectMember
```json
{
  "user_id": "int",
  "project_id": "int"
}
```
Constraint: (`user_id`, `project_id`) must be unique.

### Relationships
- User ↔ Project (many-to-many via ProjectMember) - Not implemented yet
- User → Project (owner)
- User → Task (owner) - Not implemented yet
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
`owner_id` in task payload is planned and currently not implemented.

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
Task owner update is planned and currently not implemented.

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

#### Add Member
`POST /projects/{id}/members`
```json
{
  "user_id": 1
}
```
Not implemented yet.

#### Remove Member
`DELETE /projects/{id}/members`
```json
{
  "user_id": 1
}
```
Not implemented yet.

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

---

## Current MVP Scope

- Implemented: Users, Projects, and Tasks CRUD.
- Implemented: Task hierarchy rules (no cycle, no self-parent, project consistency).
- Implemented: Shared list contract (`search`, `sort`, `order`, `page`, `limit`).
- Implemented: Project owner assignment validation and owner cleanup on user deletion.
- Planned: Task owner assignment and owner cleanup on user deletion.
- Planned: Project member endpoints and membership rules.
- Planned: Additional task filters (`status`, `project_id`) and list-by-parent endpoint.

## Missing / Things To Consider Next

- Authorization rules: who can update/delete project or task.
- Membership policy: should project owner be required to be a member.
- Task assignment policy: any user vs only project members.
- Deployment readiness for cloud: env configuration, migration strategy, health checks, and logging/monitoring.
