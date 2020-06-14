from flask import Flask
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# THIS CODE IS DERIVATED FROM THE EXAMPLE OF Flask-RESTX EXTENSION

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)

api = Api(
    app,
    version='1.0',
    title='TodoMVC API',
    description='A simple TodoMVC API',
)

ns = api.namespace('todos', description='TODO operations')

todo = api.model(
    'Todo', {
        'id':
        fields.Integer(readOnly=True,
                       description='The task unique identifier'),
        'createdAt':
        fields.DateTime(readOnly=True,
                        description='datetime value of task creation time'),
        'task':
        fields.String(required=True, description='The task details')
    })

# flask_alchemy Model that represents the schema of our sql table


class TodoModel(db.Model):
    __tablename__ = 'todos'
    id = db.Column('id', db.Integer, primary_key=True)
    createdAt = db.Column('createdAt', db.DateTime)
    task = db.Column('task', db.String(300), nullable=False)


class TodoDAO(object):
    def get(self, id):
        todo = TodoModel.query.filter_by(id=id).first()
        return todo
        api.abort(404, "Todo {} doesn't exist".format(id))

    def getAll(self):
        todo = TodoModel.query.all()
        return todo

    def create(self, data):
        # id is automatically autoincremented by SQLAlchemy
        todo = TodoModel(createdAt=datetime.now(), task=data['task'])
        db.session.add(todo)
        db.session.commit()
        return todo

    def update(self, id, data):
        todo = TodoModel.query.filter_by(id=id)
        todo.task = data['task']
        db.session.commit()
        return todo

    def delete(self, id):
        todo = TodoModel.query.filter_by(id=id)
        db.session.delete(todo)
        db.session.commit()


DAO = TodoDAO()


@ns.route('/')
class TodoList(Resource):
    '''Shows a list of all todos, and lets you POST to add new tasks'''
    @ns.doc('list_todos')
    @ns.marshal_list_with(todo)
    def get(self):
        '''List all tasks'''
        return DAO.getAll()

    @ns.doc('create_todo')
    @ns.expect(todo)
    @ns.marshal_with(todo, code=201)
    def post(self):
        '''Create a new task'''
        return DAO.create(api.payload), 201


@ns.route('/<int:id>')
@ns.response(404, 'Todo not found')
@ns.param('id', 'The task identifier')
class Todo(Resource):
    '''Show a single todo item and lets you delete them'''
    @ns.doc('get_todo')
    @ns.marshal_with(todo)
    def get(self, id):
        '''Fetch a given resource'''
        # print(DAO.get(id))
        return DAO.get(id)

    @ns.doc('delete_todo')
    @ns.response(204, 'Todo deleted')
    def delete(self, id):
        '''Delete a task given its identifier'''
        DAO.delete(id)
        return '', 204

    @ns.expect(todo)
    @ns.marshal_with(todo)
    def put(self, id):
        '''Update a task given its identifier'''
        return DAO.update(id, api.payload)


if __name__ == '__main__':
    app.run(debug=True)
