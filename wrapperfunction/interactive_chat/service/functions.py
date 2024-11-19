import datetime
import os
import pandas as pd
from datetime import datetime


file_path = 'wrapperfunction\\interactive_chat\\service\\vacation_forms.xlsx'


# Approve vacation by employee name and department
def approve_vacation(employee_name, department_name):
    df = pd.read_excel(file_path)
    
    # Check if the employee exists in the specified department
    employee_row = df[(df['Employee Name'] == employee_name) & (df['Department'] == department_name)]
    if employee_row.empty:
        return f"Employee Name: {employee_name}, Department: {department_name} not found."

    # Approve vacation for the employee
    df.loc[(df['Employee Name'] == employee_name) & (df['Department'] == department_name), 'Status'] = 'Approved'
    df.loc[(df['Employee Name'] == employee_name) & (df['Department'] == department_name), 'Comments'] = 'Approved by Manager'
    df.to_excel(file_path, index=False)  # Save changes to the Excel file

    return f"Vacation for Employee Name: {employee_name}, Department: {department_name} approved."

# Disapprove vacation by employee name and department
def disapprove_vacation(employee_name, department_name):
    df = pd.read_excel(file_path)
    
    # Check if the employee exists in the specified department
    employee_row = df[(df['Employee Name'] == employee_name) & (df['Department'] == department_name)]
    if employee_row.empty:
        return f"Employee Name: {employee_name}, Department: {department_name} not found."

    # Disapprove vacation for the employee
    df.loc[(df['Employee Name'] == employee_name) & (df['Department'] == department_name), 'Status'] = 'Disapproved'
    df.loc[(df['Employee Name'] == employee_name) & (df['Department'] == department_name), 'Comments'] = 'Disapproved by Manager'
    df.to_excel(file_path, index=False)  # Save changes to the Excel file

    return f"Vacation for Employee Name: {employee_name}, Department: {department_name} disapproved."

# Pending vacation by employee name and department
def pending_vacation(employee_name, department_name):
    df = pd.read_excel(file_path)
    
    # Check if the employee exists in the specified department
    employee_row = df[(df['Employee Name'] == employee_name) & (df['Department'] == department_name)]
    if employee_row.empty:
        return f"Employee Name: {employee_name}, Department: {department_name} not found."

    # Set vacation to pending status for the employee
    df.loc[(df['Employee Name'] == employee_name) & (df['Department'] == department_name), 'Status'] = 'Pending'
    df.loc[(df['Employee Name'] == employee_name) & (df['Department'] == department_name), 'Comments'] = 'Edited by Manager'
    df.to_excel(file_path, index=False)  # Save changes to the Excel file

    return f"Vacation for Employee Name: {employee_name}, Department: {department_name} set to Pending successfully."

# Show all requests from a specific cuoloms
def get_forms(coulomn_name,value):
    df = pd.read_excel(file_path)
    print(coulomn_name,value)
    department_df = df[df[coulomn_name] == value]
    if department_df.empty:
        return f"No requests found for {coulomn_name}: {value}"
    
    return department_df.to_dict(orient='records')  # Return the department requests as a list of dictionaries

# Show all requests
def get_all_forms():
    df = pd.read_excel(file_path)
    if df.empty:
        return f"No requests found"
    return df.to_dict(orient='records')  # Return the department requests as a list of dictionaries


def fill_form(form_data):
    # Prepare data for DataFrame
    new_data = {
        "Type": form_data["type"],
        "Employee Name": form_data["employee_name"],
        "ID": form_data["employee_ID"],
        "Manager Name": form_data["manager_name"],
        "Department": form_data["employee_department"],
        "Start-date": form_data["start_date"],
        "End-date": form_data["end_date"],
        "Total days": (datetime.strptime(form_data["end_date"], '%Y-%m-%d') - 
                       datetime.strptime(form_data["start_date"], '%Y-%m-%d')).days,
        "Comments": form_data["comments"],
        "Status": "Pending"  # Initially empty
    }

    # Create a DataFrame from the new data
    new_data_df = pd.DataFrame([new_data])  # Wrap data in a list to create a DataFrame
    excel_file = file_path

    if os.path.exists(excel_file):
        # Read the existing file into a DataFrame
        existing_data = pd.read_excel(excel_file, sheet_name='Sheet1')

        # Append the new data to the existing data
        combined_data = pd.concat([existing_data, new_data_df], ignore_index=True)

        # Write the combined data back to the Excel file
        combined_data.to_excel(excel_file, sheet_name='Sheet1', index=False)
    else:
        # File does not exist, create a new file and write the header
        new_data_df.to_excel(excel_file, sheet_name='Sheet1', index=False)
