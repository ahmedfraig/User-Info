from datetime import datetime
import os
import pyodbc


def insert_data_from_file(fileName,insertFunction,conn,cursor):
    if os.path.exists("./" + fileName):
        with open("./" + fileName, "r") as file:
            lines = file.readlines()
            insertFunction(lines,cursor)
            # Commit the transaction
            conn.commit()

def user_table_insert(lines,cursor):
    if len(lines) > 1:
        for line in lines[1:]:
            # Skip empty lines
            if line.strip():
                userID, firstName, lastName, departmentID, age, gender, year_of_birth = line.strip().split(',')
                departmentID = int(departmentID)
                userID = int(userID)
                age = int(age)
                year_of_birth = int(year_of_birth)
                # Insert data into the table if id not in table
                cursor.execute(f"SELECT COUNT(*) FROM Users WHERE UserID = ?", userID)
                if cursor.fetchone()[0] == 0:
                    insert_query = """
                    INSERT INTO Users (UserID, FirstName, LastName, DepartmentID, Age, Gender, Year_of_birth)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(insert_query, (userID, firstName, lastName, departmentID, age, gender, year_of_birth))
                else:
                    print(f"User ID: {userID} in table")
            else:
                print("File is empty")

def department_table_insert(lines,cursor):
    if len(lines) > 1:
        for line in lines[1:]:
            # Skip empty lines
            if line.strip():
                departmentID, departmentName= line.strip().split(',')
                departmentID = int(departmentID)
                # Insert data into the table if id not in table
                cursor.execute(f"SELECT COUNT(*) FROM Departments WHERE DepartmentID = ?", departmentID)
                if cursor.fetchone()[0] == 0:
                    insert_query = """
                    INSERT INTO Departments (DepartmentID, DepartmentName)
                    VALUES (?, ?)
                    """
                    cursor.execute(insert_query, (departmentID, departmentName))
                else:
                    print(f"Department ID: {departmentID} in table")
            else:
                print("File is empty")

def insert_into_sql_server():
    connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-F9SAMSI\SQLEXPRESSS;"  
    "DATABASE=AdventureWorks2022;"  
    "Trusted_Connection=yes;" 
    )

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    create_table = """
    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'Departments'
    )
    BEGIN
        CREATE TABLE Departments (
            DepartmentID INT PRIMARY KEY,
            DepartmentName NVARCHAR(50),
        )
    END

    IF NOT EXISTS (
        SELECT * FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_NAME = 'Users'
    )
    BEGIN
        CREATE TABLE Users (
            UserID INT PRIMARY KEY,
            FirstName NVARCHAR(50),
            LastName NVARCHAR(50),
            DepartmentID INT,
            Age INT,
            Gender NVARCHAR(10),
            Year_of_birth INT,
            FOREIGN KEY (DepartmentID) REFERENCES Departments (DepartmentID)
        )
    END
    """
    cursor.execute(create_table)
    conn.commit()
    insert_data_from_file("department info.txt",department_table_insert,conn,cursor)
    insert_data_from_file("user info.txt",user_table_insert,conn,cursor)
    cursor.close()
    conn.close()

# dealing with files
def read_from_file(fileName,read_to,firstStatement,departments):
    if os.path.exists("./"+ fileName):
        with open("./"+ fileName, "r") as file:
            lines = file.readlines()
            if len(lines) > 1:
                read_to(departments,lines)
            else:
                with open ("./"+ fileName, "w") as f:
                    f.write(firstStatement)
    else:
        with open("./"+ fileName, 'w'):
            pass

def read_from_userInfo_file_to_dictionary(departments, lines):
    for line in lines[1:]:
        words = line.strip().split(',')
        userID, firstName, lastName, departmentID, age, gender, year_of_birth = words
        departmentID = int(departmentID)
        userID = int(userID)
        if departmentIDNotInDepartments(departmentID):
            departments[departmentID] = ['', {}]
        departments[departmentID][1][userID] = f"{firstName},{lastName},{age},{gender},{year_of_birth}"

def read_from_departmentInfo_to_dictionary(departments, lines):
    for line in lines[1:]:
        words = line.strip().split(',')
        departmentID, departmentName = words
        departmentID = int(departmentID)
        if departmentIDNotInDepartments(departmentID):
            departments[departmentID][0] = ['']
        departments[departmentID][0] = departmentName

def write_to_file(fileName,line):
    with open("./"+ fileName, "a") as f:
        f.write(line)
#-----------------------------------------------------
#-----------------------------------------------------
# validations functions
def get_valid_input(prompt, validation_func, error_message):
    while True:
        user_input = input(prompt)
        if validation_func(user_input):
            return user_input
        print(error_message)

def is_alpha(value):
    return value.isalpha()

def is_valid_gender(value):
    return value.isdigit() and value in {"1", "2"}

def is_valid_option(value):
    return value.isdigit() and value in {"1", "2", "3", "4", "5"}

def is_valid_id(value):
    return value.isdigit() and len(value) == 3

def is_valid_year_of_birth(value):
    current_year = datetime.now().year
    if value.isdigit() and len(value) == 4:
        return current_year - int(value) >= 18
    return False

def id_not_in_use(value):
    value = int(value)
    if len(departments) != 0 :
        for departmentID, items in departments.items():
            for item in items:
                if isinstance(item, dict) and value in item:
                    return [False , departmentID]
    return [True , value]

def departmentIDNotInDepartments(value):
    return int(value) not in departments

def check_if_first_item_in_list_isNone (departmentID):
    return not departments.get(departmentID)
#-----------------------------------------------------
#-----------------------------------------------------

# Search for a specific user by their User ID
def search_for_specific_user():
    userID = int(get_valid_input(
    "Please enter ID you want (3 numbers only): ",
    lambda x: is_valid_id(x),
    "Enter a valid ID with exactly 3 digits."
    ))
    find_user = id_not_in_use(userID)
    if not find_user[0]:
        line = departments[find_user[1]][1][userID]
        departmentName = departments[find_user[1]][0]
        words = line.strip().split(',')
        firstName, LastName,age,gender,year_of_birth = words
        print(f"Data of user: {userID} is\nFinst Name: {firstName}\nLast Name: {LastName}\nAge: {age}\nGendre: {gender}\nYear of birth: {year_of_birth}\nDepartment Name: {departmentName}")
    else:
        print(f"User with ID: {userID} not found")
#-----------------------------------------------------
#-----------------------------------------------------

#Display
def display():
    if os.path.exists("./user info.txt") :
        with open("./user info.txt", "r") as file:
            lines = file.readlines()
            if len(lines) > 1:
                for line in lines[1:]:
                    words = line.strip().split(',')
                    userID, firstName, lastName, departmentID, age, gender, year_of_birth = words
                    departmentID = int(departmentID)
                    print(f"User ID: {userID}, First Name: {firstName}, Last Name: {lastName}, Age: {age}, Gendre: {gender}, Year of birth: {year_of_birth}, Department ID: {departmentID}, Department Name: {departments[departmentID][0]}")
            else:
                print("File is Empty")
    else:
        print("File User Info doesn't exist")
#-----------------------------------------------------
#-----------------------------------------------------

#take user option
def userOption():
    while True:
        user_option = get_valid_input(
            "Enter your option(1,2,3,4,5):\n1- Enter new data\n2- Display data\n3- Search for a user\n4- Insert Into sql server\n5- Exit\nEnter your option: ",
            is_valid_option,"please,Enter 1,2,3,4 or 5 for option")
        read_from_file("user info.txt",read_from_userInfo_file_to_dictionary,"userID,firstName,lastName,departmentID,age,gendre,year of birth\n",departments)
        read_from_file("department info.txt",read_from_departmentInfo_to_dictionary,"departmentID,departmentName\n",departments)
        if user_option == "1":
            userInfo()
        elif user_option == "2":
            display()
        elif user_option == "3":
            search_for_specific_user()
        elif user_option == "4":
            insert_into_sql_server()
        else:
            return
#-----------------------------------------------------
#-----------------------------------------------------

def userInfo():
    # Get validated inputs
    departmentID = int(get_valid_input(
        "Please enter department ID (3 numbers only): ",
        lambda x: is_valid_id(x) and id_not_in_use(x)[0],
        "Enter a valid ID with exactly 3 digits and ensure it's unique."
    ))

    if check_if_first_item_in_list_isNone(departmentID):
        departmentName = get_valid_input(
            "Please enter your department name (alphabets only): ",
            is_alpha, "Enter alphabets only for department name."
        )

    userID = int(get_valid_input(
        "Please enter your ID (3 numbers only): ",
        lambda x: is_valid_id(x) and id_not_in_use(x)[0] and departmentIDNotInDepartments(x),
        "Enter a valid ID with exactly 3 digits and ensure it's unique."
    ))

    firstName = get_valid_input(
        "Please enter your first name (alphabets only): ",
        is_alpha, "Enter alphabets only for first name."
    )

    lastName = get_valid_input(
        "Please enter your last name (alphabets only): ",
        is_alpha, "Enter alphabets only for last name."
    )

    genderNo = get_valid_input(
        "Please enter 1 if male and 2 if female: ",
        is_valid_gender, "Enter 1 or 2 for gender."
    )

    year_of_birth = int(get_valid_input(
        "Please enter your year of birth (shoud be 4 digits and you should not be less than 18): ",
        is_valid_year_of_birth, "Enter 4 digits and you should not be less than 18."
    ))

    age = datetime.now().year - year_of_birth

    gender = "male" if genderNo == "1" else "female"
#-----------------------------------------------------
#-----------------------------------------------------

    #write to file
    line = f"{userID},{firstName},{lastName},{departmentID},{age},{gender},{year_of_birth}\n"
    write_to_file("user info.txt", line)
#-----------------------------------------------------
#-----------------------------------------------------

    # Write to dictionary
    if departmentIDNotInDepartments(departmentID):
        departments[departmentID] = ['', {}]
        departments[departmentID][0] = departmentName
        line = f"{departmentID},{departmentName}\n"
        write_to_file("department info.txt", line)
    departments[departmentID][1][userID] = f"{firstName},{lastName},{age},{gender},{year_of_birth}"

departments = {}
userOption()