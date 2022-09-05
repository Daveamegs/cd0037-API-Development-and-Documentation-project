import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    question = [question.format() for question in selection]
    current_questions = question[start:end]
    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, supports_credentials=True)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization, true")
        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PATCH, DELETE, OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_categories():
        all_categories = Category.query.all()
        data = {category.id: category.type for category in all_categories}

        if len(data) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "categories": data,
            "total_categories": len(all_categories)
        })
    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions")
    def get_questions():

        selection = Question.query.order_by(Question.id).all()
        data = paginate_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()
        categories_data = {
            category.id: category.type for category in categories}

        if len(data) == 0:
            categories = None
            abort(404)
        else:
            return jsonify({
                "success": True,
                "questions": data,
                "totalQuestions": len(selection),
                "categories": categories_data,
                "currentCategory": "History"
            })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question_to_delete = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question_to_delete == None:
                abort(404)

            question_to_delete.delete()

            return jsonify({
                "success": True,
                "deleted_id": question_to_delete.id
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None)

        try:
            question = Question(
                question=new_question, answer=answer, category=category, difficulty=difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            data = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "question_created": question.id,
                "questions": data,
                "total_questions": len(Question.query.all())
            })
        except:
            abort(405)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json()

        search_value = body.get("searchTerm", None)

        if search_value == None:
            abort(404)

        else:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike("%" + search_value + "%")).all()

            if len(selection) == 0:
                abort(404)

            data = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "questions": data,
                "total_questions": len(selection)
            })

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions")
    def get_categorized_questions(category_id):
        selection = Question.query.order_by(Question.id).filter(
            Question.category == category_id).all()
        data = paginate_questions(request, selection)
        current_category = Category.query.filter(
            Category.id == category_id).one_or_none()

        if len(selection) == 0:
            abort(404)

        return jsonify({
            "success": True,
            "questions": data,
            "totalQuestions": len(selection),
            "currentCategory": current_category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def start_quiz():
        try:
            body = request.get_json()
            category = body.get("quiz_category", None)
            previous_questions = body.get("previous_questions", None)

            if category["id"] == 0:
                questions = Question.query.filter(
                    Question.id.notin_(previous_questions)).all()

            else:
                questions = Question.query.filter(Question.category == str(
                    category["id"])).filter(Question.id.notin_(previous_questions)).all()

            return jsonify({
                "success": True,
                "question": questions[random.randint(0, len(questions) - 1)].format() if len(questions) else None
            })

        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "error_message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "error_message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "error_message": "bad request"
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "error_message": "internal server error"
        }), 500

    @app.errorhandler(405)
    def not_allowed(error):
        return ({
            "success": False,
            "error": 405,
            "error_message": "method not allowed"
        }), 405

    return app
