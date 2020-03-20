from docassemble.base.functions import get_config, all_variables, user_info, user_logged_in, comma_and_list, comma_list
from docassemble.base.util import Address, Individual, Person, Name, format_date, DAObject, DADict, DAList, DADateTime
from decimal import Decimal

__all__ = ['get_simple_vars']

def get_simple_vars(mapping = {},skip=[],custom=False):
  """Returns a dictionary of the current interview state with variables suitable to include in a spreadsheet.
  Similar to Google Forms. You will lose some information--variables will be flattened out.
  Does its best to handle Individual, Person, Address, DAList/DADict and DAObject datatypes

  Optionally, map the columns to new names with a dictionary

  By default this takes the interview's current state. You can instead provide your own dictionary
  of variables to simplify
  """
  # The following are keys that Docassemble uses that we never want to extract from the answer set
  keys_to_ignore = ['_internal','url_args','PY2','string_types','nav','__warningregistry__'] + skip

  if custom:
    interview_state = custom
  else:
    interview_state = all_variables(simplify=False)
  interview_state = {k:v for k, v in interview_state.items() if k not in keys_to_ignore}

  simplified_vars = {}

  for key, value in interview_state.items():
    if isinstance(value, Individual):
      add_individual(simplified_vars,key,value)
    elif isinstance(value, Person):
      add_person(simplified_vars,key,value)
    elif isinstance(value,DADict):
      add_dict(simplified_vars,key, value)
    elif isinstance(value, DAList):
      simplified_vars[key] = comma_list(value)
    elif isinstance(value, DADateTime):
      simplified_vars[key] = value.format_date(format='yyyy-MM-dd')
    elif isinstance(value,DAObject):
      all_attributes = set(value.__dict__.keys()) - {'has_nonrandom_instance_name', 'instanceName', 'attrList', 'location'}
      for attribute in all_attributes:
        if isinstance(getattr(value,attribute), DADateTime):
          simplified_vars[key + '.' + attribute ] = getattr(value,attribute).format_date(format='yyyy-MM-dd')
        else:
          simplified_vars[key + '.' + attribute] = str(getattr(value,attribute))
    # Don't transform numbers
    elif isinstance(value,int) or isinstance(value,float):
      simplified_vars[key] = value
    # Send Decimal values as floating point
    elif isinstance(value,Decimal):
      simplified_vars[key] = float(value)
    # Everything else gets turned into a string, including True/False values
    else:
      simplified_vars[key] = str(value)

  # Map the values to new column names if the user provided a mapping
  simplified = {}
  if len(mapping) > 0:
    for name, value in simplified_vars.items():
      if name in mapping:
        simplified[mapping[name]] = value
      else:
        simplified[name] = value

  return simplified

def add_individual(the_dict, key, individual):
  the_dict[key] = str(individual)
  the_dict[key + '.name.first'] = individual.name.first
  if hasattr(individual,'name') and hasattr(individual.name,'middle'):
    the_dict[key + '.name.middle'] = individual.name.middle
  if hasattr(individual,'name') and hasattr(individual.name,'last'):
     the_dict[key + '.name.last'] = individual.name.last
  if hasattr(individual,'name') and hasattr(individual.name,'suffix'):
     the_dict[key + '.name.suffix'] = individual.name.suffix
  if hasattr(individual, 'birthdate'):
    the_dict[key+ '.birthdate'] = format_date(individual.birthdate, format='yyyy-MM-dd')
  # Get a list of all of the attributes of this individual, excluding built-in ones
  all_attributes = set(individual.__dict__.keys()) - {'has_nonrandom_instance_name', 'instanceName', 'attrList', 'name', 'address', 'location','birthdate'}
  for attribute in all_attributes:
    the_dict[key + '.' + attribute] = str(getattr(individual,attribute))
  if hasattr(individual, 'address') and hasattr(individual.address,'address'):
    add_address(the_dict, key + '.address', individual.address)
  
def add_person(the_dict, key, person):
  the_dict['key'] = str(person) # equivalent of name.text
  all_attributes = set(person.__dict__.keys()) - {'has_nonrandom_instance_name', 'instanceName', 'attrList', 'name', 'address', 'location','birthdate'}
  for attribute in all_attributes:
    the_dict[key + '.' + attribute] = str(getattr(person,attribute))
  if hasattr(person, 'address') and hasattr(person.address,'address'):
    add_address(the_dict, key + '.address',person.address)

def add_address(the_dict, key, address):
  all_attributes = set(address.__dict__.keys()) - {'has_nonrandom_instance_name', 'instanceName', 'attrList', 'location','geolocated', 'city_only'}
  for attribute in all_attributes:
    the_dict[key + '.' + attribute] = str(getattr(address,attribute))
  
def add_dict(the_dict, key, value):
  try:
    # Convert the dictionary into an iterable. Check the first item and see if it is a True/False variable
    if type(next(iter(value.values()))) is bool: # We will assume it is output of datatype: checkboxes
      the_dict[key] = comma_list(value.true_values()) # only return the checked items
    else:
      the_dict[key] = str(value) # this probably isn't what they want, but best we can do
  except:
    the_dict[key] = str(value)