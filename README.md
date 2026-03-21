# 📌 Task Planning API

## 🧭 Overview
Task Planning API is a system that allows users to manage tasks in a **tree-based structure** within projects.  
It supports task hierarchy, deadlines, and status tracking to better organize related work.

---

## 🧱 System Design Stages

1. System Vision  
2. Functional Requirements  
3. Non-Functional Requirements  
4. Domain Model  
5. API Endpoints  

---

## 1️⃣ System Vision

### 🎯 Purpose
The system enables users to manage tasks in a hierarchical (tree-based) structure with deadlines and statuses, making it easier to organize related tasks within a project.

### 👤 Users
- Initially: single user  
- Future: multi-user (teams)

### ⚙️ Task Characteristics
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

### 📁 Project
- Has an owner (User)
- Has members (Users)
- Contains tasks

---

## 2️⃣ Functional Requirements

- User can create a task  
- User can assign or change a parent task  
- User can change task status (`todo`, `in_progress`, `done`)  
  - Only if all subtasks are `done`  
- User can view task hierarchy  
- User can delete a task  
  - Children tasks will have `parent_id = null`  
- User can list all tasks in a project  
- User can list tasks by parent  

---

## 3️⃣ Non-Functional Requirements / Business Rules

- Deleting a parent task does **not delete children**
- Child tasks remain assigned to the same project
- Parent task must be manually updated to `done`
- System must prevent cycles in task hierarchy
- Pagination: default 10 items per page
- System should handle large task trees efficiently

---

## 4️⃣ Domain Model

### 🧩 Entities

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
  "project_id": "int"
}
```
#### ProjectMember
```json
{
  "user_id": "int",
  "project_id": "int"
}
```
Constraint: (user_id, project_id) must be unique
### 🔗 Relationships
- User ↔ Project (many-to-many via ProjectMember)
- User → Project (owner)
- Project → Task (one-to-many)
- Task → Task (self-relation, parent → children)
## 5️⃣ API Endpoints
### 📌 Tasks
#### Create Task
POST /tasks
```json
{
  "name": "Task name",
  "content": "desc",
  "project_id": 1,
  "parent_id": null,
  "deadline": "2026-03-20T10:00:00",
  "priority": "minor"
}
```
#### Get Task
GET /tasks/{id}
#### List Tasks
GET /tasks
#### Filter Tasks
GET /tasks?status=TODO&project_id=1&sort=deadline
#### Update Tasks
PATCH /tasks/{id}
```json
{
  "content": "desc",
  "deadline": "2026-03-20T10:00:00",
  "priority": "major",
  "status": "in_progress"
}
```
#### Delete Task
DELETE /tasks/{id}

### 📌 Projects
#### Create Project
POST /projects
```json
{
    "name": "Telecom"
}
```
#### Assign Owner
PATCH /projects/{id}
```json
{
  "owner_id": 1
}
```
#### Add Member
PATCH /projects/{id}/add_member
```json
{
  "user_id": 1
}
```
#### Remove Member
PATCH /projects/{id}/remove_member
```json
{
  "user_id": 1
}
```
#### Get Project
GET /projects/{id}
#### List Projects
GET /projects
#### Delete Project
DELETE /projects/{id}
### Users
#### Create User
POST /users
```json
{
  "name": "John"
}
```
#### Get User
GET /users/{id}
#### List Users
GET /users/{id}
#### Delete User
DELETE /users/{id}
