import mysql.connector
import pandas as pd

class DatabaseOperations:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="kiit",
            database="employee_db"
        )
        self.cursor = self.conn.cursor()
    
    def get_departments(self):
        self.cursor.execute("SELECT * FROM Department")
        return pd.DataFrame(self.cursor.fetchall(), columns=['DeptID', 'DeptName'])
    
    def get_employees(self):
        self.cursor.execute("""
            SELECT e.*, d.DeptName 
            FROM Employee e 
            LEFT JOIN Department d ON e.DeptID = d.DeptID
        """)
        return pd.DataFrame(self.cursor.fetchall(), columns=['EmpID', 'EmpName', 'DeptID', 'JoinDate', 'BasicPay', 'DeptName'])
    
    def add_employee(self, emp_name, dept_id, join_date, basic_pay):
        try:
            # Check duplicate
            self.cursor.execute("""
                SELECT COUNT(*) FROM Employee 
                WHERE EmpName = %s AND DeptID = %s
            """, (emp_name, dept_id))
            if self.cursor.fetchone()[0] > 0:
                return False
            
            # AUTO_INCREMENT handles EmpID
            self.cursor.execute("""
                INSERT INTO Employee (EmpName, DeptID, JoinDate, BasicPay) 
                VALUES (%s, %s, %s, %s)
            """, (emp_name, dept_id, join_date, basic_pay))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return False
    
    def get_attendance(self):
        self.cursor.execute("""
            SELECT a.*, e.EmpName 
            FROM Attendance a 
            JOIN Employee e ON a.EmpID = e.EmpID
            ORDER BY a.AttDate DESC
        """)
        return pd.DataFrame(self.cursor.fetchall(), columns=['AttID', 'EmpID', 'AttDate', 'Status', 'EmpName'])
    
    def mark_attendance(self, emp_id, att_date, status):
        try:
            self.cursor.execute("""
                INSERT INTO Attendance (EmpID, AttDate, Status) 
                VALUES (%s, %s, %s)
            """, (emp_id, att_date, status))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return False
    
    def get_performance(self):
        self.cursor.execute("""
            SELECT p.*, e.EmpName 
            FROM Performance p 
            JOIN Employee e ON p.EmpID = e.EmpID
        """)
        return pd.DataFrame(self.cursor.fetchall(), columns=['PerfID', 'EmpID', 'Month', 'Score', 'Rating', 'EmpName'])
    
    def add_performance(self, emp_id, month, score):
        try:
            # Upsert logic
            self.cursor.execute("""
                SELECT PerfID FROM Performance 
                WHERE EmpID = %s AND Month = %s
            """, (emp_id, month))
            result = self.cursor.fetchone()

            if result:
                perf_id = result[0]
                self.cursor.execute("""
                    UPDATE Performance SET Score = %s WHERE PerfID = %s
                """, (score, perf_id))
            else:
                self.cursor.execute("""
                    INSERT INTO Performance (EmpID, Month, Score) 
                    VALUES (%s, %s, %s)
                """, (emp_id, month, score))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return False
    
    def get_payroll(self):
        self.cursor.execute("""
            SELECT py.*, e.EmpName 
            FROM Payroll py 
            JOIN Employee e ON py.EmpID = e.EmpID
        """)
        return pd.DataFrame(self.cursor.fetchall(), columns=['PayrollID', 'EmpID', 'Month', 'Basic', 'DA', 'HRA', 'Deductions', 'NetSalary', 'EmpName'])
    
    def generate_payroll(self, emp_id, month, basic, da, hra, deductions):
        net_salary = basic + da + hra - deductions
        try:
            self.cursor.execute("""
                INSERT INTO Payroll (EmpID, Month, Basic, DA, HRA, Deductions, NetSalary) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (emp_id, month, basic, da, hra, deductions, net_salary))
            self.conn.commit()
            return net_salary
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return None
    
    def get_analytics(self):
        analytics = {}
        
        # Metrics
        self.cursor.execute("SELECT COUNT(*) FROM Employee")
        analytics['total_emp'] = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT COALESCE(AVG(NetSalary), 0) FROM Payroll")
        analytics['avg_salary'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COALESCE(MAX(Score), 0) FROM Performance")
        analytics['top_score'] = self.cursor.fetchone()[0]
        
        self.cursor.execute("""
            SELECT COALESCE(SUM(CASE WHEN Status='Present' THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0)*100, 0) as pct 
            FROM Attendance
        """)
        analytics['present_pct'] = self.cursor.fetchone()[0]
        
        # Ratings
        self.cursor.execute("SELECT Rating, COUNT(*) as count FROM Performance GROUP BY Rating")
        result = self.cursor.fetchall()
        analytics['ratings'] = pd.DataFrame(result, columns=['Rating', 'count']) if result else pd.DataFrame()
        
        # Salary by emp
        self.cursor.execute("""
            SELECT e.EmpName, COALESCE(AVG(py.NetSalary), 0) as avg_salary 
            FROM Employee e LEFT JOIN Payroll py ON e.EmpID = py.EmpID 
            GROUP BY e.EmpID
        """)
        result = self.cursor.fetchall()
        analytics['salary_by_emp'] = pd.DataFrame(result, columns=['EmpName', 'avg_salary']) if result else pd.DataFrame()
        
        # Correlation
        self.cursor.execute("""
            SELECT p.Score, py.NetSalary, e.EmpName
            FROM Performance p JOIN Payroll py ON p.EmpID = py.EmpID AND p.Month = py.Month
            JOIN Employee e ON p.EmpID = e.EmpID
        """)
        result = self.cursor.fetchall()
        analytics['correlation'] = pd.DataFrame(result, columns=['Score', 'NetSalary', 'EmpName']) if result else pd.DataFrame()
        
        return analytics
    
    def insert_sample_data(self):
        try:
            # Departments
            self.cursor.execute("INSERT IGNORE INTO Department VALUES (1,'IT'),(2,'HR'),(3,'Finance')")
            
            # Employees (AUTO_INCREMENT EmpID)
            self.cursor.execute("""
                INSERT IGNORE INTO Employee (EmpName, DeptID, JoinDate, BasicPay) VALUES
                    ('Rahul Sharma', 1, '2024-01-15', 50000),
                    ('Priya Singh', 1, '2024-03-10', 45000),
                    ('Amit Kumar', 2, '2024-02-01', 40000)
            """)
            
            # Get actual EmpIDs
            self.cursor.execute("SELECT EmpID, EmpName FROM Employee")
            name_to_id = {name: emp_id for emp_id, name in self.cursor.fetchall()}
            
            rahul_id = name_to_id.get('Rahul Sharma')
            priya_id = name_to_id.get('Priya Singh')
            amit_id = name_to_id.get('Amit Kumar')
            
            if rahul_id and priya_id and amit_id:
                # Attendance
                self.cursor.execute("""
                    INSERT IGNORE INTO Attendance (EmpID, AttDate, Status) VALUES
                        (%s, '2025-01-01', 'Present'), (%s, '2025-01-02', 'Present'),
                        (%s, '2025-01-01', 'Present'), (%s, '2025-01-02', 'Absent')
                """, (rahul_id, rahul_id, priya_id, priya_id))
                
                # Performance
                self.cursor.execute("""
                    INSERT IGNORE INTO Performance (EmpID, Month, Score) VALUES
                        (%s, 'Jan-2025', 92), (%s, 'Jan-2025', 78), (%s, 'Jan-2025', 65)
                """, (rahul_id, priya_id, amit_id))
                
                # Payroll
                self.cursor.execute("""
                    INSERT IGNORE INTO Payroll (EmpID, Month, Basic, DA, HRA, Deductions, NetSalary) VALUES
                        (%s, 'Jan-2025', 50000, 5000, 10000, 2000, 58000),
                        (%s, 'Jan-2025', 45000, 4500, 9000, 1500, 54000)
                """, (rahul_id, priya_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            self.conn.rollback()
            return False