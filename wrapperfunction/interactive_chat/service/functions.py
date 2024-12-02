import datetime
import os
import pandas as pd
from datetime import datetime


file_path = os.path.join(os.path.dirname(__file__), f"vacations_forms.xlsx")


# Approve vacation by employee ID
def approve_vacation(employee_ID):
    df = pd.read_excel(file_path)
    
    # Check if the employee ID exists
    employee_row = df[(df['ID'] == employee_ID)]
    if employee_row.empty:
        return f"Employee with ID: {employee_ID}, not found."

    # Approve vacation for the employee
    df.loc[(df['ID'] == employee_ID), 'Status'] = 'Approved'
    df.loc[(df['ID'] == employee_ID), 'Comments'] = 'Approved by Manager'
    df.to_excel(file_path, index=False)  # Save changes to the Excel file

    return f"Vacation for Employee ID: {employee_ID} approved."

# Disapprove vacation by employee ID
def disapprove_vacation(employee_ID):
    df = pd.read_excel(file_path)
    
    # Check if the employee ID exists
    employee_row = df[(df['ID'] == employee_ID)]
    if employee_row.empty:
        return f"Employee with ID: {employee_ID}, not found."

    # Disapprove vacation for the employee
    df.loc[(df['ID'] == employee_ID), 'Status'] = 'Disapproved'
    df.loc[(df['ID'] == employee_ID), 'Comments'] = 'Disapproved by Manager'
    df.to_excel(file_path, index=False)  # Save changes to the Excel file

    return f"Vacation for Employee ID: {employee_ID}, disapproved."

# Pending vacation by employee ID
def pending_vacation(employee_ID):
    df = pd.read_excel(file_path)
    
    # Check if the employee ID exists
    employee_row = df[(df['ID'] == employee_ID)]
    if employee_row.empty:
        return f"Employee with ID: {employee_ID}, not found."

    # Set vacation to pending status for the employee
    df.loc[(df['ID'] == employee_ID), 'Status'] = 'Pending'
    df.loc[(df['ID'] == employee_ID), 'Comments'] = 'Edited by Manager'
    df.to_excel(file_path, index=False)  # Save changes to the Excel file

    return f"Vacation for Employee ID: {employee_ID}, set to Pending successfully."

# Show all requests from a specific cuoloms
def get_forms(coulomn_name,value):
    df = pd.read_excel(file_path)
    print(coulomn_name,value)
    department_df = df[df[coulomn_name] == value]
    if department_df.empty:
        return f"No Forms found for {coulomn_name}: {value}"
    
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
