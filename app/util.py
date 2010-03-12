#!/usr/bin/env python
#
# (c) Alexey Pegov (spleaner@gmail.com) 2009-2010
#
import os
import logging

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp import template
from django.utils import simplejson

def is_dev_env():
  """ Checks devel environment (localhost) """
  return os.environ.get('SERVER_SOFTWARE','').startswith('Devel') # 'Goog' for production

class RequestHandlerEx(webapp.RequestHandler):
  """ Just a helper methods """
  
  def is_mobile(self):
    """ Checks if this site is accessed through webkit-compatible mobile browser """
    agent = self.request.headers['User-Agent']
    return "Android" in agent or "iPhone" in agent
    
class TemplateHandler(RequestHandlerEx):
  """ Request handler which output is always rendered with specified  django template """
  
  TEMPLATES_PATH = "templates"
  
  def __init__(self, template_name, auth_template, admin_template):
    self.template_name = template_name
    self.auth_template = auth_template
    self.admin_template = admin_template
  
  def get(self):
    user = users.get_current_user()
    if users.is_current_user_admin():
      self.render(self.template_path(self.admin_template), 
        {'logout_url': users.create_logout_url("/"), 
         'username': user.nickname()})
    elif user:
      self.render(self.template_path(self.auth_template), 
        {'logout_url': users.create_logout_url("/"), 
         'username': user.nickname()})
    else: 
      self.render(self.template_path(self.template_name), 
        {'login_url': users.create_login_url("/")})

  def _404(self):
    self.error(404)
    self.response.out.write('Page not found! // TBD')

  def template_path(self, template_name):
    return os.path.join(os.path.dirname(__file__), self.TEMPLATES_PATH, '%s.html' % (self.is_mobile() and template_name + "-m" or template_name))

  def render(self, template_path, data):
    self.response.out.write(template.render(template_path, data))


class JSONHandler(RequestHandlerEx):
  def prepare_data(self, user):
    raise NotImplementedError

  def post(self):
    user = users.get_current_user()
    data = { 'status': False, 'error': 'Forbidden' }
    if user: data = self.prepare_data(user)
    self.response.headers['Content-Type'] = 'application/json'
    simplejson.dump(data, self.response.out, ensure_ascii=False)