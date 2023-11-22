import re
import filetype

def validate_name(name):
  return name and (3 < len(name) < 80)

def validate_phone(phone):
  if phone:
    phone_no_space = re.sub(r'\s+', '', phone)
    phone_regex = r'^\+569\d{8}$'
    return bool(re.match(phone_regex, phone_no_space))
  else:
    return True
  
def validate_email(email):
  if email:
      email_regex = r'^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
      return bool(re.match(email_regex, email))
  else:
      return False

def validate_comuna(comuna):
  if comuna: return True
  else: False

def validate_region(region):
  if region: return True
  else: False

def validate_tipos(tipos):
  return tipos and (1 <= len(tipos) <= 3)

def validate_transporte(transporte):
  if transporte: return True
  else: False
