# Task_Management_System
Python

MAIN.PY

This class is main.py where I have defined the necessary function structure for my project. Then, it contains my main python project by writing the codes required to compile the program here.


def root():
	This method is used to render the first page of the application i.e., the index.html file. The initial flow of the application starts with this root method.

def homepage():
	I used this method as it redirects the user to the home.html page after the user has successfully logged into the system.


def createBoardPage():
	This method renders add addnewBoard.html page. 

def createBoard():
	I used this structure to create a new board. I kept board Name as key. As board data, I have established a relationship from the user's e-mail address to the owner and partner part.

def addTask():
	This method renders add addtask.html page. 


def addTasktoBoard():
	I used this method to create a task. Here, I transferred the necessary data for the task to the datastore entity.

def editTask():
	This method is used to edit the task values that come with the task Id.

def edittaatask():
	I used it to edit the selected task by keeping the taskId and boardname parameters.


def deletetaatask():
	This method is used to delete the selected task by keeping the taskId.

def deletePartner():
	This method is used to delete the partner.

def findboard():
	This method is used to get board information to find.

def addUsertoBoard():
	This method is used  for boardName,  is taken as parameter/filter and checked with the data store if there is any data available first to avoid multiple entry of same data. If data is not available in datastore then a new entry is created with the parameters taken from user in form of Board object.

def assignUserTotask():
	This method I used to perform the appropriate assignment of the task data with the parameters task id and user id

def taskComplate(): 
	I complated task data on the entity with the taskId and user Id parameters.
