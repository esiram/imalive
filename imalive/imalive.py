### ALL IMPORTS ###
import os
import sqlite3
import datetime #for date stamp -- TO BE USED WITH DB ITEMS; not used as of 3/17/17
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash


### CONFIGURATION CODE ###
"""Loads default config and overrides config from environment variable."""

app = Flask(__name__)                # create app instance & initialize it
app.config.from_object(__name__)     # load config from this file, imalive.py

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'imalive.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
    ))
app.config.from_envvar('IMALIVE_SETTINGS', silent=True)



### DATABASE FUNCTIONS ###
#FUNCTIONS TO CONNECT DB
def connect_db():
   """Connects to specific database."""
   rv = sqlite3.connect(app.config['DATABASE'])
   rv.row_factory = sqlite3.Row           #this allows rows to be treated like dictionaries vs tuples
   return rv

def get_db():
    """Opens a new database connection if none yet for current application context."""
    if not hasattr(g, 'sqlite_db'):       #store db in a global variable 'g'
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):                      #if things go well the error parameter is None
    """Closes the database again at end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

        
#FUNCTIONS TO UTILIZE DB
def create_table():
    """To create table 'survivors' if table doesn't exist."""
    conn = connect_db()                   #connection
    cur = conn.cursor()                   #cursor (TBD: see init_db 'c' for cursor: determine if a general cursor object for the entire app should get made)
    cur.execute('CREATE TABLE IF NOT EXISTS survivors(familyname TEXT, personalname TEXT, signupdate TIMESTAMP)')
       

#FUNCTIONS TO INITIALIZE DB
def init_db():
    """Opens file from resource folder."""
    db = get_db()
    c = db.cursor()                #db.cursor() used in flaskr tutorial rather than c (TBD: does this duplicate the create_table 'cur' variable? Can you simplify?)
    with app.open_resource('schema.sql', mode='r') as f:
       c.executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')  #flask creates an application context bound to correct application
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

    
    
### VIEW FUNCTIONS ###
#GENERAL VIEW FUNCTIONS
@app.route('/', methods = ['POST', 'GET'])
@app.route('/home', methods = ['POST', 'GET'])
def home():
   """ Handles home screen (home.html). """
   render_template('home.html', error = None)
   error = None
  # while request.method == 'POST':     #should doWhat have a not null value????-ES 3/15/17
   if request.method == 'POST':
       doWhat = request.form['doWhat']
       if doWhat == "search":
           return redirect(url_for("search"))
       elif doWhat == "signup":
           return redirect(url_for("signupSurvivor"))
       elif doWhat == "login":
           return redirect(url_for("loginSurvivor"))
       else: #if nothing chosen but submit/enter button hit (i.e. doWhat = None); THIS DOESN'T WORK! Currently an error at redirections/rendering 'home.html'-es3/17/17
           return render_template('home.html', error = "TESTING WHICH ERROR MSG: Please select from one of the options.  Thank you.")
   else:    #request.method == 'GET'
       error = "Please select from one of the options.  Thank you."
       return render_template('home.html')#, error = error)

#@app.route('/celebrate/<personalname>', methods = ['GET', 'POST']) #not pulling dynamic stuff into URL - Es 3/13/17
@app.route('/celebrate', methods = ['GET', 'POST'])
def celebrate():
    """Handles the celebrate screen (celebrate.html)."""
    if 'personalname' in session:                                                        #this pulls name dynamically into template, URL not showing yet as of 3/13/17
       return render_template('celebrate.html', personalname = session['personalname'], message = session['message'])  #this pulls name dynamically as of 3/13/17
    else:
       message= "Celebrate, you live!!!  If you want to look somoone else up, please check out the I'mAlive's Search page."
       return render_template('celebrate.html', message = message)

    
   
#SURVIVOR VIEW FUNCTIONS
@app.route('/signupSurvivor', methods = ['GET', 'POST'])
def signupSurvivor():
    """Handles survivor signup screen (signupSurvivor.html)."""
    render_template('signupSurvivor.html', error = None)
    if request.method == 'POST':
       error = None
       message = ""
       
       #form inputs:
       familyname = request.form['familyname']
       personalname = request.form['personalname']
       additionalname = request.form['additionalname']
       gender = None
       if 'gender' in request.form:
          gender = request.form['gender']  ##### Gender works: Thx to advice from D.
       age = request.form['age']
       year = request.form['year']
       month = request.form['month']
       day = request.form['day']
       country = request.form['country']
       state = request.form['state']
       city = request.form['city']
       county = request.form['county']
       village = request.form['village']
       other = request.form['other']
       sos = None
       if 'sos' in request.form:
          sos = request.form['sos']
       otherSOS = request.form['otherSOS']
       password = request.form['password']   #####  WORK ON HASHING and SALTING AT LATER DATE
       #password2 = request.form['password2'] ### if password2 == password:... else: error
       #automatic input
       signupDate = 12  #hard code for now
       
       if familyname and personalname and password: #for now to keep simple
          db = get_db()
          db.execute('INSERT INTO survivors (familyName, personalName, additionalName, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, password, signupDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                      [familyname, personalname, additionalname, gender, age, year, month, day, country, state, city, county, village, other, sos, otherSOS, password, signupDate])
          db.commit()
          session['personalname'] = request.form['personalname']
          session['message'] = "Celebrate, " + session['personalname'] + ", you're alive! Hip, hip, hooray!"
          return redirect(url_for('celebrate')) 
       else:
           error = "Not enough information to continue, please fill in all asterisked/starred items."
           return render_template('signupSurvivor.html', error = error)
    else: #request.method == 'GET'
       return render_template('signupSurvivor.html', error = None)


@app.route('/loginSurvivor', methods = ['GET', 'POST'])
def loginSurvivor():
    """Handles survivor login to update information (loginSurvivor.html)."""  #WIP:more info needed
    render_template('loginSurvivor.html')    
    error = None
    return render_template('loginSurvivor.html', error = error)
 #when logged in this should redirect(url_for('updateSurvivor'))

 #NOTE: SQL syntax may go something like UPDATE survivors SET column1=value, column2=value WHERE some_column=some_value
 #always use the WHERE statement with an SQL UPDATE statement
""" I need to have an update info page so that pulls current info, but also shows all updates once updated.  Only folks a person logged in can access his/her personal page. """
@app.route('/updateSurvivor', methods = ['GET', 'POST'])
def updateSurvivor():
   """Handles survivor update information, only accessible when logged in."""
   render_template('updateSurvivor.html')
   error = None
   return render_template('updateSurvivor.html', error = error)

#SEARCH VIEW FUNCTIONS
@app.route('/search', methods = ['POST', 'GET'])
def search():
    """Handles the search index screen (search.html)."""
    render_template('search.html', error = None)
    if request.method == 'POST':
        error = None
        message = ""
        
        #form inputs:
        familyname = request.form['familyname']
        personalname = request.form['personalname']
        additionalname = request.form['additionalname']
        gender = None
        if 'gender' in request.form:
           gender = request.form['gender']
        age = request.form['age']
        year = request.form['year']
        month = request.form['month']
        day = request.form['day']
        country = request.form['country']
        state= request.form['state']
        city = request.form['city']
        county = request.form['county']       
        village = request.form['village']
        other = request.form['other']

        if familyname and personalname: #for now to keep simple  ### Q) should I only pull the not null values?-es 4/6/17
           db = get_db()
           cur = db.execute("SELECT id, familyName, personalName, additionalName, gender, age, year, month, day, country, state, city, county, village, other, signupDate FROM survivors WHERE familyName=familyname AND personalName=personalname AND additionalName=additionalname AND gender=gender AND age=age AND year=year AND month=month AND day=day AND country=country AND state=state AND city=city AND county=county AND village=village AND other=other")             
           msgDB = ""
           rowCount = 0
           idList = []
           lastDate = 0
           for row in cur.fetchall():   #when adding row[] later: note position change(s) from selected db columns
              if familyname in row[1] and personalname in row[2]:  THIS WORKS
                 msgDB = msgDB + str(row[2] + " " + row[1]) + " ID # " + str(row[0]) + "... "
                 rowCount = rowCount + 1
                 idList = idList + [row[0]]
                 lastDate = lastDate + row[15]
              else:
                 msgDB = msgDB
                 rowCount = rowCount
                 idList = idList
                 lastDate = lastDate
                 
           if msgDB == "":
              error = "No such survivor with that name has enrolled with I'mAlive."
              return render_template('search.html', error = error)
           
           elif rowCount != 1: # multiple survivors with similar info
           #   newRowCount = 0
           #   msgDB2 = "For i in idList Message: "
           #   for i in idList:     ### would it be better to use length of idList????-Es 4/7/17
           #      if i == row[0] and (additionalname == row[3] or gender == row[4]):
####or age == row[5] or year == row[6] or month == row[7] or day == row[8] or country == row[9] or state == row[10] or city == row[11] or county == row[12] or village == row[13] or other == row[14]):
           #         newRowCount = newRowCount + 1
           #         msgDB2 = msgDB2 + str(row[2] + " " + row[1] + "ID# " + row[0])
           #         error = msgDB2 + " " +  str(newRowCount)
           #         if msgDB2 == "For i in idList Messag: ":     #basically nothing matching in row[]
           #            error = "[test 'for i in idList' msg:] I'mAlive has " + str(newRowCount) + " people with this information registered in its database: " + msgDB + " Please provide more detail. ID LIST TEST: " +str(idList)
           #            return render_template('search.html', error = error)
           #         elif newRowCount != 1:
           #         error = "[test 'newRowCount != 1' msg:] I'mAlive has " + str(newRowCount) + " people with this information registered in its database: " + msgDB2 + "Please provide more detail. ID LIST TEST: " + str(idList)
           #         return render_template('search.html', error = error)
           #          else:
           #            session['personalname'] = request.form['personalname']
           #            session['familyname'] = request.form['familyname']
           #            session['lastDate'] = request.form['lastDate']
           #            session['message'] = "[after iterating through additional data] msg: Celebrate! On " + str(session['lastDate']) + " " + session ['personalname'] + " " + session['familyname'] + " register with I'mAlive.  Hooray!!!!"
           #            return redirect(url_for('celebrate'))
           #      else:   
              error = "I'mAlive has " + str(rowCount) + " people with this information registered in its database: " + msgDB + " Please provide more detail." + " ID LIST TEST: " +str(idList)
              return render_template('search.html', error = error)
           
           else:#msgDB != "" and rowCount == 1
              session['personalname'] = request.form['personalname']
              session['familyname'] = request.form['familyname']
              session['lastDate'] = lastDate
              session['message'] = "Celebrate! On " + str(session['lastDate']) + " " + session ['personalname'] + " " + session['familyname'] + " registered with I'mAlive.  Hooray!"
              return redirect(url_for('celebrate'))
        else:  
            error = "Not enough information to continue; please provide both a family name, a personal name, and a gender. Thank you."
            return render_template('search.html', error = error)
    else: #request.method == 'GET'
        return render_template('search.html', error = None)
