import mysql.connector

def initialize_database():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="kiit",
    )
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS employee_db")
    conn.database = "employee_db"

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Department (
        DeptID INT PRIMARY KEY,
        DeptName VARCHAR(50) NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Employee (
        EmpID INT AUTO_INCREMENT PRIMARY KEY,
        EmpName VARCHAR(50),
        DeptID INT,
        JoinDate DATE,
        BasicPay DECIMAL(10,2),
        FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Attendance (
        AttID INT AUTO_INCREMENT PRIMARY KEY,
        EmpID INT,
        AttDate DATE,
        Status ENUM('Present','Absent','Leave'),
        FOREIGN KEY (EmpID) REFERENCES Employee(EmpID)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Performance (
        PerfID INT AUTO_INCREMENT PRIMARY KEY,
        EmpID INT,
        Month VARCHAR(20),
        Score INT,
        Rating VARCHAR(20),
        FOREIGN KEY (EmpID) REFERENCES Employee(EmpID)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Payroll (
        PayrollID INT AUTO_INCREMENT PRIMARY KEY,
        EmpID INT,
        Month VARCHAR(20),
        Basic DECIMAL(10,2),
        DA DECIMAL(10,2),
        HRA DECIMAL(10,2),
        Deductions DECIMAL(10,2),
        NetSalary DECIMAL(10,2),
        FOREIGN KEY (EmpID) REFERENCES Employee(EmpID)
    );
    """)

    # Drop the trigger if it exists (safe to run repeatedly)
    cursor.execute("DROP TRIGGER IF EXISTS AutoRating")

    # Create a trigger that sets the performance rating based on score.
    # Note: mysql-connector-python does not support the client-side DELIMITER directive,
    # so we send the trigger definition as a single statement.
    trigger_sql = """
    CREATE TRIGGER AutoRating
    BEFORE INSERT ON Performance
    FOR EACH ROW
    BEGIN
        IF NEW.Score >= 90 THEN
            SET NEW.Rating = 'Excellent';
        ELSEIF NEW.Score >= 75 THEN
            SET NEW.Rating = 'Good';
        ELSEIF NEW.Score >= 60 THEN
            SET NEW.Rating = 'Average';
        ELSE
            SET NEW.Rating = 'Poor';
        END IF;
    END
    """
    cursor.execute(trigger_sql)

    cursor.execute("""
    INSERT IGNORE INTO Department (DeptID, DeptName) VALUES
    (1, 'HR'),
    (2, 'Finance'),
    (3, 'Engineering');
    """)

    cursor.execute("""
    INSERT IGNORE INTO Employee (EmpName, DeptID, JoinDate, BasicPay) VALUES
    ('Alice Johnson', 1, '2020-01-15', 50000.00),
    ('Bob Smith', 2, '2019-03-10', 60000.00),
    ('Charlie Brown', 3, '2021-07-23', 55000.00);
    """)

    cursor.execute("""
    INSERT IGNORE INTO Attendance (EmpID, AttDate, Status) VALUES
    (1, '2025-01-01', 'Present'),
    (2, '2025-01-01', 'Absent'),
    (3, '2025-01-01', 'Leave');
    """)

    cursor.execute("""
    INSERT IGNORE INTO Performance (EmpID, Month, Score) VALUES
    (1, 'January-2025', 85),
    (2, 'January-2025', 92),
    (3, 'January-2025', 70);
    """)

    cursor.execute("""
    INSERT IGNORE INTO Payroll (EmpID, Month, Basic, DA, HRA, Deductions, NetSalary) VALUES
    (1, 'January-2025', 50000.00, 10000.00, 5000.00, 2000.00, 63000.00),
    (2, 'January-2025', 60000.00, 12000.00, 6000.00, 3000.00, 75000.00),
    (3, 'January-2025', 55000.00, 11000.00, 5500.00, 2500.00, 69000.00);
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized with 3 sample records each!")

if __name__ == "__main__":
    initialize_database()
