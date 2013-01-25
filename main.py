#!/usr/bin/env python
# -*- coding:utf-8 -*-

import webapp2
import jinja2
import os, json

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class Person(ndb.Model):
  email = ndb.StringProperty()
  name = ndb.StringProperty()
  phone = ndb.StringProperty()
  address = ndb.StringProperty()
  notes = ndb.TextProperty()

  def toDict(self):
    # Python Dictionary (Dict) is equivalent to JavaScript object
    return { 'email': self.email,
             'name': self.name,
             'phone': self.phone,
             'address': self.address,
             'notes': self.notes }
 

class MainPage(webapp2.RequestHandler):
  def get(self):
    template_values = {}

    user = users.get_current_user()
    if user:
      template_values['isLogin'] = True
      template_values['userEmail'] = user.email()
      template_values['signoutURL'] = users.create_logout_url("/")
    else:
      template_values['isLogin'] = False
      template_values['signinOrRegisterURL'] = users.create_login_url("/")

    template = jinja_environment.get_template('index.html')
    self.response.out.write(template.render(template_values))


class RESTfulHandler(webapp2.RequestHandler):
  def isLegalUser(self, email):
    user = users.get_current_user()
    if not user:
      return False
    if email != user.email():
      return False
    return True

  def get(self, email):
    if not self.isLegalUser(email):
      self.error(404)
      return
    # use email as ID for database access
    person = Person.get_by_id(email)
    if (person):
      self.response.out.write(json.dumps(person.toDict()))
    else:
      self.error(404)

  def post(self, email):
    if not self.isLegalUser(email):
      self.error(404)
      return
    person = Person.get_by_id(email)
    if (person):
      # this entity already exists!
      self.error(403)
      return
    data = json.loads(self.request.body)
    person = Person(id = email,
                    email = email,
                    name = data['name'],
                    phone = data['phone'],
                    address = data['address'],
                    notes = data['notes'])
    person.put()
    self.response.out.write(json.dumps(person.toDict()))

  def put(self, email):
    if not self.isLegalUser(email):
      self.error(404)
      return
    person = Person.get_by_id(email)
    data = json.loads(self.request.body)
    person.name = data['name']
    person.phone = data['phone']
    person.address = data['address']
    person.notes = data['notes']
    person.put()
    self.response.out.write(json.dumps(person.toDict()))

  def delete(self, email):
    if not self.isLegalUser(email):
      self.error(404)
      return
    person = Person.get_by_id(email)
    if (person):
      person.key.delete()
    else:
      self.error(403)


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/RESTful/([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})', RESTfulHandler)],
                              debug=True)