import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import web
from web import form
import os
import datetime
root = os.path.dirname(__file__) 
render = web.template.render(os.path.join(root, 'templates/'),cache=False)
db = web.database(dbn='postgres',user='postgres',pw='123',db='blog',host='127.0.0.1')

urls = (
'/','index',
'/add/(.*)','add',
'/register','register',
'/private/(.*)/(.*)/(.*)','private',
'/edit/(.*)/(.*)','edit',
)

add_form = form.Form(
	form.Textbox('content'),
)

class index:
	def GET(self):
		todos = db.select('todo')
		return render.index()
class private:
	def GET(self,user,status,page):
		per_page = 12
		off = (int(page)-1)*12
		num = db.query("select count(0) as num from works where id = "+user)[0]["num"]
		if num % per_page == 0:
			pages = num / per_page
		else: 
			pages = num / per_page + 1
		if int(status) == 2:
			works = db.select('works',where="id="+user,limit=per_page,offset=off)
		else:
			works = db.select('works',where="id="+user+" and status="+status,limit=per_page,offset=off)
		blank = 12 - len(works)
		data = [user,page,works,num,blank]
		return render.index(data)
class register:
	def GET(self):
		return render.register()
class add:
	def GET(self,user):
		data = [user]
		return render.add(data)
	def POST(self,user):
		post = web.input()
		db.insert('works',
			id=user,
			content=post.content,
			status=post.status,
			createtime=datetime.datetime.now()
			)
		raise web.seeother('/private/'+user)	
class edit:
	def GET(self,user,w_id):
		work = db.select('works',where='w_id='+w_id)[0]
		data = [user,w_id,work]
		return render.edit(data)
	def POST(self,user,w_id):
		post = web.input()
		db.update('works',
			where='w_id='+w_id,
			id=user,
			content=post.content,
			status=post.status,
			createtime=datetime.datetime.now()
			)
		raise web.seeother('/private/'+user)	
application = web.application(urls, globals()).wsgifunc()

