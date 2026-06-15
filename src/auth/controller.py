import re
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import  or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import jwt
from src.auth.schema import UserCreateSchema, UserUpdateSchema, UserResponseSchema, LoginSchema, RenewTokenResponseSchema
from src.auth.models import UsersModel
from src.utils.auth.passwords import get_hashed_password, verify_password
from src.utils.settings import settings
from src.utils.auth.authentication import create_auth_tokens
from src.roles.models import RolesModel

async def user_registration(body: UserCreateSchema, session: AsyncSession) -> UserResponseSchema:
  try:
    role_exists = await session.scalar(select(RolesModel.id).where(RolesModel.id == body.role_id))
  except SQLAlchemyError as err:
    print(f"Database error during role check: {err}")
    raise HTTPException(status_code=500, detail="Database communication failure.")
  
  if not role_exists:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="The assigned Role ID does not exist."
    )

  try:
    existing_user = await session.scalar(
      select(UsersModel).where(
        or_(
          UsersModel.username == body.username,
          UsersModel.email == body.email,
          UsersModel.phone_number == body.phone_number
        )
      )
    )
  except SQLAlchemyError as err:
    print(f"Database error during user duplicate check: {err}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Database communication failure."
    )

  if existing_user:

    if existing_user.username == body.username:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already exists! Please use a different username.")
    if existing_user.email == body.email:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email ID already exists! Please use a different email.")
    if existing_user.phone_number == body.phone_number:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, "Phone number already exists! Please use a different phone number.")

  hashed_password = get_hashed_password(body.password)
  
  new_user = UsersModel(
    name=body.name,
    phone_number=body.phone_number,
    email=body.email,
    username=body.username,
    password=hashed_password,
    role_id=body.role_id
  )

  try:
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user
      
  except IntegrityError as err:
    await session.rollback()
    error_details = str(err.orig).lower()
    print(f"Conflict race condition detected on registration: {err}")
    
    if "username" in error_details:
      raise HTTPException(status.HTTP_409_CONFLICT, "Username was taken right before submission.")
    elif "email" in error_details:
      raise HTTPException(status.HTTP_409_CONFLICT, "Email was registered right before submission.")
    elif "phone_number" in error_details:
      raise HTTPException(status.HTTP_409_CONFLICT, "Phone number was registered right before submission.")
    
    raise HTTPException(status.HTTP_409_CONFLICT, "User registration conflict occurred.")
      
  except SQLAlchemyError as err:
    await session.rollback()
    print(f"Unexpected error while creating user: {err}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
      detail="Something went wrong on the server, please try again later."
    )

async def user_login(body: LoginSchema, session: AsyncSession) -> LoginSchema:
  identifier = body.identifier.strip()

  if "@" in identifier:
    key = "email"
  elif re.match(r"^\+?1?\d{9,15}$", identifier):
    key = "phone_number"
  else:
    key = "username"
  
  # user = await session.query(UsersModel).filter(getattr(UsersModel, key) == identifier).first()
  user = await session.scalar(select(UsersModel).where(getattr(UsersModel, key) == identifier))
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid {key} or password.")
  
  if not verify_password(body.password, user.password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password.")
  
  tokens = await create_auth_tokens(user.id, session)
  return tokens

async def renew_access_token(refresh_token: str, session: AsyncSession) -> RenewTokenResponseSchema:
  try:
    # Cryptographically verify the refresh token
    data = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
  except jwt.PyJWKError as error:
    print("ERROR WHILE DECODING REFRESH TOKEN :: ", error)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or Expired Refresh Token.")
  
  # ensure if it's actually a Refresh token.
  if not data.get("refresh"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token.")
  
  user_id = data.get("_id")
  user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found.")

  # Generate Access Token
  return await create_auth_tokens(user.id, session, True)

async def get_profile_info(session: AsyncSession, user: UsersModel) -> UserResponseSchema:
  try:
    profile_data = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))

    if not profile_data:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="User Data Not Found."
      )
    return profile_data
  except SQLAlchemyError as err:
    print("Error while fetching user profile info :: ", err)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong in the server. Please try again later.")

async def update_profile(body: UserUpdateSchema, session: AsyncSession, user: UsersModel) -> UserResponseSchema:
  current_user = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))
  if not current_user:
    raise HTTPException(atus_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  
  # Role validation
  if body.role_id is not None:
    current_user_role = await session.scalar(select(RolesModel).where(RolesModel.id == body.role_id))
    if not current_user_role:
      raise HTTPException(atus_code=status.HTTP_400_BAD_REQUEST, detail="Role ID Doesn't Exist.")
    current_user.role_id = body.role_id

  # Name Validation
  if body.name is not None:
    if not body.name.strip():
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name cannot be blank")
    current_user.name = body.name

  # Build dynamic uniqueness checks for values passed in payload
  clauses = []
  if body.username is not None: clauses.append(UsersModel.username == body.username)
  if body.email is not None: clauses.append(UsersModel.email == body.email)
  if body.phone_number is not None: clauses.append(UsersModel.phone_number == body.phone_number)

  print("CLAUSES FORMED ::: ", clauses)

  existing_conflict = None
  if clauses:
    existing_conflict = await session.scalar(select(UsersModel).where(UsersModel.id != user.id, or_(*clauses)))
  
  if existing_conflict:
    if body.username and existing_conflict.username == body.username:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists!")
    if body.email and existing_conflict.email == body.email:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ID already exists!")
    if body.phone_number and existing_conflict.phone_number == body.phone_number:
      raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number already exists!")

  if body.username is not None: current_user.username = body.username
  if body.email is not None: current_user.email = body.email
  if body.phone_number is not None: current_user.phone_number = body.phone_number
  
  current_user.updated_at = datetime.now(timezone.utc)

  try:
    await session.commit()
    await session.refresh(current_user)
    return current_user
  except SQLAlchemyError as err:
    print(f"Database error during profile update: {err}")
    raise HTTPException(status_code=500, detail="Failed to update profile.")
  
async def delete_account(session: AsyncSession, user: UsersModel) -> None:
  try:
    current_user = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))
    if not (current_user):
      raise HTTPException(404, f"User Not Found!")
    
    await session.delete(user)
    await session.commit()
    return None
  except SQLAlchemyError as err:
    await session.rollback()
    print("Error in deleting user profile.")
    raise HTTPException(500, f"Something went wrong in the server, please try again later.")
