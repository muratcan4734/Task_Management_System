from ast import For
import datetime
from flask import Flask, render_template, request, redirect
from google.cloud import datastore
import google.oauth2.id_token
from google.auth.transport import requests
import string
import random
import os

#enter key
#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "example9-6db6f-306d9e5d901d.json"
app = Flask(__name__)

# get access to the datastore client so we can add and store data in the datastore
datastore_client = datastore.Client()

# get access to a request adapter for firebase as we will need this to authenticate users
firebase_request_adapter = requests.Request()


@app.route('/')
def root():
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
        except ValueError as exc:
            error_message = str(exc)

    return render_template('index.html', user_data=claims, error_message=error_message)


@app.route('/dashboard')
def homepage():
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            userdata_key = datastore_client.key('User', claims['email'])
            userdata = datastore_client.get(userdata_key)
            if userdata == None:
                userdata_key = datastore_client.key('User', claims['email'])
                userdata_entity = datastore.Entity(key=userdata_key)
                userdata_entity.update({
                    'email': claims['email'],
                    'name': claims['name'],
                })
                datastore_client.put(userdata_entity)
            userdata_key = datastore_client.key('User', claims['email'])
            userdata = datastore_client.get(userdata_key)
            query = datastore_client.query(kind='Board')
            boards = query.fetch()
            boards=list(boards)
            
           
            
            

            return render_template('home.html', user_data=claims, boards=boards)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/createBoardPage')
def createBoardPage():
    id_token = request.cookies.get("token")
    claims = None
    response = {
        "error": False
    }
    if id_token:
        try:
            message = request.args.get('message')
            print(message)
            if message != None:
                response = {
                    "error": True,
                    "message": message
                }
            print(response)

            return render_template('addnewBoard.html', response=response)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/createBoard', methods=['POST'])
def createBoard():
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            boardName = request.form['boardName'].capitalize()
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            boarddata_key = datastore_client.key('Board', boardName)
            boarddata = datastore_client.get(boarddata_key)

            if boarddata == None:
                boarddata_key = datastore_client.key('Board', boardName)
                boarddata_entity = datastore.Entity(key=boarddata_key)
                date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
                boarddata_entity.update({
                    'owner': claims['email'],
                    'board': boardName,
                    'createdDate': date,
                    'partners':[claims['email']]
                })
                datastore_client.put(boarddata_entity)
            else:
                return redirect('/createBoardPage?message=This board exists already')
            boarddata = datastore_client.get(boarddata_key)

            return redirect('/dashboard')
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/addtask')
def addtask():
    id_token = request.cookies.get("token")
    claims = None
    response = {
        "error": False
    }
    if id_token:
        try:
            message = request.args.get('message')
            print(message)
            if message != None:
                response = {
                    "error": True,
                    "message": message
                }
            query = datastore_client.query(kind='Board')
            boards = query.fetch()
            if boards == []:
                return redirect("/dashboard")

            return render_template('addtask.html', response=response, boards=boards)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/addtasktoBoard', methods=['POST'])
def addtasktoBoard():
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            boardName = request.form['board']
            taskName = request.form['taskName']
            dueDate = request.form['dueDate']
            currentdate = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")

            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            boarddata_key = datastore_client.key('Board', boardName)
            boarddata = datastore_client.get(boarddata_key)

            if boarddata == None:
                return redirect('/addtask?message=This board does not exist')

            isCompleted = False

            taskid = ''.join(random.choices(
                string.ascii_letters+string.digits, k=20))
            task_key = datastore_client.key('Task', taskid)
            taskdata_entity = datastore.Entity(key=task_key)
            date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
            taskdata_entity.update({
                'taskid': taskid,
                'taskName':taskName,
                'owner':claims['email'],
                'assignedTo':claims['email'],
                'boardName': boardName,
                'dueDate': dueDate,
                'isCompleted':isCompleted,
                'createdon': date
            })
            datastore_client.put(taskdata_entity)

            return redirect('/dashboard')
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/editTask/<string:taskid>')
def editTask(taskid):
    id_token = request.cookies.get("token")
    claims = None
    response = {
        "error": False
    }

    if id_token:
        try:
            message = request.args.get('message')
            print(message)
            if message != None:
                response = {
                    "error": True,
                    "message": message
                }
            task_key = datastore_client.key('Task', taskid)
            task_data = datastore_client.get(task_key)
            print(task_data)
            if task_data == None:
                return redirect('/addtask?message=No task of such exists.')

            return render_template('editTaskdata.html', response=response, task=task_data)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')

@app.route('/editatask/<string:taskid>/<string:boardName>', methods=['POST'])
def editaatask(taskid, boardName):
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            print(request.form)
            taskName=request.form['taskName']
            
            dueDate=request.form['dueDate']
            
            currentdate = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")

            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            task_key = datastore_client.key('Task', taskid)
            taskdata_entity = datastore.Entity(key=task_key)
            if request.form['is_completed']:
                isCompleted=True
            else:
                isCompleted=False
            date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
            taskdata_entity.update({
                'taskid': taskid,
                'taskName':taskName,
                'owner':claims['email'],
                'assignedTo':claims['email'],
                'boardName': boardName,
                'dueDate': dueDate,
                'isCompleted':isCompleted,
                'createdon': date
            })
            datastore_client.put(taskdata_entity)
            return redirect('/boarddatas/'+boardName)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/delete/<string:taskid>', methods=['POST'])
def deleteaatask(taskid):
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:

            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            task_key = datastore_client.key('Task', taskid)
            task_data = datastore_client.get(task_key)
            boardName=task_data['boardName']
            if task_data == None:
                return redirect('/addtask?message=No task of such exists.')

            if task_data['owner'] != claims['email']:
                return redirect('/addtask?message=You are not the owner of the board you tried to delete')

            datastore_client.delete(task_key)

            return redirect('/boarddatas/'+boardName)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/deletePartner/<string:boardName>/<string:newPartner>',methods=['POST'])
def deletePartner(boardName,newPartner):
    id_token = request.cookies.get("token")
    claims = None
    flag=False
    if id_token:
        try:
            boardName=boardName.capitalize()
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            query2 = datastore_client.query(kind='Board')
            query2 = query2.add_filter('board', '=', boardName)
            board = query2.fetch()
            if board != None:
                partners=list(board)[0]['partners']
                for partner in partners:
                    if partner==newPartner:
                        flag=True
                        
                if flag:
                    partners.remove(newPartner)
                
                boarddata_key = datastore_client.key('Board', boardName)
                boarddata_entity = datastore.Entity(key=boarddata_key)
                date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
                boarddata_entity.update({
                    'owner': claims['email'],
                    'board': boardName,
                    'createdDate': date,
                    'partners':partners
                })
                datastore_client.put(boarddata_entity)
                
            return redirect('/boarddatas/'+boardName)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/boarddatas/<string:boardName>')
def fetchboarddata(boardName):
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            boardName=boardName.capitalize()
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            query = datastore_client.query(kind='Task')
            query = query.add_filter('boardName', '=', boardName)
            tasks = query.fetch()
            if tasks!=None:
                tasklist = list(tasks)

            query2 = datastore_client.query(kind='Board')
            query2 = query2.add_filter('board', '=', boardName)
            
            board = query2.fetch()
            firstboard=list(board)[0]
            partners=firstboard['partners']
            boardOwner=firstboard['owner']
            
            query3 = datastore_client.query(kind='User')
            users = query3.fetch()
            usersList=list(users)
            
            
            return render_template('viewBoard.html', tasklist=tasklist, boardName=boardName, user_data=claims , usersList=usersList, partners=partners,boardOwner=boardOwner)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/findboard', methods=['POST'])
def findboard():
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            boardName = request.form['boardName']
            boardName = boardName.capitalize()
            return redirect('/boarddatas/'+boardName)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/addUsertoBoard/<string:boardName>',methods=['POST'])
def addUsertoBoard(boardName):
    id_token = request.cookies.get("token")
    claims = None
    flag=False
    if id_token:
        try:
            boardName=boardName.capitalize()
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            query2 = datastore_client.query(kind='Board')
            query2 = query2.add_filter('board', '=', boardName)
            board = query2.fetch()
            if board != None:
                partners=list(board)[0]['partners']
                newPartner=request.form['board']
                for partner in partners:
                    if partner==newPartner:
                        flag=True
                        
                if not flag:
                    partners.append(newPartner)
                
                boarddata_key = datastore_client.key('Board', boardName)
                boarddata_entity = datastore.Entity(key=boarddata_key)
                date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")
                boarddata_entity.update({
                    'owner': claims['email'],
                    'board': boardName,
                    'createdDate': date,
                    'partners':partners
                })
                datastore_client.put(boarddata_entity)
                
            return redirect('/boarddatas/'+boardName)
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/boarddatas/assignUserTotask/<string:taskid>/<string:user_id>',)
def assignUserTotask(taskid,user_id):
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            query = datastore_client.query(kind='Task')
            query = query.add_filter('taskid', '=', taskid)
            taskList = list(query.fetch())[0]
            
            
            task_key = datastore_client.key('Task', taskid)
            taskdata_entity = datastore.Entity(key=task_key)
          
            
            taskdata_entity.update({
                'taskid': taskid,
                'taskName':taskList['taskName'],
                'owner':claims['email'],
                'assignedTo':user_id,
                'boardName': taskList['boardName'],
                'dueDate': taskList['dueDate'],
                'isCompleted':taskList['isCompleted'],
                'createdon': taskList['createdon']
            })
            datastore_client.put(taskdata_entity)
            print(taskdata_entity)
            return redirect('/boarddatas/'+taskList["boardName"])
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')


@app.route('/taskComplete/<string:taskid>',methods=['POST','GET'])
def taskComplete(taskid):
    id_token = request.cookies.get("token")
    claims = None
    if id_token:
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            query = datastore_client.query(kind='Task')
            query = query.add_filter('taskid', '=', taskid)
            taskList = list(query.fetch())[0]
            
            
            task_key = datastore_client.key('Task', taskid)
            taskdata_entity = datastore.Entity(key=task_key)
          
            
            taskdata_entity.update({
                'taskid': taskid,
                'taskName':taskList['taskName'],
                'owner':claims['email'],
                'assignedTo':taskList['assignedTo'],
                'boardName': taskList['boardName'],
                'dueDate': taskList['dueDate'],
                'isCompleted':True,
                'createdon': taskList['createdon']
            })
            datastore_client.put(taskdata_entity)
            print(taskdata_entity)
            return redirect('/boarddatas/'+taskList["boardName"])
        except ValueError as exc:
            error_message = str(exc)
    return redirect('/')
 
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
