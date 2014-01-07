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
'/delete/(.*)/(.*)','delete',
'/login','login',
'/logout','logout',
)
add_form = form.Form(
	form.Textbox('content'),
)

class index:
	def GET(self):
		todos = db.select('todo')
		return render.index()

class login:
	def GET(self):
		if session.login ==0:
			return render.login()
		else:
			user = session.login
			return 'You have logged'
	def POST(self):
		post = web.input()
		user = post.user
		pd = post.pd
		i = db.select("users",where="login_name='"+user+"' and password='"+pd+"'")
		if len(i) > 0:
			user = i[0].id
			session.login=user
			web.redirect('/private/'+str(user)+"/2/1")	
		else:
			print "user error or password error"
			web.redirect('/login')	

class logout:
	def GET(self):
		session.login = 0
		session.kill()	
		return 'You are logout'

class private:
	def GET(self,user,status,page=1):
		if session.login > 0:
			per_page = 12
			off = (int(page)-1)*12
			if status ==2:
				num = db.query("select count(0) as num from works where id = "+user)[0]["num"]
			else:
				num = db.query("select count(0) as num from works where id = "+user+" and status="+status)[0]["num"]
			if num % per_page == 0:
				pages = num / per_page
			else: 
				pages = num / per_page + 1
			if int(status) == 2:
				works = db.select('works',where="id="+user,order="w_id DESC",limit=per_page,offset=off)
			else:
				works = db.select('works',where="id="+user+" and status="+status,order="w_id DESC",limit=per_page,offset=off)
			blank = 12 - len(works)
			lastpage = int(page) -1
			nextpage = int(page) +1	
			data = [user,page,works,num,blank,lastpage,nextpage,pages,status]
			return render.index(data)
		else:
			return '111'

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
		raise web.seeother('/private/'+user+"/2/1")	
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
		raise web.seeother('/private/'+user+"/2/1")	
class delete:
	def GET(self,user,w_id):
		db.delete('works',where='w_id='+w_id)
		raise web.seeother('/private/'+user+"/2/1")	
app = web.application(urls, globals())

curdir = os.path.dirname(__file__)
session = web.session.Session(app, web.session.DiskStore(curdir + '/' + 'sessions'),initializer={'login':0})

application = app.wsgifunc()
