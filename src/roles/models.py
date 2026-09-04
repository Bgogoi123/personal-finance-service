from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
from src.utils.db import Base
import uuid


class RolesModel(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, default=lambda: str(
        uuid.uuid4()), nullable=False)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False, default="default")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # DB generates the value on INSERT
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True  # NULL until the role is actually updated
    )

    user = relationship("UsersModel", back_populates="role")
    # SQLAlchemy's 'relationship()' is an Object-Relational Mapping (ORM) abstraction.
    # It tells SQLAlchemy to link Python object properties together based
    # on the underlying Foreign Key constraint.
    # Without relationships, if we want to know the name or type of a user's role in Python,
    # we would have to write a separate query manually every single time:
    # 1. 'user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))'
    # 2. 'role = await session.scalar(select(RolesModel).where(RolesModel.id == user.role_id))
    # 3. print(role.type)

    # Here, instead of querying the database twice manually,
    # SQLAlchemy automatically links the instances.
    # - user.role returns the full RolesModel object associated with that
    # user (user.role.type, user.role.name).
    # - role.users returns a list of all UsersModel objects assigned to that role.
    # - 'back_populates' synchronizes both sides in memory. If you assign user.role = admin_role,
    #         role.users immediately includes user before you even commit to the database.
