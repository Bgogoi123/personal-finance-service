import re
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta, timezone
import jwt
from src.users.schema import CreateUserSchema, UserDataResponse, LoginSchema
from src.users.models import UsersModel
from src.utils.auth.passwords import get_hashed_password, verify_password
from src.utils.settings import settings

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

def user_login(body: LoginSchema, session: Session):
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
  
  # Create Access Token
  access_token_expiry_time = datetime.now(timezone.utc) + timedelta(minutes = settings.ACCESS_TOKEN_EXPIRY_MINUTES)
  access_token = jwt.encode({"_id": str(user.id), "username": user.username, "exp": access_token_expiry_time}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  # Create Refresh Token
  refresh_token_expiry_days = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRY_DAYS)
  refresh_token = jwt.encode({"_id": str(user.id), "username": user.username, "exp": refresh_token_expiry_days }, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

  return { "access_token": access_token, "refresh_token": refresh_token }

def is_authenticated(request: Request, session: Session):
  auth_header = request.headers.get("authorization")
  if not auth_header or auth_header.startswith("Beared "):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized! Missing or invalid token format.")
  
  token = auth_header.split(" ")[1]
  data =jwt.decode(
    token, 
    settings.SECRET_KEY, 
    [settings.ALGORITHM], 
    options={ "verify_exp": False } # Prevents ExpiredSignatureError from being thrown.
  )
  user_id = data.get("_id")
  exp_time = data.get("exp")
  current_time = datetime.now(timezone.utc).timestamp()

  if current_time > exp_time:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized.")
  
  user = session.query(UsersModel).filter(UsersModel.id == user_id).first()
  if not user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized.")
  
  return user

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