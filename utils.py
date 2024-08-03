
import openpyxl
from datetime import datetime


# Initialize the Excel workbook and sheet
def initialize_excel():
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Queries and Links"
    sheet.append(["Question Number", "Query", "Link"])  # Add headers
    return workbook, sheet


# Get the current timestamp
def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
