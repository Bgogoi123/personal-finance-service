from sqlalchemy import Column, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from src.utils.db import Base


class UsersModel(Base):
    __tablename__ = "users"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone_number = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False, unique=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=True  # NULL until the role is actually updated
    )
    role_id = Column(String, ForeignKey(
        "roles.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)

    # Relationships
    role = relationship("RolesModel", back_populates="user")  # Current

    balance = relationship("BalanceModel", back_populates="user")
    category = relationship("CategoriesModel", back_populates="user")
    payment_option = relationship(
        "PaymentOptionsModel", back_populates="user")
    transactions = relationship("TransactionsModel", back_populates="user")

    # SQLAlchemy's 'relationship()' is an Object-Relational Mapping (ORM) abstraction.
    # It tells SQLAlchemy to link Python object properties together based on the underlying Foreign Key constraint.
    # Without relationships, if we want to know the name or type of a user's role in Python,
    # we would have to write a separate query manually every single time:
    # 1. 'user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))'
    # 2. 'role = await session.scalar(select(RolesModel).where(RolesModel.id == user.role_id))
    # 3. print(role.type)

    # Here, instead of querying the database twice manually, SQLAlchemy automatically links the instances.
    # - user.role returns the full RolesModel object associated with that user (user.role.type, user.role.name).
    # - role.users returns a list of all UsersModel objects assigned to that role.
    # - 'back_populates' synchronizes both sides in memory. If you assign user.role = admin_role,
    #         role.users immediately includes user before you even commit to the database.


class RefreshTokensModel(Base):
    __tablename__ = "refresh_tokens"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    device_info = Column(JSON, nullable=True)
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE",
                     onupdate="CASCADE"), nullable=False)
