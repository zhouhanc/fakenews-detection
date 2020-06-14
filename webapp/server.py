"""
    TODO: bot database botaccount.db needs to be actively managed and
          automatically updated
"""
from flask import Flask, jsonify, send_from_directory, render_template, make_response, abort
from flask import request, redirect, Response, url_for, session, flash
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from functools import wraps, update_wrapper
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# from werkzeug.middleware.proxy_fix import ProxyFix
import os
import os.path
# from collections import namedtuple
import sys
sys.path.insert(0, "/home/centos/research/TwitterBotProject/")
sys.path.insert(0, "/Users/zc/Documents/TwitterBotProject/tag_classifier")
sys.path.insert(0, "/home/centos/research/TwitterBotProject/tag_classifier")
# import predict_domain
# from update_feedback import insert_feedback, get_feedback
import redis
from pprint import pprint
from rq import Queue
sys.path += ['../']
import pymongo
import json
# from tasks import account_get_score, domain_get_score
# from send_email import send_one
# from make_token import generate_confirmation_token, confirm_token

app = Flask(__name__)
# app.secret_key = b'>lw\xef\x90\xf7wA\x00\xbe[\xbf!\xa3i\xdb'
# app.config['SECURITY_PASSWORD_SALT'] = '424242'

print(app.config)

#app.wsgi_app = ProxyFix(app.wsgi_app)
root_directory = os.environ['TwitterBotProjectPath']

# connection to redis server 
r = redis.Redis()
print(r)
queue_high = Queue('high', connection=r)
queue_default = Queue('default', connection=r)
queue_low = Queue('low', connection=r)
print(queue_high, queue_default, queue_low)

# svm_classifier = predict_domain.load_classifier()

# def mongo_client_user_collection():
#     mongo_client_predict_domain = pymongo.MongoClient(**util.mongo_config)
#     return mongo_client_predict_domain.dbuser.user
    
# mongo_client_score = predict_domain.mongo_client_score_collection()
# mongo_client_user = mongo_client_user_collection()

# main_client = pymongo.MongoClient(**util.mongo_config)
# mongo_client_score = main_client.domain_lookup.score
# mongo_client_user = main_client.dbuser.user
# mongo_client_feedback = main_client.feedback.domain


# def load_directory():
#     with open(root_directory + '/config.json') as json_data_file:
#         return json.load(json_data_file)


# config = load_directory()
# ProcessedDataPath = config["ProcessedDataPath"]
# NetworkGraphPath = config["NetworkGraphPath"]


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


def is_authorized_request_addr():
    """Return true if the user has unrestricted access, false otherwise
    """
    F.write(str(request.remote_addr) + " " + str(datetime.now()) + '\n')
    F.flush()
    print("[Get request from %s]" %(str(request.remote_addr)))
    return True
    if request.remote_addr[:3] == "10." or request.remote_addr[:7] == "128.42." or request.remote_addr == "127.0.0.1" or request.remote_addr[:10] == "104.237.90":
        return True
    else:
        return False

# silly user model
class User(UserMixin):

    def __init__(self, name):
        self.id = name
        self.name = "user " + str(name)
        # self.password = self.name + "_secret"
        
    def __repr__(self):
        return "%d/%s/" % (self.id, self.name)


####################
# for API endpoint
####################

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': "Not Found"}), 404)

@app.errorhandler(400)
def bad_request(error = "Bad Request"):
    return make_response(jsonify({'error': str(error)}), 400)

@app.errorhandler(401)
def unauthorized(error = "Unauthorized"):
    return make_response(jsonify({'error': str(error)}), 401)


####################
# for web application
####################

@app.route('/')
@app.route('/discoverer')
def discoverer():
    return render_template("index.html")
    # return None


@app.route('/vendor/<path:path>')
def send_vendor(path):
    return send_from_directory('vendor', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/img/<path:path>')
def send_img(path):
    return send_from_directory('img', path)

@app.route('/font/<path:path>')
def send_font(path):
    return send_from_directory('font', path)

@app.route('/html/<path:path>')
def send_html(path):
    return send_from_directory('html', path)

@app.route('/gun_control.html')
def gun_control():
    return render_template("gun_control.html")

@app.route('/release_the_memo.html')
def release_the_memo():
    return render_template("release_the_memo.html")

@app.route('/threat_intelligence.html')
def threat_intelligence():
    return render_template("threat_intelligence.html")

@app.route('/redirection')
def trend():
    return render_template("redirection.html")

@app.route('/google6b1aea530c160ffc.html')
def google_verify():
    return render_template("google6b1aea530c160ffc.html")

@app.route('/sitemap.xml')
def sitemap_verify():
    return render_template("sitemap.xml")

@app.route('/api.html')
def monitor_markdown():
    return render_template("api.html")

@app.route('/detector')
def detector(warning_meg=None):
    return render_template("tag_classifier.html", warning_meg=warning_meg)

@app.route('/tag_classifier.html')
def return_classifier():
    return render_template("tag_classifier.html")

@app.route('/account')
def return_account():
    return render_template("score_account.html")


@app.route('/account_prediction', methods = ['POST'])
def account_prediction():
    jsonData = request.get_json()
    screen_name = jsonData['screen_name']
    if "screen_name" not in jsonData:
        return make_response(jsonify({'error': "no screen_name or priority"}), 400)
    # by default, priority is low
    if "priority" not in jsonData:
        jsonData["priority"] = "low"
    if "priority" in jsonData and jsonData["priority"] not in ["default", "low"]:
        return make_response(jsonify({'error': "priority can be default or low"}), 400)

    if jsonData["priority"] == "default":
        job = queue_default.enqueue(account_get_score, args=(screen_name, svm_classifier, ), job_timeout=70)
    elif jsonData["priority"] == "low":
        job = queue_low.enqueue(account_get_score, args=(screen_name, svm_classifier, ), job_timeout=70)

    print("new job added {}-{}".format(job.id, job.enqueued_at))
    pprint(job)
    result = {}
    result["job_id"] = job.id
    result["status"] = "no_record"
    
    print(result)
    print("[monitor] send result of domain {} -- {}".format(screen_name, result["status"]))
    return Response(json.dumps(result), mimetype='application/json')


@app.route('/tag_prediction', methods = ['POST'])
def tag_prediction():

    jsonData = request.get_json()
    domain = jsonData['domain']
    if "domain" not in jsonData:
        make_response(jsonify({'error': "no domain and priority fields"}), 400)
    # by default, priority is low
    if "priority" not in jsonData:
        jsonData["priority"] = "low"
    if "priority" in jsonData and jsonData["priority"] not in ["default", "low"]:
        make_response(jsonify({'error': "priority can be default or low"}), 400)

    # NOTE: passing svm_classifier can be a slow bottleneck for some tasks
    if "no_svm_feature" in jsonData:
        result = predict_domain.get_domain_score(domain, mongo_client_score, svm_classifier=None)
    else:
        result = predict_domain.get_domain_score(domain, mongo_client_score, svm_classifier=svm_classifier)
    if (result["status"] == "no_record" and "no_job" not in jsonData) or \
       (result["status"] == "no_record" and "no_job" in jsonData and jsonData["no_job"] is False):

        print("test if svm_classifier is None...")
        print(svm_classifier)
        if jsonData["priority"] == "default":
            job = queue_default.enqueue(domain_get_score, args=(domain, svm_classifier, ), job_timeout=45)
        elif jsonData["priority"] == "low":
            job = queue_low.enqueue(domain_get_score, args=(domain, svm_classifier, ), job_timeout=45)

        print("new job added {}-{}".format(job.id, job.enqueued_at))
        pprint(job)
        result["job_id"] = job.id
    else:
        print('no_job exists, do not add data to queue')
    
    print("[monitor] send result of domain {} -- {}".format(domain, result["status"]))
    return Response(json.dumps(result), mimetype='application/json')


@app.route("/jobs/<job_id>", methods=["GET"])
def get_job_status(job_id):
    task = queue_default.fetch_job(job_id)
    if task:
        response_object = {
            "status": "success",
            "data": {
                "task_id": task.get_id(),
                "task_status": task.get_status(),
                "task_result": task.result,
                "tast_meta": task.meta
            },
        }
    else:
        response_object = {"status": "error"}
    # print(response_object)
    return jsonify(response_object)


@app.route('/feedback', methods = ['POST', 'GET'])
# @login_required
def feedback():
    if request.method == 'POST':
        jsonData = request.get_json()
        if insert_feedback(jsonData, request, mongo_client_feedback):
            return Response(json.dumps({'status': 'succeed'}), mimetype='application/json')
        else:
            return bad_request("please check your input fields")
    elif request.method == 'GET':
        jsonData = request.get_json()
        result = get_feedback(mongo_client_feedback)
        print('========== PRINT result ...')
        pprint(result)

        print('========== response')
        return Response(json.dumps(result), mimetype='application/json')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=18000, debug = True)
    # ParseResult(scheme='https', netloc='www.wittyfeed.com', path='/', params='', query='', fragment='')
    # print(urlparse("twitter.com"))
