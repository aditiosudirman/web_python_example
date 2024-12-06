import psycopg2
import bcrypt
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dbname_var = "hotel"
user_var = "postgres"
password_var = "admin"

# Function to create a new database
def create_database():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=user_var,
            password=password_var,
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        # Check if the 'hotel' database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'hotel'")
        if cur.fetchone():
            print("Database 'hotel' already exists.")
        else:
            cur.execute("CREATE DATABASE hotel;")
            print("Database 'hotel' created successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

def create_tables():
    user.check_table()
    user_details.check_table()


class Web:

    def __init__(self):
        self.title = "My Website"

    def create_db(self):
        create_database()
        create_tables()

class User:

    def __init__(self):
        pass

    def check_table(self):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # Check if 'user' table exists
            cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'user'
                    );
                """)
            if cur.fetchone()[0]:
                print("Table 'user' already exists.")
            else:
                query = """
                        CREATE TABLE IF NOT EXISTS "user" (
                            id SERIAL PRIMARY KEY,
                            level INTEGER NOT NULL,
                            username VARCHAR(20) NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        );
                    """
                cur.execute(query)
                conn.commit()
                print("Table 'user' created successfully in the 'hotel' database!")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def add(self, level, username, password):
        password_encode = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            query = """
                INSERT INTO "user" (level, username, password)
                VALUES (%s, %s, %s)
            """
            cur.execute(query, (level, username, password_encode))
            conn.commit()
            print("New 'user' successfully added")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def remove(self, username):
        try:
            conn = psycopg2.connect(
                dbname="hotel",
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            query = """
                DELETE FROM "user"
                WHERE username = %s
            """
            cur.execute(query, (username,))
            conn.commit()

            if cur.rowcount > 0:
                print(f"User '{username}' successfully removed!")
            else:
                print(f"User '{username}' not found.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def update(self, username, new_level=None, new_password=None):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            updates = []
            params = []

            if new_level is not None:
                updates.append("level = %s")
                params.append(new_level)
            if new_password is not None:
                password_encode = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                updates.append("password = %s")
                params.append(password_encode)

            if not updates:
                print("No updates provided.")
                return

            query = f"""
                UPDATE "user"
                SET {', '.join(updates)}
                WHERE username = %s
            """
            params.append(username)
            cur.execute(query, tuple(params))
            conn.commit()

            if cur.rowcount > 0:
                print(f"User '{username}' successfully updated!")
            else:
                print(f"User '{username}' not found.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def get_by_id(self, user_id):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # Fetch user data by id
            query = """
                SELECT id, level, username, password FROM "user"
                WHERE id = %s
            """
            cur.execute(query, (user_id,))
            user_data = cur.fetchone()

            if user_data:
                print(f"User found: ID={user_data[0]}, Level={user_data[1]}, Username={user_data[2]}")
                return user_data
            else:
                print(f"User with ID {user_id} not found.")
                return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def get_by_username(self, username):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # Fetch user data by id
            query = """
                SELECT id, level, username, password FROM "user"
                WHERE username = %s
            """
            cur.execute(query, (username,))
            user_data = cur.fetchone()

            if user_data:
                print(f"User found: ID={user_data[0]}, Level={user_data[1]}, Username={user_data[2]}")
                return user_data
            else:
                print(f"User with username {username} not found.")
                return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cur.close()
            conn.close()

class UserDetails:

    def __init__(self):
        pass

    def check_table(self):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # Check if 'user_details' table exists
            cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'user_details'
                        );
                    """)
            if cur.fetchone()[0]:
                print("Table 'user_details' already exists.")
            else:
                query = """
                            CREATE TABLE IF NOT EXISTS user_details (
                                detail_id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL,
                                first_name VARCHAR(50),
                                last_name VARCHAR(50),
                                email VARCHAR(100),
                                phone VARCHAR(20),
                                FOREIGN KEY (user_id) REFERENCES "user" (id) ON DELETE CASCADE
                            );
                        """
                cur.execute(query)
                conn.commit()
                print("Table 'user_details' created successfully in the 'hotel' database!")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def add(self, user_id, first_name, last_name, email, phone=None):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            query = """
                INSERT INTO user_details (user_id, first_name, last_name, email, phone)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (user_id, first_name, last_name, email, phone))
            conn.commit()
            print("New 'user_details' successfully added!")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def remove(self, user_id):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            query = """
                DELETE FROM user_details
                WHERE user_id = %s
            """
            cur.execute(query, (user_id,))
            conn.commit()

            if cur.rowcount > 0:
                print(f"Details for user with ID {user_id} successfully removed!")
            else:
                print(f"User with ID {user_id} not found in 'user_details'.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def update(self, user_id, first_name=None, last_name=None, email=None, phone=None):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            updates = []
            params = []

            if first_name is not None:
                updates.append("first_name = %s")
                params.append(first_name)
            if last_name is not None:
                updates.append("last_name = %s")
                params.append(last_name)
            if email is not None:
                updates.append("email = %s")
                params.append(email)
            if phone is not None:
                updates.append("phone = %s")
                params.append(phone)

            if not updates:
                print("No updates provided.")
                return

            query = f"""
                UPDATE user_details
                SET {', '.join(updates)}
                WHERE user_id = %s
            """
            params.append(user_id)
            cur.execute(query, tuple(params))
            conn.commit()

            if cur.rowcount > 0:
                print(f"Details for user with ID {user_id} successfully updated!")
            else:
                print(f"User with ID {user_id} not found.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            cur.close()
            conn.close()

    def get_by_id(self, user_id):
        try:
            conn = psycopg2.connect(
                dbname=dbname_var,
                user=user_var,
                password=password_var,
                host="localhost",
                port="5432"
            )
            cur = conn.cursor()

            # Fetch user details by user_id
            query = """
                SELECT detail_id, user_id, first_name, last_name, email, phone 
                FROM user_details
                WHERE user_id = %s
            """
            cur.execute(query, (user_id,))
            user_details = cur.fetchone()

            if user_details:
                print(f"User Details found: ID={user_details[0]}, User ID={user_details[1]}, Name={user_details[2]} {user_details[3]}, Email={user_details[4]}, Phone={user_details[5]}")
                return user_details
            else:
                print(f"User details for ID {user_id} not found.")
                return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        finally:
            cur.close()
            conn.close()




user = User()
user_details = UserDetails()
web = Web()