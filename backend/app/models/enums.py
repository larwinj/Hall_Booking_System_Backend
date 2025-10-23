import enum

class UserRole(str, enum.Enum):
    customer = "customer"
    moderator = "moderator"
    admin = "admin"

class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class QueryStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"

class PublicationStatus(str, enum.Enum):
    draft = "draft"
    published = "published"