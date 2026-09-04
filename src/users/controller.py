import re
from fastapi import HTTPException,  status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.auth.controller import PASSWORD_REGEX, PASSWORD_RULE_MESSAGE
from src.auth.models import UsersModel
from src.auth.schema import ChangePasswordSchema, UserResponseSchema, UserUpdateSchema
from src.roles.models import RolesModel
from src.utils.auth.passwords import get_hashed_password, verify_password


async def get_all_users(session: AsyncSession):
    try:
        users = await session.scalars(select(UsersModel))

        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No Users found.")

        return users
    except SQLAlchemyError as err:
        print(f"Error while fetching all users :: ${err}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong in the server. Please try again later.")


async def get_user_info(session: AsyncSession, user: UsersModel) -> UserResponseSchema:
    try:
        user_data = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User Data Not Found."
            )
        return user_data
    except SQLAlchemyError as err:
        print("Error while fetching user profile info :: ", err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong in the server. Please try again later.")


async def update_user(
        body: UserUpdateSchema,
        session: AsyncSession,
        user: UsersModel
) -> UserResponseSchema:
    current_user = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))
    if not current_user:
        raise HTTPException(
            atus_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Role validation
    if body.role_id is not None:
        current_user_role = await session.scalar(
            select(RolesModel).where(RolesModel.id == body.role_id)
        )
        if not current_user_role:
            raise HTTPException(
                atus_code=status.HTTP_400_BAD_REQUEST, detail="Role ID Doesn't Exist.")
        current_user.role_id = body.role_id

    # Name Validation
    if body.name is not None:
        if not body.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Name cannot be blank")
        current_user.name = body.name

    # Build dynamic uniqueness checks for values passed in payload
    clauses = []
    if body.username is not None:
        clauses.append(UsersModel.username == body.username)
    if body.email is not None:
        clauses.append(UsersModel.email == body.email)
    if body.phone_number is not None:
        clauses.append(UsersModel.phone_number == body.phone_number)

    existing_conflict = None
    if clauses:
        existing_conflict = await session.scalar(
            select(UsersModel)
            .where(UsersModel.id != user.id, or_(*clauses))
        )

    if existing_conflict:
        if body.username and existing_conflict.username == body.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists!")
        if body.email and existing_conflict.email == body.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email ID already exists!")
        if body.phone_number and existing_conflict.phone_number == body.phone_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists!")

    if body.username is not None:
        current_user.username = body.username
    if body.email is not None:
        current_user.email = body.email
    if body.phone_number is not None:
        current_user.phone_number = body.phone_number

    current_user.updated_at = datetime.now(timezone.utc)

    try:
        await session.commit()
        await session.refresh(current_user)
        return current_user
    except SQLAlchemyError as err:
        print(f"Database error during profile update: {err}")
        raise HTTPException(
            status_code=500, detail="Failed to update profile.")


async def change_password(
        session: AsyncSession,
        user: UsersModel,
        body: ChangePasswordSchema
):
    if (not re.fullmatch(
        PASSWORD_REGEX,
        body.new_password.strip()
    ) or not re.fullmatch(
        PASSWORD_REGEX,
        body.old_password
    )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_RULE_MESSAGE)

    if not verify_password(body.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter the Correct Old Password."
        )

    hashed_password = get_hashed_password(body.new_password)

    try:
        current_user = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        current_user.password = hashed_password

        await session.commit()
        await session.refresh(current_user)
        return current_user

    except SQLAlchemyError as err:
        await session.rollback()
        print(f"Error while changing password :: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong, try again later."
        )


async def delete_user(session: AsyncSession, user: UsersModel) -> None:
    try:
        current_user = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))
        if not (current_user):
            raise HTTPException(404, "User Not Found!")

        await session.delete(user)
        await session.commit()
        return None
    except SQLAlchemyError as err:
        await session.rollback()
        print("Error in deleting user profile.", err)
        raise HTTPException(
            500, "Something went wrong in the server, please try again later.")
