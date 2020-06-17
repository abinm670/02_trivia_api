import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
import pprint

QUESTIONS_PER_PAGE = 10
def paginate_questions(request, selection):
  page=request.args.get('page',1,type=int)
  start=(page -1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions= [question.format() for question in selection]
  current_questions= questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Headers', 'GET,PUT,POST,DELETE,OPTIONS')

    return response



  
  @app.route('/categories')
  def retrive_categories():
    selection = Category.query.order_by(Category.id).all()
  
    
    selection=[i.type.format() for i in selection]

    

    return jsonify({
      'success':True,
      "categories":selection,
      "total_categories":len(selection)
    })

 


  
  @app.route('/questions')
  def retrive_questions():
    selection= Question.query.order_by(Question.id).all()
    current_question = paginate_questions(request, selection)
    if len(current_question) ==0:
      abort(404)
    current_category=[i.category for i in selection]
    selection2 = Category.query.order_by(Category.id).all()
    selection2=[i.type.format() for i in selection2]
   

    return jsonify({
      "success":True,
      "questions":current_question,
      "total_question":len(current_question),
      "categories":selection2,
      # "current_category":current_category
      
    })


  
  @app.route('/questions/<int:q_id>', methods=['DELETE'])
  def delete(q_id):
    try:
      question=Question.query.filter(Question.id == q_id).one_or_none()

      if question is None:
        abort(404)
      
      question.delete()
      selection=Question.query.order_by(Question.id).all()
      current_question=paginate_questions(request,selection) 

      return jsonify({
        "success":True,
        "deleted":q_id,
        "question":current_question,
        "total_question":len(current_question)
      })

    except:
      abort(422)
    

  
  @app.route('/questions', methods=['POST'])
  def new_question():
    body=request.get_json()
        
    new_question=body.get('question',None)
    new_answer=body.get('answer', None)
    new_difficulty=body.get('difficulty')
    new_category=body.get('category')
    search=body.get('searchTerm')

    
    try:
      if search:
        selection=Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        x=selection.all()
        if  selection is None :
          abort(404)
        
        current_question=paginate_questions(request, selection)
        

        return jsonify({
          'success':True, 
          'questions':current_question,
          "totalQuestions":len(current_question), 
          "current_category":""
        })

      else:
        question=Question(question=new_question, answer=new_category, difficulty=new_category, category=new_category )
        question.insert()
        print(question)
        return jsonify({
          'success':True,
          'created':question.id,
          'total_books':len(Question.query.all())
        })
    
    except:
      abort(422)

 

  
  @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
  def get_questions_by_categories(cat_id):
    selection=Question.query.filter(Question.category == (cat_id+1))
    questions=paginate_questions(request, selection)

    return jsonify({
      "questions":questions,
      "total_questions":len(questions),
      "current_category":""
    })


  
  @app.route('/quizzes' , methods=['POST'])
  def quiz():
    body=request.get_json()
    print("info send :", body)
    previous_questions=body['previous_questions']
    quiz_category=body['quiz_category']['id']
    # print("test",previous_questions, "id:", quiz_category)
    try:
      quiz=Question.query.filter(Question.category == int(quiz_category)+1).all()

      if quiz is None:
        abort(404)

      quiz_list=[q.format() for q in quiz]
      quiz=random.choice(quiz_list)

      return jsonify({
        "success":True,
        "question":quiz, 
        "previous_questions":[]
      })
      

    except:
      abort(422) 


  @app.errorhandler(404)
  def notFound(error):
    return jsonify({
      "success":False,
      "error":404,
      "message":"resource not found please check your input"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success":False,
      "error":422,
      "message":"unprocessable",
    }),422


  return app

    