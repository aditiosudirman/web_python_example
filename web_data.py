from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, text
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash, check_password_hash
import os

db_use = 'postgresql'

if db_use == 'postgresql':
    # PostgreSQL connection details
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "192.168.11.216")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "mydb")
    ADMIN_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"

    # Check and create the database if it doesn't exist
    try:
        admin_engine = create_engine(ADMIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
        with admin_engine.connect() as conn:
            # Check if the database exists
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": POSTGRES_DB}
            ).fetchone()

            if not result:
                print(f"Database '{POSTGRES_DB}' does not exist. Creating it...")
                conn.execute(text(f"CREATE DATABASE {POSTGRES_DB}"))
                print(f"Database '{POSTGRES_DB}' created successfully.")

    except OperationalError as e:
        print(f"Error connecting to PostgreSQL: {e}")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
else:
    DATABASE_URL="sqlite:///mydb.db"

# Create Database engine and sessionmaker
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
print("This is Database URL: "+DATABASE_URL)
# Declarative base
Base = declarative_base()

class Web:
    def __init__(self):
        self.title = "My Website"


# User Model
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    user_details = relationship('UserDetails', back_populates='user', uselist=False)

    def get_level_string(self) -> str:
        levels = {0: "Administrator", 1: "Member", 2: "Developer"}
        return levels.get(self.level, "Not Identified")

    def __repr__(self):
        return f"({self.id}) {self.username} {self.get_level_string()}"


# UserDetails Model
class UserDetails(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    user = relationship('User', back_populates='user_details')

    def __repr__(self):
        return f"({self.id}) {self.first_name} {self.last_name} {self.email}"


# Create tables
Base.metadata.create_all(bind=engine)

# Web instance
web = Web()

def add_user(level, username, password, first_name, last_name, email, phone=None):
    """Adds a new user with associated details."""
    session = Session()  # Create a new session

    try:
        # Check for existing username or email
        if session.query(User).filter(User.username == username).first():
            raise ValueError("Username already exists.")
        if session.query(UserDetails).filter(UserDetails.email == email).first():
            raise ValueError("Email already exists.")

        # Hash the password before saving it
        hashed_password = generate_password_hash(password)

        # Create and save the user and user details in a single transaction
        new_user = User(level=level, username=username, password=hashed_password)
        session.add(new_user)
        session.commit()  # Commit user to get ID

        new_user_detail = UserDetails(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )
        session.add(new_user_detail)
        session.commit()

    finally:
        session.close()  # Close the session when done

def login_user(username, password):
    """Logs in a user by verifying username and password."""
    session = Session()  # Create a new session

    try:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            raise ValueError("Wrong username.")
        if not check_password_hash(user.password, password):
            raise ValueError("Wrong password.")
        return user.id

    finally:
        session.close()  # Close the session when done
