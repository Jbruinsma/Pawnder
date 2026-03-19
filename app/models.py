import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .database import Base

# --- Association Tables for Many-to-Many Relationships ---

# Maps which users have bookmarked which posts [cite: 33, 185]
bookmarks = Table(
    "bookmarks",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("post_id", UUID(as_uuid=True), ForeignKey("posts.id"), primary_key=True),
)

# Maps users to the neighborhood groups they join [cite: 272, 282]
user_communities = Table(
    "user_communities",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("community_id", UUID(as_uuid=True), ForeignKey("communities.id"), primary_key=True),
)

# Maps tags (Species, Breed) to specific pet posts [cite: 359]
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True), ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), primary_key=True),
)


# --- Core Tables ---

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String, nullable=False, info={"description": "Community User or Shelter/Moderator"})  # [cite: 322]
    email = Column(String, unique=True, nullable=False, index=True)  # [cite: 325]
    password_hash = Column(String, nullable=False)  # [cite: 327]
    full_name = Column(String, nullable=False)  # [cite: 329]

    # PostGIS Point for the user's current context [cite: 198, 331]
    last_known_location = Column(Geometry(geometry_type='POINT', srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    posts = relationship("Post", back_populates="author")
    joined_communities = relationship("Community", secondary=user_communities, back_populates="members")
    saved_posts = relationship("Post", secondary=bookmarks)


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    post_type = Column(String, nullable=False)  # Lost, Found, Alert, General [cite: 341]
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)  # [cite: 343]

    # The spatial anchor for geo-relevant feeds [cite: 130, 345]
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)

    status = Column(String, default="Active")  # Active, Resolved [cite: 348]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    author = relationship("User", back_populates="posts")
    tags = relationship("Tag", secondary=post_tags)


class Community(Base):
    __tablename__ = "communities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)  # e.g., "Brooklyn" [cite: 272]
    description = Column(String)

    # Spatial Polygon to define the neighborhood boundary [cite: 355]
    geofence_boundary = Column(Geometry(geometry_type='POLYGON', srid=4326))

    # Relationships
    members = relationship("User", secondary=user_communities, back_populates="joined_communities")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String, nullable=False)  # Species, Breed, Status [cite: 363]
    name = Column(String, nullable=False)  # e.g., "Husky", "Dog" [cite: 365]