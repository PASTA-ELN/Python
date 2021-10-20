"""extractor data from .hap file
- Fischer-Scope .hap file: unknown
"""

def use(fileName, doc):
  """
  Args:
     fileName (string): full path file name
     doc (dict): supplied to guide image creation doc['-type']

  Returns:
    list: image|content, [('png'|'jpg'|'svg'|'text'), type, metaVendor, metaUser]
  """
  #final return if nothing successful
  return None, ['', [], {}, {}]
