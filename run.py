# -*- coding: UTF-8 -*-
from flask import *
from flask.ext.script import Manager
from flask.ext.pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from mongodb import *

#mongoDB config
app = Flask(__name__)
app.config['MONGO_HOST'] = MONGO_HOST
app.config['MONGO_PORT'] = MONGO_PORT
app.config['MONGO_DBNAME'] = MONGO_DBNAME
app.config['MONGO_USERNAME'] = MONGO_USERNAME
app.config['MONGO_PASSWORD'] = MONGO_PASSWORD
app.config['MONGO_SELF'] = False

mongo = PyMongo(app, config_prefix='MONGO')

#查詢科目
def classQuery(classkind,classname):
    courses=[]
    if classkind == "common":
        for course_post in mongo.db.commoncourse.find({"course":{"$regex":classname}}):
            courses.append(course_post)
    else:
        for course_post in mongo.db.languagecourse.find({"course":{"$regex":classname}}):
                courses.append(course_post)
    return courses



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#首頁
@app.route('/')
def index():
    return render_template('index.html')

#評論頁面
@app.route('/comment',methods=['POST','GET'])
def comment():
    coursename = request.args.get('coursename')
    teacher = request.args.get('teacher')
    courses=[]
    if request.method == 'POST':
        if request.form['submit'] == 'query':
            if request.form['CourseSort'] == "common":
                courses=classQuery("common",request.form['classname'])
            elif request.form['CourseSort'] == "language":
                courses=classQuery("language",request.form['classname'])
        elif request.form['submit'] == 'sent':
            if request.form['title'] != "" or request.form['message'] != "":
                #處理評論的
                posts = {"time":datetime.now(),"coursename":coursename,"teacher":teacher,"title":request.form['title'],"message":request.form['message']}
                course = mongo.db.course
                course.insert(posts)
                return redirect(url_for('browse'))
    else:
        courses=classQuery("common","")
    return render_template('comment.html',courses=courses,coursename=coursename,teacher=teacher)

#瀏覽
@app.route('/browse',methods=['POST','GET'])
def browse():
    comments=[]
    courses=[]
    name = request.args.get('name')

    if request.method == 'POST':
        if request.form['CourseSort'] == "common":
            courses=classQuery("common",request.form['classname'])
        else:
            courses=classQuery("language",request.form['classname'])
    else:
        courses=classQuery("common","")

    if request.args.get('name'):
        for comment_post in mongo.db.course.find({"coursename":name}):
            comments.append(comment_post)
    else:
        for comment_post in mongo.db.course.find():
            comments.append(comment_post)
    return render_template('browse.html', courses=courses,comments=comments)

#修改評論
@app.route('/editcomment',methods=['POST','GET'])
def editcomment():
    id = request.args.get('id')
    comment = mongo.db.course.find_one({'_id':ObjectId(id)})
    title = comment['title']
    message = comment['message']
    if request.method == 'POST':
        if request.form['title'] != "" and request.form['message'] != "":
            result = mongo.db.course.find_one({'_id': ObjectId(id)})
            mongo.db.course.update({'_id': ObjectId(id)},{'title': request.form['title'],'message': request.form['message'],'teacher':comment['teacher'],'coursename':comment['coursename']})
            return redirect(url_for('browse'))
    return render_template('editcomment.html',title=title,message=message)

#討論區
@app.route('/forum')
def forum():
    name = request.args.get('name')
    return redirect(url_for('browse',name=name))

#新增評論
@app.route('/review')
def review():
    course = []
    id = request.args.get('id')
    if (mongo.db.languagecourse.find_one({'_id':ObjectId(id)})):
        course = mongo.db.languagecourse.find_one({'_id':ObjectId(id)})
    elif (mongo.db.commoncourse.find_one({'_id':ObjectId(id)})):
        course = mongo.db.commoncourse.find_one({'_id':ObjectId(id)})

    return redirect(url_for('comment',coursename=course['course'],teacher=course['teacher']))

#刪除資料
@app.route('/delete')
def delete():
    id = request.args.get('id')
    result = mongo.db.course.remove({'_id':ObjectId(id)})
    return redirect(url_for('browse'))

#團隊介紹
@app.route('/team')
def team():
    return render_template('team.html')


#test
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)



