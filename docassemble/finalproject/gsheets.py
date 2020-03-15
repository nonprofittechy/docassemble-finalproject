import gspread
import json
from docassemble.base.util import get_config
from oauth2client.service_account import ServiceAccountCredentials
credential_info = json.loads(get_config('google').get('service account credentials'), strict=False)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
__all__ = ['read_sheet', 'append_with_column_labels', 'append_to_sheet', 'get_column_headings']

def read_sheet(sheet_name, worksheet_index=0):
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = gspread.authorize(creds)
  sheet = client.open(sheet_name).get_worksheet(worksheet_index)
  return sheet.get_all_records()

def append_to_sheet(sheet_name, vals, worksheet_index=0):
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = gspread.authorize(creds)
  sheet = client.open(sheet_name).get_worksheet(worksheet_index)
  sheet.append_row(vals)

def append_with_column_labels(sheet_name, vals, worksheet_index=0):
  """Add a new row to the sheet, Google Forms style. Will put values in the right column
  And add new column headings to match values provided.
  Expects a dictionary of column heading: value. 
  Note that this may do weird things if there are duplicate headings"""
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = gspread.authorize(creds)
  sheet = client.open(sheet_name).get_worksheet(worksheet_index)
  column_headings = sheet.row_values(1)

  # Check if any column headings are missing
  new_columns = set(vals.keys()) - set(column_headings)
  if len(new_columns) > 0:
    starting_column = len(column_headings) + 1
    # Create a range in A1 format, starting 1 column from the last existing heading
    new_column_range = colnum_string(starting_column)+str(1) + ':' + colnum_string(starting_column + len(new_columns))+str(1)
    # Add the new column headings to the first row
    sheet.batch_update([{
      'range': new_column_range,
      'values': [list(new_columns)]
    }])

  # Update our internal listing of headings to match the new ones--assuming success
  column_headings = column_headings + list(new_columns)
  sorted_values = []
  # Build an ordered list of values based on the column headings so they will match up
  # Use empty string if we didn't get a value for this column
  for heading in column_headings:
    if vals.get(heading):
      sorted_values.append(vals.get(heading))
    else:
      sorted_values.append('')

  sheet.append_row(sorted_values)
  return sorted_values
  

def get_column_headings(sheet_name, worksheet_index=0):
  """Returns a list of all values stored in the first row of the given sheet"""
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = gspread.authorize(creds)
  sheet = client.open(sheet_name).get_worksheet(worksheet_index)
  return sheet.row_values(1)

def colnum_string(n):
  string = ""
  if n is None:
    n = 0
  while n > 0:
    n, remainder = divmod(n - 1, 26)
    string = chr(65 + remainder) + string
  return string

# I don't think this is needed. See https://gspread.readthedocs.io/en/latest/api.html#gspread.models.Worksheet.get_all_records
def sheet_data_to_dict(arr):
  """ Take results from Google Sheets, which is a list of lists, and convert to a list of ordered dictionaries.
  Keys will be taken from the first row, which will be interpreted as column headers."""
  res = list()
  headers = arr[0]
  for row in arr[1:]: # skip the first row of results -- it's the header row
    row_dict = OrderedDict()
    row_length = len(row)
    for index, item in enumerate(row):
      if index < len(headers): # is this a named column?
        col_name = headers[index]
        if col_name:
          row_dict[col_name] = item
        else:
          row_dict[colnum_string(index+1)] = item # default column title to numeric index as string
      else: 
        row_dict[colnum_string(index+1)] = item
    res.append(row_dict)      
  return res