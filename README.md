# Rizz ORM

Rizz ORM is a lightweight Object-Relational Mapping (ORM) system designed to provide a Pythonic interface for interacting with SQL databases. It allows developers to define their database schema in Python code and perform database operations without writing raw SQL queries.

## Features

- **Python Class-Based Schema Definition**: Define your database schema using Python classes and attributes.
- **CRUD Operations**: Easily create, read, update, and delete records in your SQLite database.
- **Automatic SQL Generation**: SQL queries for table creation and data manipulation are generated automatically.
- **Type Mapping**: Python data types are automatically mapped to corresponding SQLite column types.
- **Foreign Key Support**: Define relationships between tables using foreign keys.
- **Connection Management**: Manage database connections and execute queries through a single `Database` class.

## Installation

To install Rizz ORM, you can simply copy the `orm.py` file into your project directory. As it uses standard Python libraries (`sqlite3` and `inspect`), no additional dependencies are required.

## Usage

Below is an example of how to use Rizz ORM to define a database schema, connect to a database, and perform CRUD operations.

### Defining the Schema

```python
from orm import Database, Table, Column, ForeignKey

class User(Table):
    username = Column(str)
    email = Column(str)

class Post(Table):
    title = Column(str)
    content = Column(str)
    author = ForeignKey(User)
```

### Connecting to a Database

```python
db = Database('path/to/database.db')
```

### Creating Tables

```python
db.create(User)
db.create(Post)
```

### Inserting Records

```python
user = User(username='johndoe', email='john@example.com')
db.save(user)

post = Post(title='Hello World', content='This is my first post.', author=user)
db.save(post)
```

### Retrieving Records

```python
user = db.get(User, id=1)
print(user.username, user.email)

post = db.get(Post, id=1)
print(f"Post: {post.asdict}")
```

### Updating Records

```python
user = db.get(User, id=1)
user.email = 'newemail@example.com'
db.update(user)
```

### Deleting Records

```python
db.delete(User, id=1)
```

### Listing All Records

```python
users = db.all(User)
for user in users:
    print(user.username, user.email)
```

## Contributing

Contributions to improve Rizz ORM are welcome. Please ensure to follow best practices and add unit tests for any new features or bug fixes.

## License

Rizz ORM is open-source software licensed under the MIT License.

Please note that this ORM is a basic example and may not cover all use cases or complex scenarios. For production environments, consider using more established ORM libraries such as SQLAlchemy or Django ORM.
