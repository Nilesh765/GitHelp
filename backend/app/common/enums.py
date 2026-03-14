import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    manager = "manager"

class RepoProvider(str, enum.Enum):
    github = "github"
    gitlab = "gitlab"

class RepoStatus(str, enum.Enum):
    pending = "pending"
    cloning = "cloning"
    analyzing = "analyzing"
    completed = "completed"
    failed = "failed"

class AnalysisMode(str, enum.Enum):
    full = "full"
    quick = "quick"

class ReviewStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"