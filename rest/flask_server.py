"""Module with Flask functional. REST requests handling."""

from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

from common.configs_handler import Config
from rest.redis_storage.test_case_instance import TestCaseRedis
from rest.redis_storage.test_suite_instance import TestSuiteRedis

server_data = Config().get()

# Redis instances
case_redis = TestCaseRedis(server_data['hash_names']['test_case'])
suite_redis = TestSuiteRedis(server_data['hash_names']['test_suite'])

# Flask
app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = server_data['jwt_secrete_key']
jwt = JWTManager(app)

valid_user = server_data['valid_user']


@app.route("/api/v1/")
def index():
    """Server index."""
    return jsonify(message="Simple Test Management System API"), 200


@app.route('/api/v1/login', methods=['POST'])
def login():
    """Login to the server.

    :return: {"access_token": <str>} or error message
    """
    if request.content_type != "application/json":
        return jsonify(message="Content-type must be application/json"), 415

    if not request.data:
        return jsonify(message="Bad request body"), 400

    username = request.json.get("username")
    password = request.json.get("password")
    if not (username and password):
        return jsonify(message="Bad request body"), 400

    if username != valid_user['name'] or password != valid_user['password']:
        return jsonify(message="No such username or password"), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token), 200


# NOTE: Test case routes
@app.route("/api/v1/test_cases", methods=['GET'])
@jwt_required
def get_all_test_cases():
    """Get all test cases data.

    :return: {"test_cases": list with test cases data (dicts)}
    """
    test_cases = case_redis.get_all()
    return jsonify(test_cases=test_cases), 200


@app.route("/api/v1/test_cases/<test_case_id>", methods=['GET'])
@jwt_required
def get_test_case(test_case_id):
    """Get test case data.

    :param test_case_id: id of test case
    :return: {"test_case": dict with test case data}
    """
    test_case = case_redis.get(test_case_id)
    if test_case is None:
        return jsonify(message="Test case doesn't exist"), 404
    return jsonify(test_case=test_case), 200


@app.route("/api/v1/test_cases", methods=['POST'])
@jwt_required
def post_test_case():
    """Create new test case.

    Body schema for request:
        {
            suites_id: connection to suite
            title: test case name
            description: short info about test case
        }
    :return: {message:<str>, id:<str>} if success, else {message:<str>}
    """
    if request.content_type != "application/json":
        return jsonify(message="Content-type must be application/json"), 415

    if not request.data:
        return jsonify(message="Bad request body"), 400

    data = request.json

    # Verify request body
    if not all([item in data for item in
                server_data['requests']['body']['test_case']]):
        return jsonify(message="Bad request body"), 400

    if not suite_redis.is_item_exists(data['suite_id']):
        return jsonify(message="Test suite does not exist"), 404

    result = case_redis.add(data)
    if result is None:
        return jsonify(message="Test case already exist"), 409

    suite_redis.update_cases(data['suite_id'], result, '+')
    suite_redis.update_length(data['suite_id'], "+")
    return jsonify(message="Test case successfully added", id=result), 200


@app.route("/api/v1/test_cases", methods=['DELETE'])
@jwt_required
def delete_all_test_cases():
    """All test cases deletion.

    :return: {message:<str>}
    """
    case_list = case_redis.get_all()

    for case in case_list:
        suite_redis.update_cases(case['suite_id'], case['id'], '-')
        suite_redis.update_length(case['suite_id'], "-")

    case_redis.delete_all()
    return jsonify(message="All test cases successfully deleted"), 200


@app.route("/api/v1/test_cases/<test_case_id>", methods=['PUT'])
@jwt_required
def put_test_case(test_case_id):
    """Update existing test case data.

    Body schema for request:
        {
            suites_id: connection to suite
            title: test case name
            description: short info about test case
        }
    :param test_case_id: id of test case
    :return: {message:<str>}
    """
    if request.content_type != "application/json":
        return jsonify(message="Content-type must be application/json"), 415

    if not request.data:
        return jsonify(message="Bad request body"), 400

    data = request.json

    # Verify request body
    if not all([item in data for item in
                server_data['requests']['body']['test_case']]):
        return jsonify(message="Bad request body"), 400

    if not case_redis.update(test_case_id, data):
        return jsonify(message="Test case does not exist"), 404

    return jsonify(message="Test case successfully updated"), 200


@app.route("/api/v1/test_cases/<test_case_id>", methods=['DELETE'])
@jwt_required
def delete_test_case(test_case_id):
    """Test case deletion.

    :param test_case_id: id of test case
    :return: {message:<str>}
    """
    if not case_redis.is_item_exists(test_case_id):
        return jsonify(message="Test case doesn't exist"), 404

    suite_id = case_redis.get_suite_id(test_case_id)

    case_redis.delete(test_case_id)

    suite_redis.update_cases(suite_id, test_case_id, '-')
    suite_redis.update_length(suite_id, "-")
    return jsonify(message="Test case successfully deleted"), 200


# NOTE: Test Suite routes
@app.route("/api/v1/test_suites", methods=['GET'])
@jwt_required
def get_all_test_suites():
    """Get all test suites data.

    :return: {"test_suites": list with test suites data (dicts)}
    """
    test_suites = suite_redis.get_all()
    return jsonify(test_suites=test_suites), 200


@app.route("/api/v1/test_suites/<test_suite_id>", methods=['GET'])
@jwt_required
def get_test_suite(test_suite_id):
    """Get test suite data.

    :return: {"test_suite": dict with test suite data}
    """
    test_suite = suite_redis.get(test_suite_id)

    if test_suite is None:
        return jsonify(message="Test suite doesn't exist"), 404

    return jsonify(test_suite=test_suite), 200


@app.route("/api/v1/test_suites", methods=['POST'])
@jwt_required
def post_test_suite():
    """Create test suite record.

    Body schema for request: {title:<string>}
    :return: {message:<str>, id:<str>} if success, else {message:<str>}
    """
    if request.content_type != "application/json":
        return jsonify(message="Content-type must be application/json"), 415

    if not request.data:
        return jsonify(message="Bad request body"), 400

    data = request.json

    # Verify request body
    if not all([item in data for item in
                server_data['requests']['body']['test_suite']]):
        return jsonify(message="Bad request body"), 400

    result = suite_redis.add(data)

    if result is None:
        return jsonify(message="Test suite already exist"), 409

    return jsonify(message="Test suite successfully added", id=result), 200


@app.route("/api/v1/test_suites", methods=['DELETE'])
@jwt_required
def delete_all_test_suites():
    """Delete test suite.

    :return: {message:<str>}
    """
    if request.data:
        if request.content_type != "application/json":
            return jsonify(
                message="Content-type must be application/json"), 415

        if request.json.get("force"):
            case_redis.delete_all()
            suite_redis.delete_all()
            return jsonify(
                message="All test cases and suites successfully deleted"), 200

    suite_list = suite_redis.get_all()
    for suite in suite_list:
        if not suite['cases']:
            suite_redis.delete(suite['id'])

    return jsonify(message="Empty test suites successfully deleted"), 200


@app.route("/api/v1/test_suites/<test_suite_id>", methods=['PUT'])
@jwt_required
def put_test_suite(test_suite_id):
    """Update existing test suite data.

    Body schema for request: {title:<string>}
    :param test_suite_id: id of test suite
    :return: {message:<str>}
    """
    if request.content_type != "application/json":
        return jsonify(message="Content-type must be application/json"), 415

    if not request.data:
        return jsonify(message="Bad request body"), 400

    data = request.json

    # Verify request body
    if not all([item in data for item in
                server_data['requests']['body']['test_suite']]):
        return jsonify(message="Bad request body"), 400

    if not suite_redis.update(test_suite_id, data):
        return jsonify(message="Test suite does not exist"), 404

    return jsonify(message="Test suite successfully updated"), 200


@app.route("/api/v1/test_suites/<test_suite_id>", methods=['DELETE'])
@jwt_required
def delete_test_suite(test_suite_id):
    """Delete test suite.

    :param test_suite_id: id of test suite
    :return: {message:<str>}
    """
    linked_cases = suite_redis.get_record_data(test_suite_id)['cases']

    if not suite_redis.is_item_exists(test_suite_id):
        return jsonify(message="Test suite doesn't exist"), 404

    if request.data:
        if request.content_type != "application/json":
            return jsonify(
                message="Content-type must be application/json"), 415

        data = request.json

        if linked_cases:
            force = data.get("force")
            if not force:
                return jsonify(
                    message="Unable to delete test suite with linked test "
                            "cases.\nPlease, use 'Force':True option to "
                            "delete suite and all test cases in it"), 409
            if force:
                for case_id in linked_cases:
                    delete_test_case(case_id)

    suite_redis.delete(test_suite_id)
    return jsonify(message="Test suite successfully deleted"), 200


def start_flask_server():
    """Start Flask server."""
    app.run(host=server_data.get('host', 'localhost'),
            port=server_data.get('port', 5000),
            debug=True)
