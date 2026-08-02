import re
from fastapi import HTTPException, Request, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import jwt

from src.auth.schema import ChangePasswordSchema, LoginSchema, RenewTokenResponseSchema, UserCreateSchema, UserResponseSchema, UserUpdateSchema
from src.auth.models import UsersModel, RefreshTokensModel
from src.utils.auth.passwords import get_hashed_password, verify_password
from src.utils.settings import settings
from src.utils.auth.authentication import create_auth_tokens
from src.roles.models import RolesModel

USERNAME_REGEX = r"^[a-zA-Z0-9_]+$"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
PASSWORD_REGEX = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
PHONE_REGEX = r"^\+?[0-9\s\-()]{7,15}$"

PASSWORD_RULE_MESSAGE = "Password should be atleast 8 characters in length, atleast one lower case letter, atleast one upper case letter, atleast one digit, atleast one special character (#?!@$%^&*-)."

async def user_registration(body: UserCreateSchema, session: AsyncSession) -> UserResponseSchema:
  # Validate Email, Phone Number, and Username.
  email = body.email.strip()
  password = body.password.strip()
  phone_number = body.phone_number.strip()
  user_name = body.username.strip()

  if not re.fullmatch(EMAIL_REGEX, email):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email!")
  
  if not re.fullmatch(PHONE_REGEX, phone_number):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Phone Number!")
  
  if not re.fullmatch(USERNAME_REGEX, user_name):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Username! Must contain only letters (uppercase or lowercase), numbers, and underscores (_)")
  
  if not re.fullmatch(PASSWORD_REGEX, password):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_RULE_MESSAGE)

  # Validate Role.
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

  # Check if user already exist. (Check agains email, phone_number, and username)
  try:
    existing_user = await session.scalar(
      select(UsersModel).where(
        or_(
          UsersModel.username == user_name,
          UsersModel.email == email,
          UsersModel.phone_number == phone_number
        )
      )
    )

  except SQLAlchemyError as err:
    print(f"Database error during user duplicate check: {err}")
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail="Database communication failure."
    )

  # If user exist, raise error against the identifier (email, phone_number, or username)
  if existing_user:
    if existing_user.username == user_name:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already exists! Please use a different username.")
    if existing_user.email == email:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email ID already exists! Please use a different email.")
    if existing_user.phone_number == phone_number:
      raise HTTPException(status.HTTP_400_BAD_REQUEST, "Phone number already exists! Please use a different phone number.")

  hashed_password = get_hashed_password(password)
  
  # Create new user object
  new_user = UsersModel(
    name=body.name,
    phone_number=phone_number,
    email=email,
    username=user_name,
    password=hashed_password,
    role_id=body.role_id
  )

  # Query for creating new user.
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

async def user_login(body: LoginSchema, session: AsyncSession, request: Request) -> LoginSchema:
  identifier = body.identifier.strip()

  if re.fullmatch(EMAIL_REGEX, identifier):
    key = "email"
  elif re.fullmatch(PHONE_REGEX, identifier):
    key = "phone_number"
  elif re.fullmatch(USERNAME_REGEX, identifier):
    key = "username"
  else:
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Identifier.")
  
  if not re.fullmatch(PASSWORD_REGEX, body.password.strip()):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_RULE_MESSAGE)

  try:
    user = await session.scalar(select(UsersModel).where(getattr(UsersModel, key) == identifier))
    if not user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid {key} or password.")
    
    # Delete expired tokens for the current user
    await session.execute(delete(RefreshTokensModel).where(RefreshTokensModel.user_id == user.id, RefreshTokensModel.expires_at < datetime.now(timezone.utc)))
    
    if not verify_password(body.password, user.password):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password.")

    tokens = await create_auth_tokens(user.id, session, request)
    return tokens
  
  except SQLAlchemyError as error: 
    print(f"Error while Login :: {error}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong on the server, please try again later.")

async def renew_access_token(refresh_token: str, user_id: str, session: AsyncSession, request: Request) -> RenewTokenResponseSchema:
  try:
    if user_id:
      # Check if user actually exist.
      user = await session.scalar(select(UsersModel).where(UsersModel.id == user_id))

      if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found.")

      # Delete all expired tokens for this user from DB.
      await session.execute(delete(RefreshTokensModel).where(RefreshTokensModel.user_id == user_id, RefreshTokensModel.expires_at < datetime.now(timezone.utc)))
      await session.commit()

    # Cryptographically verify the refresh token
    data = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    # Ensure if it's actually a Refresh token.
    if not data.get("refresh"):
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token.")
    
    # Ensure token belongs to the logged-in user.
    user_id_jwt = data.get("_id")
    if not user_id_jwt == user_id:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Token doesn't belong to the current user.")

    # Check if token exist in DB
    db_token = await session.scalar(select(RefreshTokensModel).where(RefreshTokensModel.token == refresh_token, RefreshTokensModel.user_id == user.id))
    if not db_token:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has been revoked or logged out.")
    
    # Generate Access Token
    return await create_auth_tokens(user.id, session, request, True, refresh_token)

  except jwt.PyJWKError as error:
    print("Error while decoding refresh token :: ", error)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh Token.")
  
  except jwt.ExpiredSignatureError as expErr:
    print("Error while decoding refresh token :: ", expErr)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh Token has expired. Please log in again.")
  
  except SQLAlchemyError as err: 
    await session.rollback()
    print(f"Error in deleting tokens while renewing-access-token : {err}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server. Please try again later.")

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
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in the server. Please try again later.")

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

async def logout(refresh_token: str, session: AsyncSession, user: UsersModel):
  if not refresh_token:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Refresh Token.")
  
  try:
    token = await session.scalar(select(RefreshTokensModel).where(RefreshTokensModel.token == refresh_token, RefreshTokensModel.user_id == user.id))
    if not token:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Refresh Token!")
    
    await session.delete(token)
    await session.commit()
    return None
  
  except SQLAlchemyError as error:
    print(f"Error while Logout :: {error}")
    raise HTTPException(500, f"Something went wrong in the server, please try again later.")

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
    print("Error in deleting user profile.", err)
    raise HTTPException(500, f"Something went wrong in the server, please try again later.")

async def change_password(session: AsyncSession, user: UsersModel, body: ChangePasswordSchema):
  if not re.fullmatch(PASSWORD_REGEX, body.new_password.strip()) or not re.fullmatch(PASSWORD_REGEX, body.old_password):
  # if not re.fullmatch(PASSWORD_REGEX, body.new_password.strip()):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=PASSWORD_RULE_MESSAGE)

  if not verify_password(body.old_password, user.password):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter the Correct Old Password.")
  
  hashed_password = get_hashed_password(body.new_password)

  try:
    current_user = await session.scalar(select(UsersModel).where(UsersModel.id == user.id))
    if not current_user:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
  
    current_user.password = hashed_password

    await session.commit()
    await session.refresh(current_user)
    return current_user

  except SQLAlchemyError as err:
    await session.rollback()
    print(f"Error while changing password :: {err}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong, try again later.")
  