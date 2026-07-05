from enum import StrEnum


class TaskStatus(StrEnum):
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    DONE = 'done'


class TaskPriority(StrEnum):
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    MAJOR = 'major'
    MINOR = 'minor'


class SortBy(StrEnum):
    DEADLINE = 'deadline'
    NAME = 'name'
    CREATED_AT = 'created_at'


class OrderBy(StrEnum):
    ASC = 'asc'
    DESC = 'desc'


class UserRole(StrEnum):
    ADMIN = 'admin'
    USER = 'user'
