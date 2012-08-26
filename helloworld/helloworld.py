import cgi
import datetime
import urllib
import webapp2
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import util

class Greeting(db.Model):
  """Models an individual Guestbook entry with an author, content, and date."""
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)


def guestbook_key(guestbook_name=None):
  """Constructs a datastore key for a Guestbook entity with guestbook_name."""
  return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')
    guestbook_name = self.request.get('guestbook_name')



class MainPageOLD(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')
    self.response.out.write('hello world appengine')
    self.response.out.write('</body></html>')


class HelloWorldPage(webapp2.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>Hello World Appengine HelloWorldPage</body></html>')



class Guestbook(webapp2.RequestHandler):
  def get(self):
#    self.response.headers['Content Type'] = 'text/plain'
#    self.response.out.write('Hello, world appengine')
# how do we show the last entry in the guestbook? 
# 1) get a guestbook 2) get the last greeting
    guestbook_name = self.request.get('guestbook_name');

    self.response.out.write("""
       <html><body>
         Guestbook: """ + guestbook_name + """<br><br>
         
       """)

    greetings = db.GqlQuery("SELECT * "
                "FROM Greeting "
                "WHERE ANCESTOR IS :1 "
                "ORDER BY date DESC LIMIT 10",
                guestbook_key(guestbook_name))

    for greeting in greetings:
      if greeting.author:
        self.response.out.write(
          '<b>$s</b> wrote: ' %  greeting.author)
      else:
        self.response.out.write('An anonymous person wrote: ')
        self.response.out.write('<blockquote>%s</blockquote>' % cgi.escape(greeting.content))
                   

    self.response.out.write("""
         <form action="/sign" method="post">
           <div><textarea name="content" rows=3 columns=60>Foobar </textarea></div>
           <div><input type="hidden" name="guestbook_name" value="peetsguestbook"></input></div>
           <div><input type="submit" value="Sign Guestbook"></div>
         </form>
       </body></html>""")


  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
    guestbook_name = self.request.get('guestbook_name')
    greeting = Greeting(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))


app = webapp2.WSGIApplication([('/', Guestbook),
                               ('/sign', Guestbook),
                               ('/foo', HelloWorldPage)],
                              debug=True)
util.run_wsgi_app(app)


#def main():
#  wsgiref.handlers.CGIHandler().run(app)


#if __name__ == '__main__':
#  main()
