from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import foreign, relationship, sessionmaker

engine = create_engine("sqlite:///mydb.db", echo = True)


Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Integer)
    username = Column(String, unique=True)
    password = Column(String)
    user_detail = relationship('UserDetails', back_populates="user")
    
    def __init__(self, id: int, level: int, username: str, password: str):
        self.id = id
        self.level = level
        self.username = username
        self.password = password
                
    def __init__(self, level: int, username: str, password: str):
        self.level = level
        self.username = username
        self.password = password
        user = relationship('User', back_populates="user_details")

    def get_level_string(self) -> str:
        if self.level == 0:
            return "Administrator"
        elif self.level == 1:
            return "Member"
        elif self.level == 2:
            return "Developer"
        else:
            return "Not Identified"
        
    def __repr__(self):
        return f"({self.id}) {self.username} {self.password} {self.get_level_string()}"
    
class UserDetails(Base):
    __tablename__ = "user_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(User.id))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    
    def __init__(self):
        pass
    
    
# user = User(1, 0, "epicdreamer", "1234")
# user2 = User(0, "devasgames", "4321")
# user3 = User(1, "theblues996", "5678")

Base.metadata.create_all(bind=engine)

# insert into table
# session.add(user2)
# session.add(user3)
# session.commit()

# get
results = session.query(User).filter(User.level > 0).all()

def main() -> None:
    for result in results: print(str(result.username)+" is "+str(result.get_level_string()))

if __name__ == "__main__":
    main()