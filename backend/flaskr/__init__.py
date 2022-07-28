import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    @app.route('/')
    def welcome():
        return jsonify({'welcome': 'hello'})

    '''
  @Done: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app)
    cors = CORS(app, resources={r"*": {"origins": "*"}})
    '''
  @Done: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    # create pagination for questions
    perpage = 10

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * perpage
        end = start + perpage

        formated_questions = [Question.format(ques) for ques in selection]

        return formated_questions[start:end]
    '''
  @Done:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def retrieve_categories():
        all_categories = Category.query.all()
        #formated_categories = {Category.format(cat) for cat in all_categories}
        formated_categories = {cat.id: cat.type for cat in all_categories}
        if(len(formated_categories) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'categories': formated_categories
        })

    '''
  @Done:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def retrieve_questions():
        # if the user is trying to paginate when he/she in a specific category

        category_name = request.args.get('category', 'null')
        if category_name == 'null':
            category_name = None
            all_questions = Question.query.all()
        else:
            category_id = Category.query.filter(Category.type == category_name)
            all_questions = Question.query.filter(
                Question.category == str(category_id[0].id)).all()

        #all_questions = Question.query.all()
        formated_questions = paginate_questions(request, all_questions)

        all_categories = Category.query.all()
        # I cannot use Category.format because there is an error in the
        # frontend "Objects are not valid as a React child"
        # now the formated categories should be formated as { categories : {"id" : "type"} }
        #formated_categories = [Category.format(cat) for cat in all_categories]
        formated_categories = {cat.id: cat.type for cat in all_categories}

        if(len(formated_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(all_questions),
            'current_category': category_name,
            'categories': formated_categories
        })
    '''
  @Done:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:ques_id>', methods=['DELETE'])
    def delete_question(ques_id):
        deleted_question = Question.query.filter(
            Question.id == ques_id).one_or_none()

        if delete_question is None:
            abort(404)
        else:
            try:
                deleted_question.delete()

                return jsonify({
                    'success': True,
                    'message': "Your Question is deleted Successfully"
                })
            except BaseException:
                abort(404)
    '''
  @Done:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        question = body.get('question', '')
        answer = body.get('answer', '')
        difficulty = body.get('difficulty', '')
        category = body.get('category', '')

        # check all variables
        if(question == '' or answer == '' or difficulty == '' or category == ''):
            abort(422)

        try:
            inserted_question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category)
            inserted_question.insert()

            return jsonify({
                'succuss': True,
                'message': "Question is added successfully"
            })

        except BaseException:
            abort(422)

    '''
  @Done:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        body = request.get_json()
        searched_question = body.get('searchTerm', '')
        # in case of the user didnot input any string
        if(searched_question == ''):
            abort(422)

        all_searched_questions = Question.query.filter(
            Question.question.ilike('%' + searched_question + '%')).all()
        # incase the question is not found
        if(len(all_searched_questions) == 0):
            abort(404)

        formated_questions = paginate_questions(
            request, all_searched_questions)

        all_categories = Category.query.all()
        formated_categories = {cat.id: cat.type for cat in all_categories}

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(all_searched_questions),
            'current_category': None,
            'categories': formated_categories
        })

    '''
  @Done:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(cat_id):
        categorized_questions = Question.query.filter(
            Question.category == str(cat_id)).all()
        formated_questions = paginate_questions(request, categorized_questions)

        # get category type
        categories = Category.query.filter(Category.id == cat_id).all()
        if len(categories) == 0:
            abort(404)

        category_type = categories[0].type
        category_id = categories[0].id

        if(len(categorized_questions) == 0):
            abort(404)

        return jsonify({
            'success': True,
            'questions': formated_questions,
            'total_questions': len(categorized_questions),
            'current_category': category_type,
            'current_category_id': category_id
        })

    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_quizzes():
        body = request.get_json()
        previous_questions = body.get('previous_questions', '')
        quiz_category = body.get('quiz_category', '')

        if previous_questions == '' or quiz_category == '':
            abort(422)

        # check all categories or specific category
        if quiz_category['id'] == 0:
            all_questions = Question.query.all()
        else:
            all_questions = Question.query.filter(
                Question.category == str(quiz_category['id'])).all()

        # get a random question
        start = 0
        end = len(all_questions)
        question = all_questions[random.randint(start, end - 1)]
        # check the id of the question is added to previous questions list
        formated_question = question.format()
        while formated_question['id'] in previous_questions:
            question = all_questions[random.randint(start, end - 1)]
            formated_question = question.format()

            if(end == len(previous_questions)):
                return jsonify({
                    'success' : True
                })

        
        return jsonify({
            'success': True,
            'question': formated_question,
            'prev': previous_questions
        })

    '''
  @Done:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
    return app

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method not allowed"
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    return app
