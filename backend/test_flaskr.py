import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question ={
            'question':'what is your fav books?',
            'answer':'Math',
            'difficulty':'9',
            'category':'1'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        res=self.client().get('/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True),
        self.assertEqual(data['total_questions'],19)
        self.assertTrue(len(data['questions']))
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res=self.client().get('/questions?page=1000', json={'category':1})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found please check your input')
    
    def test_delete_question(self):
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 6).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 6)
        self.assertTrue(data['total_question'])
        self.assertTrue(len(data['question']))

    
    

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        pass

    
    def test_404_if_question_does_not_exist(self): 
        res = self.client().delete('/questions/12345')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'], False )
        self.assertEqual(data['message'], 'unprocessable')

    def test_get_questions_by_category(self):
        res=self.client().get('categories/6/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['total_questions'],2)
    
    def test_404_question_not_found(self):
        res=self.client().get('/categories/lkklok/questions')
        data=json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], "resource not found please check your input")

    
    def test_search_tool(self):
        res=self.client().post('/questions', json={'searchTerm':'Which country won the first ever soccer World Cup in 1930?'})
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['totalQuestions'],1)
    
    def test_search_for_not_found_info(self):
        res=self.client().post('/questions' , json={'searchTerm':'udacity'})
        data=json.loads(res.data)

        self.assertEqual(data['totalQuestions'],0)
        self.assertEqual(res.status_code,200)

    def test_quiz_game(self):
        res = self.client().post('/quizzes' , json={"previous_questions":[],
	"quiz_category":{
		"type":"Art",
		"id":"2"
	}})
        data=json.loads(res.data)


        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data["question"])

    def test_error_404_quiz_game(self):
        res = self.client().post('/quizzes' , json={"previous_questions":[],
	"quiz_category":{
		"type":"Art",
		"id":"213"
	}})
        data=json.loads(res.data)


        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        
        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()