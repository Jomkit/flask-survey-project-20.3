from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretKey72'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

#global constants for cookie names for Flask Sessions
RESPONSES = 'responses'
TARGET_SURVEY = 'target_survey'

@app.route('/')
def show_select_survey():
    """Show the surveys that the user can choose to take"""
    choices = [names for names in surveys.keys()]
    return render_template('select_survey.html', choices=choices)

@app.route('/select_survey', methods=['post'])
def select_survey():
    """select_survey() gets the chosen survey from select_survey.html, 
       and sets it to the global variable target_survey"""
    session[RESPONSES] = []
    
    global target_survey
    target_survey = surveys[request.form['choices']]
    return redirect('/home')

@app.route('/home')
def homepage():
    """Homepage for Shop Surveys, start survey from here"""
    survey = target_survey
    return render_template('home.html', survey=survey)

@app.route('/questions/<id>')
def get_question(id):
    """Render pages associated with survey questions sequentially
       if user tries to enter custom url to go to a question out
       of order, redirect to the next question in the original 
       sequential order"""
    responses = session[RESPONSES]
    if not int(id) == len(responses):
        flash('Attempting to access invalid question, redirecting to next question in order', 'info')
        return redirect(url_for('get_question',id=len(responses)))
    
    qid = int(id)
    p_bar = qid / len(target_survey.questions) * 100
    question = target_survey.questions[qid].question
    allow_comments = target_survey.questions[qid].allow_text
    choices = target_survey.questions[qid].choices
    return render_template('questions.html',id=qid, p_bar=p_bar, question=question, allow_comments=allow_comments, choices=choices)

@app.route('/answer', methods=['post'])
def show_answer():
    """Get answer from previous questions form
      should redirect to next question. If all questions answered, 
      should redirect to a thank you page"""

    ans = request.form['choices']
    comments = request.form.get('comments','')
    responses = session[RESPONSES]
    responses.append({'answer':ans, 'comment':comments})
    session[RESPONSES] = responses
    
    id = len(responses)
    if id >= len(target_survey.questions):
        return redirect('/thank_you')
    else:
        return redirect(url_for('get_question',id=id))
    
@app.route('/thank_you')
def thank_you():
    """Thank you page, displays questions and the user's responses"""
    questions = target_survey.questions
    length = range(len(questions))
    return render_template('thank_you.html', questions=questions, range=length)
