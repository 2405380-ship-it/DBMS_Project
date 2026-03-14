import streamlit as st
import plotly.express as px
from db_operations import DatabaseOperations
from datetime import date, datetime

st.set_page_config(page_title="Employee Performance & Payroll System", layout="wide", page_icon="")

@st.cache_resource
def get_db():
    return DatabaseOperations()

db = get_db()

st.title("Employee Performance & Payroll Analytics System")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Employees", "Attendance", "Performance", "Payroll", "Analytics"])

with tab1:
    st.header("Manage Employees")
    col1, col2 = st.columns([2,1])
    
    with col1:
        with st.form("add_employee"):
            st.subheader("Add New Employee")
            emp_name = st.text_input("Full Name").strip()
            dept_df = db.get_departments()
            
            if dept_df.empty:
                st.warning("No departments. Add sample data first!")
            else:
                dept_options = {row['DeptName']: row['DeptID'] for _, row in dept_df.iterrows()}
                dept_name = st.selectbox("Department", list(dept_options.keys()))
                dept_id = dept_options[dept_name]
                join_date = st.date_input("Join Date", value=date(2025, 1, 1))
                basic_pay = st.number_input("Basic Pay (₹)", min_value=0.0, value=40000.0, step=1000.0)
                
                submitted = st.form_submit_button("Add Employee")
                if submitted and emp_name:
                    if db.add_employee(emp_name, dept_id, join_date, basic_pay):
                        st.success("Employee added!")
                        st.rerun()
                    else:
                        st.error("Employee already exists in this department!")
                elif submitted:
                    st.error("Enter employee name!")
    
    with col2:
        st.subheader("Departments")
        st.dataframe(db.get_departments(), width='stretch')
    
    st.subheader("All Employees")
    st.dataframe(db.get_employees(), width='stretch')

with tab2:
    st.header("Attendance Tracking")
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("mark_attendance"):
            emp_df = db.get_employees()
            if emp_df.empty:
                st.warning("No employees!")
            else:
                emp_options = {row['EmpName']: row['EmpID'] for _, row in emp_df.iterrows()}
                emp_name = st.selectbox("Select Employee", [""] + list(emp_options.keys()))
                emp_id = emp_options.get(emp_name) if emp_name else None
                att_date = st.date_input("Date", value=date.today())
                status = st.selectbox("Status", ["Present", "Absent", "Leave"])
                
                submitted = st.form_submit_button("Mark Attendance")
                if submitted and emp_id:
                    if db.mark_attendance(emp_id, att_date, status):
                        st.success("Marked!")
                        st.rerun()
                    else:
                        st.error("Error marking!")
                elif submitted:
                    st.error("Select employee!")
    
    st.subheader("Attendance Records")
    st.dataframe(db.get_attendance(), width='stretch')

with tab3:
    st.header("Performance Evaluation")
    st.info("Auto-rating: 90+ Excellent, 75-89 Good, 60-74 Average, <60 Poor")
    
    with st.form("add_performance"):
        emp_df = db.get_employees()
        if emp_df.empty:
            st.warning("No employees!")
        else:
            emp_options = {row['EmpName']: row['EmpID'] for _, row in emp_df.iterrows()}
            emp_name = st.selectbox("Select Employee", [""] + list(emp_options.keys()))
            emp_id = emp_options.get(emp_name) if emp_name else None
            
            current_year = datetime.now().year
            month_options = [datetime(current_year, m, 1).strftime("%b-%Y") for m in range(1, 13)]
            month = st.selectbox("Month", month_options)
            score = st.slider("Score (0-100)", 0, 100, 80)
            
            submitted = st.form_submit_button("Submit")
            if submitted and emp_id:
                if db.add_performance(emp_id, month, score):
                    st.success("Added! Rating auto-assigned.")
                    st.rerun()
                else:
                    st.error("Error!")
            elif submitted:
                st.error("Select employee!")
    
    st.subheader("Performance Records")
    st.dataframe(db.get_performance(), width='stretch')

with tab4:
    st.header("Payroll Management")
    
    with st.form("generate_payroll"):
        emp_df = db.get_employees()
        if emp_df.empty:
            st.warning("No employees!")
        else:
            emp_options = {row['EmpName']: row['EmpID'] for _, row in emp_df.iterrows()}
            emp_name = st.selectbox("Select Employee", [""] + list(emp_options.keys()))
            emp_id = emp_options.get(emp_name) if emp_name else None
            month = st.selectbox("Month", ["Jan-2025", "Feb-2025", "Mar-2025"])
            
            basic = st.number_input("Basic (₹)", value=40000.0)
            da = st.number_input("DA (₹)", value=basic*0.1)
            hra = st.number_input("HRA (₹)", value=basic*0.2)
            deductions = st.number_input("Deductions (₹)", value=2000.0)
            net_salary = basic + da + hra - deductions
            st.info(f"**Net: ₹{net_salary:,.2f}**")
            
            submitted = st.form_submit_button("Generate")
            if submitted and emp_id:
                net = db.generate_payroll(emp_id, month, basic, da, hra, deductions)
                if net:
                    st.success(f"Generated! Net: ₹{net:,.2f}")
                    st.rerun()
                else:
                    st.error("Error!")
            elif submitted:
                st.error("Select employee!")
    
    st.subheader("Payroll Records")
    st.dataframe(db.get_payroll(), width='stretch')

with tab5:
    st.header("Analytics Dashboard")
    analytics = db.get_analytics()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Employees", analytics['total_emp'])
    col2.metric("Avg Salary", f"₹{analytics['avg_salary']:,.0f}")
    col3.metric("Top Score", analytics['top_score'])
    col4.metric("Attendance %", f"{analytics['present_pct']:.1f}%")
    
    if not analytics['ratings'].empty:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(analytics['ratings'], names='Rating', values='count', title="Ratings")
            st.plotly_chart(fig_pie, width='stretch')
        with col2:
            fig_bar = px.bar(analytics['salary_by_emp'], x='EmpName', y='avg_salary', title="Avg Salary")
            st.plotly_chart(fig_bar, width='stretch')
    
    if not analytics['correlation'].empty:
        fig_scatter = px.scatter(analytics['correlation'], x="Score", y="NetSalary", hover_name="EmpName", title="Score vs Salary")
        st.plotly_chart(fig_scatter, width='stretch')

st.markdown("---")
