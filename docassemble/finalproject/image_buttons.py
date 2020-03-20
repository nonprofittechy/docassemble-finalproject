import re
from docassemble.base.functions import url_action

__all__ = ['button_field']

def button_field(buttons):
  """Create a button field, like image buttons but can be used in a question/subquestion. The buttons
  all visit a URL.
  Expects a list of dictionaries, with each dictionary having these keys:
  {
    'label': the label displayed with the link
    'icon': the font-awesome icon, or static image to display in the button
    'new_window': Boolean, optional, controls whether link opens in same/different tab
    'url': the URL the link will visit. Conflicts with action -- this takes precedence
    'action': paramater passed to url_action to generate a Docassemble action URL. Conflicts with url -- url overrides action
  }
  """

  opening = '<fieldset class="da-field-buttons"><legend class="sr-only">Press one of the following buttons:</legend><div>'
  close = "</div></fieldset>"

  html = opening

  for button in buttons:
    # TODO: fix parent CSS so we don't need to hardcode margin
    html += '<a style="margin: .3em;" class="btn btn-da btn-light btn-da btn-da-custom" '
    # Set the target of the link
    if button.get('new_window') is True or button.get('new_window', None) is None:
        target = ''
    elif button.get('new_window') is False:
        target = 'target="_self" '
    else:
        target = 'target="' + str(button.get('new_window')) + '" '    
    html += target
    if button.get('url'):
      html += 'href="' + button.get('url','') + '"'
    elif button.get('action'):
      html += 'href="' + url_action(button.get('action','')) + '"'
    else:
      html += 'href="' + '' + '"' # This won't make sense, but we can still show a button
    # Close anchor
    html += '>'
    # TODO: fix parent CSS so we don't need to hardcode vertical-align
    html += '<span style="vertical-align: middle; display: inline-block;"><div>'
    if isinstance(button.get('icon'), str):
      icon = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', button.get('icon'))
      if not re.search(r'^fa[a-z] fa-', icon):
          icon = 'fas fa-' + icon
      icon = '<i class="' + icon + '"></i> '
    else:
      icon = ''
    html += icon + '</div>' + button.get('label','') + '</span></a>'
  html += close
  
  return html
