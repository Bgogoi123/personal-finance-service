from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.utils.settings import settings

DB_URL = settings.DB_CONNECTION

# # The "create_async_engine" function from SQLAlchemy is used to create a database engine. 
# # It takes the database URL (DB_URL) as an argument, which specifies the database connection details.
engine = create_async_engine(DB_URL, echo=False)

# # The "async_sessionmaker" function configures the session to be used for database operations. 
# # The "autocommit" and "autoflush" parameters are set to False to ensure more control over transactions.
async_session_maker = async_sessionmaker(
  bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
)

# # The "declarative_base" function serves as the base class for declarative models that will be created later.
Base = declarative_base()

# # The "get_db" function sets up a context manager using the yield keyword. 
# # It creates a database session (db) using "sessionLocal" and yields it to the caller. 
# # After the execution within the context is completed, the finally block ensures that the session is closed.
async def get_db():
  async with async_session_maker() as db:
    try:
      yield db
    finally:
      await db.close()



# ==================================================#
#                      OLD CODE                     #
# ==================================================#

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base
# from src.utils.settings import settings

# DB_URL = settings.DB_CONNECTION

# # The "create_engine" function from SQLAlchemy is used 
# # to create a database engine. 
# # It takes the database URL (DB_URL) as an argument, 
# # which specifies the database connection details.
# engine = create_engine(DB_URL)

# # The "sessionmaker" function configures the session to 
# # be used for database operations. 
# # The "autocommit" and "autoflush" parameters are set to
# # False to ensure more control over transactions.
# sessionLocal = sessionmaker(autoflush=False, bind=engine)

# # The "declarative_base" function serves as the 
# # base class for declarative models that will be 
# # created later.
# Base = declarative_base()


# # The "get_db" function sets up a context manager 
# # using the yield keyword. 
# # It creates a database session (db) using 
# # "sessionLocal" and yields it to the caller. 
# # After the execution within the context is completed, 
# # the finally block ensures that the session is closed.
# def get_db():
#   db = sessionLocal()
#   try:
#     yield db
#   finally:
#     db.close()