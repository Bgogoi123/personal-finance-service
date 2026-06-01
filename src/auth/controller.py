import re
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone
import jwt
from src.auth.schema import CreateUserSchema, UserDataResponse, LoginSchema
from src.auth.models import UsersModel
from src.utils.auth.passwords import get_hashed_password, verify_password
from src.utils.settings import settings
from src.utils.auth.authentication import create_auth_tokens

def user_registration(body: CreateUserSchema, session: Session) -> UserDataResponse | HTTPException:

  isDuplicateEmail = session.query(UsersModel).filter(UsersModel.email == body.email).first()
  isDuplicatePhoneNumber = session.query(UsersModel).filter(UsersModel.phone_number == body.phone_number).first()
  isDuplicateUserName = session.query(UsersModel).filter(UsersModel.username == body.username).first()

  if(isDuplicateUserName):
    raise HTTPException(400, f"User with Username {body.username} already exists! Please use a different username.")
  elif(isDuplicateEmail):
    raise HTTPException(400, f"User with Email ID {body.email} already exists! Please use a different email.")
  elif(isDuplicatePhoneNumber):
    raise HTTPException(400, f"User with phone number {body.phone_number} already exists! Please use a different phone number.")
  else:
    # convert password to hashed password
    hashed_password = get_hashed_password(body.password)

    # Create an object of the UsersModel class, and pass this object to the database.
    user = UsersModel(
      name = body.name,
      phone_number = body.phone_number,
      email = body.email,
      username = body.username,
      password = hashed_password,
      role_id = body.role_id
    )

    try:
      session.add(user)
      session.commit()
      session.refresh(user)

      return UserDataResponse.model_validate(user)
    
    except SQLAlchemyError as e:
      session.rollback()
      print("Error in creating user: ", e)
      raise HTTPException(500, "Something went wrong on the server, please try again later.")

def user_login(body: LoginSchema, session: Session,):
  identifier = body.identifier.strip()

  if "@" in identifier:
    key = "email"
  elif re.match(r"^\+?1?\d{9,15}$", identifier):
    key = "phone_number"
  else:
    key = "username"
  
  user = session.query(UsersModel).filter(getattr(UsersModel, key) == identifier).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid {key} or password.")
  
  if not verify_password(body.password, user.password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password.")
  
  tokens = create_auth_tokens(user.id, session)
  return tokens

def renew_access_token(refresh_token: str, session: Session):
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
  user = session.query(UsersModel).filter(UsersModel.id == user_id).first()

  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found.")

  # Generate Access Token
  return create_auth_tokens(user.id, session, True)
  








  token_data = jwt.decode(refresh_token, settings.SECRET_KEY, [settings.ALGORITHM])
  token_user_id = token_data.get("_id")

  print("Comparing IDs ::: ", id, token_user_id)

  if(token_user_id != id):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid User ID.")

  user = session.query(UsersModel).filter(UsersModel.id == id).first()

  if not user:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid User ID.")

  tokens = create_auth_tokens(user.id, session, True)
  return tokens

def get_user_by_id(id: int, session: Session) -> UserDataResponse | HTTPException:
  data = session.query(UsersModel).get(id)

  if(data):
    return data
  
  raise HTTPException(404, f"Couldn't fetch details of user with ID {id}.")

def update_user_by_id(id: int, body: CreateUserSchema, session: Session) -> UserDataResponse | HTTPException:
  data = body.model_dump()
  user = session.query(UsersModel).get(id)

  if not(user):
    raise HTTPException(404, f"No user found with ID {id}.")

  for key, value in data.items():
    setattr(user, key, value)
  setattr(user, "updated_at", datetime.now())

  try:
    session.commit()
    session.refresh(user)

    return UserDataResponse.model_validate(user)

    # return {
    #   "status": 200, 
    #   "data": UserDataResponse.model_validate(user),
    #   "detail": f"User with ID {id} was updated successfully."
    # }

  except SQLAlchemyError as err:
    print(f"Error while updating user with ID {id} :: ", err)
    raise HTTPException(500, "Something went wrong in the server, please try again later.")
  
def delete_user_by_id(id: int, session: Session) -> None | HTTPException:
  user = session.query(UsersModel).get(id)

  if not (user):
    raise HTTPException(404, f"User Not Found!")
  else:
    try:
      session.delete(user)
      session.commit()

      return None
      # return {
      #   "status": 200, 
      #   "data": user,
      #   "detail": f"User with ID {id} was deleted successfully."
      # }
    except SQLAlchemyError as err:
      print("Error in deleting user with ID {id}.")
      raise HTTPException(500, f"Something went wrong in the server, please try again later.")
