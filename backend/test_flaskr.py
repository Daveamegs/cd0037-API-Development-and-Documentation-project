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
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            'student', 'student', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

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
    # GET Test Cases(Response Status Code must be equal 200)

    # Get Paginated Questions Tests
    # Pass test
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["questions"]), 10)
        self.assertTrue(data["totalQuestions"])

    # Failed test error 404 resource not found for requests beyond the availabe page
    def test_error_404_request_beyond_available_page(self):
        res = self.client().get("/questions?page=600")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error_message"], "resource not found")

    # Get All Categories Test
    # Pass Test

    def test_get_all_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_categories"])

    # Fail Tests Error 404
    def test_fail_get_all_categories(self):
        res = self.client().get("/categories/10")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    # Get Questions Based on Category
    # Pass Test

    def test_get_questions_by_category_via_category_id(self):
        res = self.client().get("/categories/2/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    # Failed Test
    def test_error_404_for_requests_beyond_available_category_id(self):
        res = self.client().get("/categories/20/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error_message"], "resource not found")

    # Delete Question by Question ID
    # Pass Test
    def test_delete_question_by_question_id(self):
        res = self.client().delete("/questions/20")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted_id"], 20)

    # Failed Test
    def test_error_404_unable_to_process_delete_request_id_does_not_exist(self):
        res = self.client().delete("/questions/100")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error_message"], "unprocessable")

    # Post, Create or Add a new question
    # Pass test
    def test_add_a_new_question(self):
        res = self.client().post("/questions", json={
            "question": "Which Football Club won the 2021/22 UEFA Champions League?",
            "answer": "Real Madrid",
            "difficulty": 2,
            "category": 6
        })

        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question_created"])
        self.assertTrue(len(data["questions"]))

    # Fail Test
    def test_405_new_question_not_allowed(self):
        res = self.client().post("/questions/100", json={
            "question": "Which Football Club won the 2021/22 UEFA Champions League?",
            "answer": "Real Madrid",
            "difficulty": 2,
            "category": 6
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error_message"], "method not allowed")

    # Get Questions based on a Search Term
    # Pass Test
    def test_get_questions_by_searching(self):
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "africa"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["questions"]))

    # Fail Test
    def test_404_question_does_exist(self):
        res = self.client().post("/questions/search",
                                 json={"searchTerm": "hshhgxn"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["error_message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
