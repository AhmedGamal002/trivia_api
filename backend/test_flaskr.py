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
        self.database_path = "postgres://{}/{}".format('postgres:Gemi2991@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        #create a question to test 
        self.new_question = {
            'question' : 'How many times Al-Ahly win the CAF Champions League?',
            'answer' : '9',
            'category' : '6',
            'difficulty' : 4
        }
        #create a question to test failing of create question 
        self.new_fail_question = {
            'question' : 'How many times Al-Ahly win the CAF Champions League?',
            'answer' : '9',
            'difficulty' : 4
        }
        #search a questions 
        self.search_term = {
            'searchTerm' : 'title'
        }
        #search a questions with empty search
        self.search_empty_term = {
            'searchTerm' : ''
        }
        #search a questions with not word doesnot include in the questions
        self.search_not_exist_term = {
            'searchTerm' : 'not_exist_word'
        }
        #play quiz 
        self.play_format = {
            'previous_questions' : [],
            'quiz_category' : {
                'id' : 6 ,
                'type' :'Sports'
            }
        }
        #fail play quiz 
        self.play_fail_format = {
            'previous_questions' : []
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
    #successful pagination on page 2
    def test_get_paginated_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['success'] , True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    #failed pagination on page 1000
    def test_404_get_paginated_questions_for_not_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 404)
        self.assertEqual(data['success'] , False)
        self.assertEqual(data['error'],404)
        self.assertEqual(data['message'], "resource not found")
        
    #successful categories retrieval
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['success'] , True)
        self.assertTrue(data['categories'])

    #failed to found categories in database
    #you need an empty categories table to test this case
    #def test_fail_to_get_categories_not_found_in_database(self):
    #    res = self.client().get('/categories')
    #    data = json.loads(res.data)
    #
    #    self.assertEqual(res.status_code , 404)
    #    self.assertEqual(data['error'] , 404)
    #    self.assertEqual(data['message'], "resource not found")

    #successful questions per category retrieval
    def test_get_questions_per_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['success'] , True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertTrue(data['current_category_id'])

    #failed question per category retrieval cause of not found category 
    def test_404_get_question_per_category(self):
        res = self.client().get('/categories/20/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 404)
        self.assertEqual(data['error'] , 404)
        self.assertEqual(data['message'], "resource not found")

    #successful question creation
    def test_create_question(self):
        res = self.client().post('/questions' , json = self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['succuss'] , True)
        self.assertEqual(data['message'] , "Question is added successfully")

    #failing question creation on missing data
    def test_missing_data_when_create_question(self):
        res = self.client().post('/questions' , json = self.new_fail_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 422)
        self.assertEqual(data['success'] , False)
        self.assertEqual(data['error'] , 422)
        self.assertEqual(data['message'] , "unprocessable")

    #successful question deletion
    def test_delete_question(self):
        res = self.client().delete('/questions/9')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['success'] , True)
        self.assertEqual(data['message'] , "Your Question is deleted Successfully")
    
    #fail question deletion when entering not existing id
    def test_not_existing_id_delete_question(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 404)
        self.assertEqual(data['success'] , False)
        self.assertEqual(data['error'] , 404)
        self.assertEqual(data['message'] , "resource not found")

    #successful question search
    def test_search_question(self):
        res = self.client().post('/questions/search' , json = self.search_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 200)
        self.assertEqual(data['success'] , True)
        self.assertTrue(data['questions']) 
        self.assertTrue(data['total_questions']) 
        self.assertTrue(data['categories']) 

    #fail search while entering empty string
    def test_422_fail_search_question(self):
        res = self.client().post('/questions/search' , json = self.search_empty_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 422)
        self.assertEqual(data['success'] , False)
        self.assertEqual(data['error'] , 422)
        self.assertEqual(data['message'] , "unprocessable")
        
    #fail search while entering empty string
    def test_404_fail_search_question(self):
        res = self.client().post('/questions/search' , json = self.search_not_exist_term)
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 404)
        self.assertEqual(data['success'] , False)
        self.assertEqual(data['error'] , 404)
        self.assertEqual(data['message'] , "resource not found")

    #successful playing of quiz
    def test_play_quiz(self):
        res = self.client().post('/quizzes' , json = self.play_format)
        data = json.loads(res.data)

        self.assertEqual(data['success'] , True)
        self.assertTrue(data['question']) 

    #fail playing of quiz
    def test_422_play_quiz(self):
        res = self.client().post('/quizzes' , json = self.play_fail_format)
        data = json.loads(res.data)

        self.assertEqual(res.status_code , 422)
        self.assertEqual(data['success'] , False)
        self.assertEqual(data['error'] , 422)
        self.assertEqual(data['message'] , "unprocessable")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()