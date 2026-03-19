# Task Planning API


# Przejdziemy przez 5 etapów:

1️⃣ System Vision
2️⃣ Functional requirments
3️⃣ Non-functional requirments
4️⃣ Domain model
5️⃣ API endpoints

# 1. System Vision [This can be change later]
- Purpose [ value he brings ]
    System allow Users manage tasks in structure [Tree based] way with deadlines and status
    which allow to manage related task easily in project scope
- who use system ? 
    One User on start later we will see.
- this is system for one or many users ?
    User - personal user - later maybe team
- task are manual or automatic ?
    task are manual on first interation later maybe also automatic
- task are made to be done once or freqently also ?
    task have it own status TODO, IN_PROGRESS, DONE
- task can have parent and childs
- task are in tree hierachi
- task are assaing to project
- task has deadline, priority, content, status
- project has owner and members as user ( later on i will not focus on user and auth policy right now )

# 2. Functional requirments
- User can create task
- User can assign/change parent task
- User can change task status to TODO, IN_PROGRESS, DONE (only if subtasks are done also)
- User can view task hierachy
- User can deleted task, optional with subtasks [ task with out parent are still has assaing to project ]
- User can see all task in given project
- User can see all task with parent

# Non-functional requirments
- System should support pagination (10 items default)
- System should handle large task trees efficiently

# Domain model
## Entities:
- User 
{
    id int, 
    name char, 
}
- Project 
{
    id int, 
    name char, 
    owner_id nullable/int, 
}
- Task 
{
    id int, 
    name char, 
    content char, 
    status char,
    priority int
    deadline datetime, 
    parent_id nullable int, 
    project_id int not null
}

- ProjectMember
{
    user_id int
    project_id int
}
## Relations:
- User <-> Project(members)
- User -> Project(owner)
- Project -> Task(project)
- Task(parent) -> Task(subtask)
# API endpoints
## Tasks
- create task
POST /tasks 
JSON
{
    'content': '', 
    'deadline': '', 
    'priority': 'MINOR'
}
- get task
GET /tasks/{id}
- list tasks
GET /tasks/
- list task with filter status, project id and sorting by deadline
GET /tasks?status=TODO&project_id=1&sort=deadline
- edit task
PATCH /tasks/{id} 
JSON
{
    'content': '', 
    'deadline': '', 
    'priority': 'BLOCKER/CRITICAL/MAJOR/MINOR',  
    'status': 'TODO/IN_PROGRES/DONE'
}
- delete task
DELETE /tasks/{id}

## Projects
- add project
POST /projects 
JSON
{
    'name': 'Telecom'
}
- assaing Onner
PATCH /projects/{id} 
JSON
{
    'owner_id': 1
}
- add Member
PATCH /projects/{id} 
JSON
{
    'members_id: "1"
}
- get project
GET /projects/{id}
- list projects
GET /projects
- remove projects
DELETE /projects/{id}

## User
- create user
POST /users 
JSON
{
    'name': 'Jhon'
}
- get user
GET /users/{id}
- list users
GET /users
- remove user
DELETE /users/{id}
