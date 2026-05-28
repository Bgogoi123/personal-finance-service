from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from src.users.schema import CreateUserSchema, UserDataResponse
from src.users.models import UsersModel

def create_user(body: CreateUserSchema, session: Session) -> UserDataResponse | HTTPException:
  data = body.model_dump()

  isDuplicateEmail = session.query(UsersModel).filter(UsersModel.email == data["email"]).first()
  isDuplicatePhoneNumber = session.query(UsersModel).filter(UsersModel.phone_number == data["phone_number"]).first()
  isDuplicateUserName = session.query(UsersModel).filter(UsersModel.username == data["username"]).first()

  if(isDuplicateUserName):
    raise HTTPException(400, f"User with Username {data['username']} already exists.")
  elif(isDuplicateEmail):
    raise HTTPException(400, f"User with Email ID {data['email']} already exists.")
  elif(isDuplicatePhoneNumber):
    raise HTTPException(400, f"User with phone number {data["phone_number"]} already exists.")
  else:
    # Create an object of the UsersModel class, and pass this object to the database.
    user = UsersModel(
      name = data["name"],
      phone_number = data["phone_number"],
      email = data["email"],
      username = data["username"],
      password = data["password"],
      role_id = data["role_id"]
    )

    try:
      session.add(user)
      session.commit()
      session.refresh(user)

      return UserDataResponse.model_validate(user)

      # return {
      #   "status": 200, 
      #   "data": UserDataResponse.model_validate(user),
      #   "detail": "User Created Successfully."
      # }
    except SQLAlchemyError as e:
      session.rollback()
      print("Error in creating user: ", e)
      raise HTTPException(500, "Something went wrong on the server, please try again later.")

def get_user_by_id(id: int, session: Session) -> UserDataResponse | HTTPException:
  data = session.query(UsersModel).get(id)

  if(data):
    return data
    # return {
    #   "status": 200,
    #   "data": data,
    #   "detail": f"Information successfully fetched for user with ID {id}."
    # }
  
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