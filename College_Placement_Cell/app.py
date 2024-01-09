from flask import Flask, request, render_template, redirect, url_for, session,jsonify,send_from_directory
#The Framework used is flask which containd different tools like render_template,url_for,redirect etc
from flask_mysqldb import MySQL #Using flask_mysqldb extension to connect python flask application with MySql
import details #User defined module which contain different variables and functionalities including CC point ranking
from datetime import datetime,date #To get current date and time...used multiple times in the project
import re #regular expression is used in this project to build the HIGH EFFICIENCY Search bar
import matplotlib.pyplot as plt  #importing pyplot as alias plt for bar graph 
import io #Used as a virtual Storage for graph png
import matplotlib # used to create graph (png formant in this project)
import base64  #Used to convert baseIO stored images into ASCII text during graph creation
import csv #to work with csv files
matplotlib.use('Agg')  # Use the Agg backend (non-interactive) to remove main loop errors



student_pfp="hello"
current_date = date.today()
current_date_str = current_date.strftime('%Y-%m-%d') #in yyyy-mm-dd format

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'amalahsanrohitrohan'  
app.config['TEMPLATES_AUTO_RELOAD'] = True  #To avoid running program manually after each template modification


#rout to handle error with code 500
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html'), 500


element_found=False 



# Database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'careerconnect'
app.config['MYSQL_DB'] = 'maindb'
mysql = MySQL(app)




############################################################################################login starts here###########################################
@app.route('/', methods=['GET', 'POST'])
def login():


    global element_found
    global hr_logged_in
    global student_logged_in
    global admin_logged_in
    if request.method == 'POST':
        user_id = request.form['user_id']
        password = request.form['password']
        # Check the user's role based on the email domain
        if user_id.endswith(details.student_userid_ends_with()):
            role = 'student'
            logintable='student_login'
            element_found=True
        elif user_id.endswith(details.admin_userid_ends_with()):
            role = 'college_admin'
            logintable='admin_login'
            element_found=True
        elif element_found==False:
            for x in details.company_hr_userid_ends_with():
                if user_id.endswith(x):
                    role = 'company_hr'
                    logintable='company_hr_login'
                    session["company_name"]=user_id[user_id.index("@")+1:-3] #find the name of the company from userid 
                    break

        else:
            session.clear()
            return "Invalid user ID"

        # Query the database to check if the user and password match
        cur = mysql.connection.cursor()
        cur.execute(f"SELECT * FROM {logintable} WHERE userid = %s AND password = %s", (user_id, password))
        user = cur.fetchone()
        cur.close()

        if user:
            # if  User exists, set a session variable for their role
            session['user_id'] = user[1]
            session['role'] = role

            current_datetime = datetime.now()

            login_date = current_datetime.date()
            login_time = current_datetime.time()
            cursor=mysql.connection.cursor()

            cursor.execute("INSERT INTO log_table(userid,designation,login_date,login_time) VALUES (%s,%s,%s,%s) ",(session['user_id'],session['role'],login_date,login_time))
            mysql.connection.commit()
            cursor.close()
            
            #Redirect to respective dashboard according to designation
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role == 'college_admin':
                session['year']=datetime.now().year
                return redirect(url_for('college_admin_dashboard'))
            elif role == 'company_hr':
                return redirect(url_for('company_hr_dashboard'))
        else:
            return redirect(url_for('invalid_login_credentials'))

    return render_template('login.html')
@app.route('/student_images/<path:filename>')
def student_images(filename):
    return send_from_directory('student_images', filename)


#If the login user is student different data is required to be pre-loaded
#The CC function is one among them and CC points have rank associated with them
#the rank is calculted by the details module
#Other values such as  uid, name , dob , student image etc are also fetched 

@app.route('/student_dashboard', methods=["GET", "POST"])
def student_dashboard():
    if 'user_id' in session and session['role'] == 'student':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT name,cgpa,dob,batch,points,graduation_year,student_pfp FROM student_details WHERE userid = %s", (session["user_id"],))
        details_of_student_for_session_dict = cursor.fetchone()
        session['student_name'] = details_of_student_for_session_dict[0]
        session['cgpa'] = details_of_student_for_session_dict[1]
        session['dob'] = details_of_student_for_session_dict[2]
        print(session['dob'])
        session['batch'] = details_of_student_for_session_dict[3]
        session['graduation_year'] = details_of_student_for_session_dict[5]
        global student_pfp
        student_pfp = base64.b64encode(details_of_student_for_session_dict[6]).decode('utf-8') if details_of_student_for_session_dict[6] else "hi"
        query = "SELECT COUNT(*) AS question_count FROM questions WHERE userid = %s AND status = 1"
        cursor.execute(query, (session['user_id'],))
        print(type(session['dob']))
        print(type(session['cgpa']))
        result = cursor.fetchone()
        session['cc_points'] = result[0]
        cursor.execute("UPDATE student_details SET points = %s WHERE userid = %s", (session['cc_points'], session['user_id']))
        mysql.connection.commit()
        cursor.close()
        return render_template(
            'student_dashboard.html',
            student_name=session['student_name'],
            student_uid=session['user_id'],
            student_dob=session['dob'],
            student_cgpa=session['cgpa'],
            student_branch=session['batch'],
            student_image=student_pfp,
            cc_points=session['cc_points'],
            student_pfp=student_pfp
        )
    else:
        return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect('/')
    
    file = request.files['file']

    if file.filename == '':
        return redirect('/')

    # Read image data
    image_data = file.read()


    # Save image data to the database
    cursor = mysql.connection.cursor()

    cursor.execute("UPDATE student_details SET student_pfp = %s WHERE userid = %s", (image_data, session['user_id']))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('student_dashboard'))




#Initial Route for College Admin after login
@app.route('/college_admin_dashboard')
def college_admin_dashboard():
    if 'user_id' in session and session['role'] == 'college_admin':
        return render_template("college_admin_dashboard.html",year=session['year'])
    
    else:
        return redirect(url_for('login'))



#The Initial route for company hr
#Contains various data which needs to be pre-loaded on login   
@app.route('/company_hr_dashboard')
def company_hr_dashboard():
    if 'user_id' in session and session['role'] == 'company_hr':
        
        cursor=mysql.connection.cursor()
        cursor.execute("SELECT power FROM interview_details WHERE company_name = %s", (session["company_name"],))
        power=cursor.fetchone()[0]
        if power==0:
            power="Placement Drive is OFF"
        else:
            power="Placement Drive is ON"
        cursor.execute("SELECT company_description,interview_detail FROM interview_details WHERE company_name = %s",(session["company_name"],))
        details_of_company=cursor.fetchone()
        cursor.execute("SELECT min_cgpa,batch,graduation_year FROM company_requirements WHERE company_name = %s",(session["company_name"],))
        company_requirements=cursor.fetchone()
        min_cgpa=company_requirements[0]
        branch=company_requirements[1]
        graduation_year=company_requirements[2]
        company_description=details_of_company[0]
        interview_detail=details_of_company[1]
        cursor.close()

        return render_template('company_hr_dashboard.html', company_name=session["company_name"],power=power,company_description=company_description,interview_detail=interview_detail,min_cgpa=min_cgpa,branch=branch,graduation_year=graduation_year)
    else:
        return redirect(url_for('login'))
    

@app.route('/login_failed')
def invalid_login_credentials():
    return "Invalid Details . Please Retry."

#############################################endpoints are mandatory for decorator function to work
#decorator functtion for hr of the company
def hr_required(view_function):
    def decorated_function(*args, **kwargs):
        if 'user_id' in session and session['role'] == 'company_hr':
            return view_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function



#decorator function for company admin
def admin_required(view_function):
    def decorated_function(*args, **kwargs):
        if 'user_id' in session and session['role'] == 'college_admin':
            return view_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function







#decorator function for students

def student_required(view_function):
    def decorated_function(*args, **kwargs):
        if 'user_id' in session and session['role'] == 'student':
            return view_function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return decorated_function






#####################################login ends here###############################################################


#####################################company hr starts here########################################################
# HR Dashboard - Set Requirements

@app.route('/hr_dashboard/set_requirements', methods=['GET', 'POST'], endpoint='set_requirements_endpoint')
@hr_required  #here no error
def set_requirements():

    if request.method == 'POST':
        min_cgpa = request.form.get('cgpa')
        graduation_year=request.form.get('passoutyear')
        temp_batch= request.form.get('additionalRequirement')
        temp_batch=temp_batch.upper()
        

        # Establish a database connection using the mysql object
        cur = mysql.connection.cursor()

        # Update company requirements in the database
        cur.execute("UPDATE company_requirements SET min_cgpa = %s, graduation_year = %s, batch = %s WHERE company_name = %s", (min_cgpa, graduation_year,temp_batch,session["company_name"]))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('company_hr_dashboard'))

    return render_template('change_interview_requirements.html')

#For displaying current requirement

@app.route('/hr_dashboard/current_requirements', endpoint='current_requirements_endpoint')
@hr_required 
def current_requirements():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM company_requirements WHERE company_name = %s", (session['company_name'],))
    temp = cur.fetchone()
    cur.close()

    if temp is not None:
        return render_template('current_requirements.html', requirement1=temp[2], requirement2=temp[3], requirement3=temp[4].upper())
    



@app.route('/hr_dashboard/eligible_students',endpoint="eligible_students_endpoint")
@hr_required
def eligible_students():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM company_requirements WHERE company_name = %s" , (session['company_name'],))
    temp_company_requirements = cur.fetchone()
    batch_details=tuple(temp_company_requirements[4].upper().split(","))

    cur.execute("SELECT * FROM student_details a WHERE cgpa >= %s AND graduation_year= %s AND batch in %s", (temp_company_requirements[2],temp_company_requirements[3],batch_details))
    eligible_students_data = cur.fetchall()
    cur.close()

    return render_template('eligible_students.html',eligible_students=eligible_students_data)


#code for applied students
@app.route('/hr_dashboard/applied_candidates',endpoint="applied_students_endpoint")
@hr_required
def applied_students():
    cur=mysql.connection.cursor()
    cur.execute("""
    SELECT * 
    FROM student_details AS SD
    JOIN applied_companies AS AC
    ON SD.userid = AC.user_id 
    WHERE AC.company_name = %s
""", (session['company_name'],))

    applied_students_details=cur.fetchall()
    cur.close()
    return render_template('applied_candidates.html',applied_students=applied_students_details)




#code to start/stop placement drive
@app.route('/hr_dashboard/toggle_power', endpoint='toggle_power_endpoint')
@hr_required
def toggle_power():
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT power FROM interview_details WHERE company_name = %s", (session['company_name'],))
    current_power = cur.fetchone()[0]
    new_power = 1 - current_power

    # Update the power value in the database
    cur.execute("UPDATE interview_details SET power = %s WHERE company_name = %s", (new_power, session['company_name']))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('company_hr_dashboard'))


#set interview Details

@app.route("/hr_dashboard/change_interview_details",methods=['GET', 'POST'],endpoint="edit_interview_details_endpoint")
@hr_required
def edit_interview_details():
    if request.method == 'POST':
        content = request.form['content']  # Get the edited content from the POST request
        interview_date=request.form['interview_date']
        interview_deadline=request.form['last_date']
        cur = mysql.connection.cursor()
        cur.execute("UPDATE interview_details SET interview_detail = %s , interview_date = %s , last_date = %s  WHERE company_name = %s", (content, interview_date, interview_deadline, session['company_name']))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('company_hr_dashboard'))
    return render_template("change_interview_details.html")




#define the logout function
@app.route('/hr_dashboard/logout',endpoint="logout_endpoint")
@hr_required
def logout():
    session.clear()
    return redirect(url_for('login'))


#define the edit company details function
@app.route('/hr_dashboard/change_company_details', methods=['GET', 'POST'], endpoint="company_details_endpoint")
@hr_required
def change_company_details():
    if request.method == 'POST':
        content = request.form['content']  
        cur = mysql.connection.cursor()
        cur.execute("UPDATE interview_details SET company_description = %s WHERE company_name = %s", (content, session['company_name']))
        mysql.connection.commit()
        cur.close()
        success_message = "Save Success"
        response = jsonify({'message': success_message})
        response.status_code = 200
        return response

    return render_template("change_company_details.html")

# Function to update application status in the applied_companies table
def update_application_status(user_id, decision):
    
    cursor=mysql.connection.cursor()

    # Update the application_status based on the decision
    if decision == 'accept':
        update_query = "UPDATE applied_companies SET application_status = 1 WHERE user_id = %s AND company_name = %s"
    elif decision == 'reject':
        update_query = "UPDATE applied_companies SET application_status = 0 WHERE user_id = %s AND company_name = %s"
    elif decision == 'wait':
            update_query = "UPDATE applied_companies SET application_status = 2 WHERE user_id = %s AND company_name = %s"
    else:
        raise ValueError("Invalid decision")

    cursor.execute(update_query, (user_id,session['company_name']))
    mysql.connection.commit()
    cursor.close()

# Route to display the application scrutiny page
@app.route('/hr_dashboard/application_scrutiny',endpoint="application_scurtiny_endpoint")
@hr_required
def application_scrutiny():
    # Dummy data (replace with actual data retrieval logic)
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT AC.user_id,AC.student_name,SD.batch,application_status FROM applied_companies AS AC JOIN student_details AS SD ON AC.user_id = SD.userid WHERE AC.company_name = %s",(session['company_name'],))
    students=list(cursor.fetchall())
    return render_template('scrutiny.html', students=students)

# Route to process the decision made for each student
@app.route('/hr_dashboard/process_decision', methods=['POST'])
def process_decision():
    user_id = request.form.get('user_id')
    decision = request.form.get('decision')

    update_application_status(user_id, decision)

    return redirect(url_for('application_scurtiny_endpoint'))




######################################################company hr ends here############################


######################################################Student Starts here################################




#Display the name and option to apply for all eligible companies . 
#Eligiblity is subject to many factors including Cgpa, branch, Interview Deadline date etc


@app.route('/student_dashboard/eligible_companies', endpoint="eligible_companies_endpoint")
@student_required
def eligible_companies():
    print(session)
    cur = mysql.connection.cursor()
    print(session['dob'])
    if details.is_valid_date(session['dob']):
        pass
    else:
        date_str = session['dob']
        parsed_date = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %Z')
        session['dob'] = parsed_date.strftime('%Y-%m-%d') 


    cur.execute("""
        SELECT CR.company_name
        FROM company_requirements AS CR
        JOIN interview_details AS ID ON CR.company_name = ID.company_name
        WHERE CR.min_cgpa <= %s
        AND CR.graduation_year = %s
        AND CR.batch LIKE %s
        AND ID.power = 1
        AND ID.last_date > %s
        """, (session['cgpa'], session['graduation_year'], '%' + session['batch'] + '%', current_date_str))
    companies = cur.fetchall()    
    if len(companies)>0:
        data = companies
        companies = tuple(item for sublist in data for item in sublist)
    cur.execute("SELECT DISTINCT company_name FROM applied_companies WHERE user_id = %s",(session['user_id'],))
    see_applied_companies = cur.fetchall()
    if see_applied_companies!=():
        see_applied_companies = tuple(item[0] for item in see_applied_companies)

    cur.close()
    return render_template("eligible_companies.html", companies=companies,existing_companies=see_applied_companies)


#If a student applies to an eligible company add the assosicated data into applied_companies table
@app.route('/student_dashboard/handle_application', methods=['POST'],endpoint="handle_application_endpoint")
@student_required
def handle_application():    
    action=request.form.get('action')
    if action=='apply':
        company_name=request.form.get('company_name')
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO applied_companies (user_id,student_name,company_name,application_status) VALUES (%s,%s,%s,%s)",(session['user_id'],session['student_name'],company_name,2))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('eligible_companies_endpoint'))


#This function provides an interface where students can view details about the interview and company
#The application deadline and interview date is also mentioned


@app.route('/student_dashboard/view_inerview_details',methods=['POST'],endpoint="view_interview_details_endpoint")
@student_required
def view_interview_details():
    action=request.form.get('action')
    if action == 'see_interview_details':
        company_name=request.form.get('company_name')
        cur=mysql.connection.cursor()
        cur.execute("SELECT interview_detail,last_date,interview_date,company_description FROM interview_details where company_name = %s",(company_name,))
        view_interview_details_data=cur.fetchone()
        cur.close()
    return render_template(
        "view_interviewdetails.html",
        company_name=company_name,
        interview_detail=view_interview_details_data[0],
        interview_date=view_interview_details_data[2],
        last_date=view_interview_details_data[1],
        company_description=view_interview_details_data[3] 
        )

@app.route('/student_dashboard/post_questions', methods=['GET','POST'], endpoint='post_question_endpoint')
@student_required
#2 for waiting question approval
#1 for approved questtions
#0 for rejected questtions
def post_questions():
    if request.method == 'POST':
        tags = request.form.get('tags')
        c_name=request.form.get('c_name')
        content = request.form.get('content')
        cur=mysql.connection.cursor()
        question_date=datetime.now().strftime("%Y-%m-%d")
        if tags !=None and c_name != None:
            cur.execute("INSERT INTO questions(tags,userid,username,question,status,question_date,company_name) VALUES (%s,%s,%s,%s,%s,%s,%s)",(tags,session['user_id'],session['student_name'],content,2,question_date,c_name))
            mysql.connection.commit()
            cur.close()
            print("hi")
        return redirect(url_for('student_dashboard'))
    return render_template("post_interview_questions.html")



#To view all the question approved by the Admin
@app.route('/student_dashboard/view_questions', methods=['GET','POST'], endpoint='view_question_endpoint')
@student_required
def view_questions():
    if request.method == 'GET':
        cur=mysql.connection.cursor()
        cur.execute("""
            SELECT Q.username, Q.userid, Q.question, Q.question_date, Q.tags, Q.company_name, SD.points , Q.q_id
            FROM questions AS Q
            JOIN student_details AS SD ON Q.userid = SD.userid
            WHERE Q.status = 1 
            ORDER BY Q.q_id DESC
        """)
        all_questions=cur.fetchall()
        questions_data=list(all_questions)
        cur.close()
        questions_data1=[]
        for question in questions_data:
            rank = details.choose_rank(question[6])
            font_style=rank[0]
            name_color=rank[1]
            style=rank[2]
            weight=rank[3]
            size=rank[4]
            question+=(font_style,name_color,style,weight,size)
            questions_data1.append(question)
        cur=mysql.connection.cursor()
        cur.execute("SELECT COUNT(q_id) FROM questions")
        total_questions=cur.fetchone()
        cur.close()

        


    return render_template('questions.html', questions_data=questions_data1,q_suffix=details.q_suffix(),q_prefix=details.q_prefix(),total_questions=total_questions,items_per_page=10)

#definig the function to view your interview result
@app.route('/student_dashboard/view_result',endpoint="view_result_endpoint")
@student_required
def view_result():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT company_name,application_status FROM applied_companies WHERE user_id = %s",(session['user_id'],))
    interview_results=list(cursor.fetchall())
    cursor.close()
    return render_template('results.html', interview_results=interview_results)


#to view all your question metadata(question id,date,company name etc)
@app.route('/student_dashboard/view_my_questions',endpoint="view_my_question_endpoint")
@student_required
def view_my_questions():
    cursor=mysql.connection.cursor()
    cursor.execute("SELECT q_id,company_name,question_date,status FROM questions WHERE userid = %s ORDER BY q_id DESC",(session['user_id'],))
    questions=list(cursor.fetchall())
    cursor.close()
    return render_template('myquestions.html', questions=questions ,prefix=details.q_prefix(),suffix=details.q_suffix())


#To view the question from metadata(question id, date etc) in 'your questions'
@app.route('/student_dasboard/view_my_questions/view_the_question',methods=["GET","POST"],endpoint="view_the_question_endpoint")
@student_required
def view_the_question():
    action=request.form.get('action')
    if action=='apply':
        q_id=request.form.get('q_id')
        cur=mysql.connection.cursor()
        cur.execute("SELECT question FROM questions WHERE q_id = %s ",(q_id,))
        the_question=cur.fetchone()
        cur.close()
    return render_template('the_question.html',the_question=the_question[0])


#used to search for a question based on student name,tags, company name etc
#One of the most interesting part of the project
@app.route('/student_dashboard/view_question/questions_search', methods=['GET'],endpoint="questions_search_endpoint")
@student_required
def questions_search():
    search_text = request.args.get('search_text').lower()


    if search_text:
        cur=mysql.connection.cursor()
        cur.execute("""
            SELECT Q.username, Q.userid, Q.question, Q.question_date, Q.tags, Q.company_name, SD.points , Q.q_id
            FROM questions AS Q
            JOIN student_details AS SD ON Q.userid = SD.userid
            WHERE Q.status = 1
            ORDER BY Q.question_date DESC
        """)
        all_questions=cur.fetchall()
        questions_data=list(all_questions)
        cur.close()
        questions_data1=[]
        for question in questions_data:
            rank = details.choose_rank(question[6])
            font_style=rank[0]
            name_color=rank[1]
            style=rank[2]
            weight=rank[3]
            size=rank[4]
            question+=(font_style,name_color,style,weight,size)

            #using regular expression to create a search bar with high efficiency
            #used to retrieve data from any where inside a question

            if (re.search(r'{}'.format(re.escape(search_text)),str(question[0]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[1]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[2]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[3]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[4]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[5]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[6]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[7]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(details.q_prefix().lower()+str(question[7]).lower())+details.q_suffix().lower())):
                questions_data1.append(question)
    else:
        return redirect(url_for('view_question_endpoint'))


    return render_template('questions.html', questions_data=questions_data1,q_suffix=details.q_suffix(),q_prefix=details.q_prefix())
       
    




@app.route('/student_dashboard/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


############################################studen dashboard ends here###############
############################################admin dashboard starts here##############


@app.route("/college_admin_dashboard_main", endpoint="college_admin_dashboard_main_endpoint")
@admin_required
def college_admin_dashboard():
    print(session['year'])

    
    return render_template('college_admin_dashboard.html',year=session['year'])



@app.route('/college_admin_dashboard_main/set_year', methods=['POST'])
def set_year():
    if request.method == 'POST':
        year = request.form.get('year')
        if year is not None:
            session['year'] = int(year)
            return redirect(url_for('college_admin_dashboard'))
    return 'Invalid request'


def generate_bar_graph1(respective_company_placements):

    companies=details.company_list
    colors = ['red', 'green', 'blue', 'orange', 'purple', 'pink', 'cyan', 'brown', 'gray', 'lime']


    plt.bar(companies,
            respective_company_placements,color=colors)
    plt.xlabel("<----Category---->")
    plt.ylabel("<----Values---->")
    plt.xticks(rotation=90)

    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    plt.close()

    return image_base64

#defining the general company report
@app.route('/admin_dashboard/companies/general_report',endpoint="company_general_report_endpoint")
@admin_required
def company_general_report():
    print(session['year'])



    total_no_of_recruiting_companies=len(details.company_hr_userid_ends_with())
    cursor=mysql.connection.cursor()

    cursor.execute("""
    SELECT ac.company_name, COUNT(*) AS accepted_students_count
    FROM applied_companies ac
    JOIN student_details sd ON ac.user_id = sd.userid
    WHERE ac.application_status = 1 AND sd.graduation_year = %s
    GROUP BY ac.company_name
    HAVING COUNT(*) = (
        SELECT COUNT(*) AS max_count
        FROM applied_companies ac_inner
        JOIN student_details sd_inner ON ac_inner.user_id = sd_inner.userid
        WHERE ac_inner.application_status = 1 AND sd_inner.graduation_year = %s
        GROUP BY ac_inner.company_name
        ORDER BY max_count DESC
        LIMIT 1)
""", (session['year'], session['year']))


    top_recruiter=cursor.fetchall()
          
          
    placement_counts = []
    #for each company mentioned in details.company_list find the number of students who got placed
    for company in details.company_list:
        query = ("""SELECT COUNT(*) FROM applied_companies ac 
    JOIN student_details sd ON ac.user_id = sd.userid 
    WHERE ac.company_name = %s AND ac.application_status = 1 AND sd.graduation_year = %s""")
        cursor.execute(query, (company,session['year']))
        placement_count = cursor.fetchone()[0]
        placement_counts.append(placement_count)
        
    #select the bottom recruiting company
          
    cursor.execute("""
    SELECT ac.company_name, COUNT(*) AS accepted_students_count
    FROM applied_companies ac
    JOIN student_details sd ON ac.user_id = sd.userid
    WHERE ac.application_status = 1 AND sd.graduation_year = %s
    GROUP BY ac.company_name
    HAVING COUNT(*) = (
        SELECT COUNT(*) AS max_count
        FROM applied_companies ac_inner
        JOIN student_details sd_inner ON ac_inner.user_id = sd_inner.userid
        WHERE ac_inner.application_status = 1 AND sd_inner.graduation_year = %s
        GROUP BY ac_inner.company_name
        ORDER BY max_count 
        LIMIT 1)
""", (session['year'], session['year']))



    bottom_recruiter=cursor.fetchall()
    #select top acceptence rate
    cursor.execute("""
        WITH RecruitmentData AS (
            SELECT 
                ac.company_name,
                SUM(CASE WHEN ac.application_status = 1 AND sd.graduation_year = %s THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0) * 100 AS recruitment_percentage
            FROM 
                applied_companies ac
            JOIN 
                student_details sd ON ac.user_id = sd.userid
            WHERE
                sd.graduation_year = %s
            GROUP BY 
                ac.company_name
        )

        SELECT 
            company_name,
            recruitment_percentage
        FROM 
            RecruitmentData
        WHERE 
            recruitment_percentage = (SELECT MAX(recruitment_percentage) FROM RecruitmentData);
    """, (session['year'], session['year']))

    top_acceptance_rate = cursor.fetchall()

    # Fetch bottom acceptance rate data from MySQL
    cursor.execute("""
        WITH RecruitmentData AS (
            SELECT 
                ac.company_name,
                SUM(CASE WHEN ac.application_status = 1 AND sd.graduation_year = %s THEN 1 ELSE 0 END) /
                NULLIF(COUNT(*), 0) * 100 AS recruitment_percentage
            FROM 
                applied_companies ac
            JOIN 
                student_details sd ON ac.user_id = sd.userid
            WHERE
                sd.graduation_year = %s
            GROUP BY 
                ac.company_name
        )

        SELECT 
            company_name,
            recruitment_percentage
        FROM 
            RecruitmentData
        WHERE 
            recruitment_percentage = (SELECT MIN(recruitment_percentage) FROM RecruitmentData);
    """, (session['year'], session['year']))

    bottom_acceptance_rate = cursor.fetchall()
    top_acceptance_rate_companies=list(map(lambda x:x[0],top_acceptance_rate ))
    bottom_acceptance_rate_companies=list(map(lambda x:x[0],bottom_acceptance_rate ))
    try:
        top_acceptance_rate,bottom_acceptance_rate=[top_acceptance_rate[0][1],100-top_acceptance_rate[0][1]],[bottom_acceptance_rate[0][1],100-bottom_acceptance_rate[0][1]]
    
        top_acceptance_rate_companies=" , ".join(top_acceptance_rate_companies)
        bottom_acceptance_rate_companies=" , ".join(bottom_acceptance_rate_companies)
        top_recruiter_number=top_recruiter[0][1]
        top_recruiter=",".join(i[0] for i in top_recruiter)
        
        
        bottom_recruiter_number=bottom_recruiter[0][1]
        bottom_recruiter=",".join(i[0] for i in bottom_recruiter)

    except:
        print(top_acceptance_rate,bottom_acceptance_rate,top_acceptance_rate_companies,bottom_acceptance_rate_companies,bottom_recruiter,top_recruiter,sep="-----------")
        return render_template("nothing_to_show.html")

    cursor.close()
    return render_template('companies.html',total_no_of_recruiting_companies=total_no_of_recruiting_companies,
                           har=str(top_acceptance_rate_companies)+" : "+str(round(float(top_acceptance_rate[0]),2)),
                           top_recruiter=top_recruiter+" : "+str(top_recruiter_number),
                           least_recruiter=bottom_recruiter+" : "+str(bottom_recruiter_number),
                           lar=str(bottom_acceptance_rate_companies)+" : "+str(round(float(bottom_acceptance_rate[0]),2)),
                           graph_image_company1=generate_bar_graph1(placement_counts))

#Function to generate bar graph whith bars of different colors
#Once the graph in generted it is saved in virtual memory bytesIO
#The png file inside bytesIO is converted into ASCII using the base64 module to embed the ASCII text in html
def generate_bar_graph(total_no_of_students,total_no_of_applied_students,total_no_of_placed_students):

    colors = ['blue', 'orange', 'green']

    plt.bar(['Total', 'Applied', 'Placed'],
            [total_no_of_students[0][0], total_no_of_applied_students[0][0], total_no_of_placed_students[0][0]],color=colors)
    plt.xlabel("<----Category---->")
    plt.ylabel("<----Values---->")
    plt.title("Graph")

    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    plt.close()

    return image_base64

#create a general report for students
@app.route('/admin_dashboard/students/general_report',endpoint="student_general_report_endpoint")
@admin_required

def student_general_report():

    cursor=mysql.connection.cursor()
    cursor.execute("SELECT COUNT(DISTINCT userid) FROM student_details WHERE graduation_year = %s", (session['year'],))

    total_no_of_students=cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(DISTINCT ac.user_id)  
        FROM applied_companies ac
        JOIN student_details sd ON ac.user_id = sd.userid
        WHERE sd.graduation_year = %s
    """, (session['year'],))

    total_no_of_applied_students=cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(DISTINCT ac.user_id)
        FROM applied_companies ac
        JOIN student_details sd ON ac.user_id = sd.userid
        WHERE ac.application_status = 1 AND sd.graduation_year = %s
    """, (session['year'],))

    total_no_of_placed_students=cursor.fetchall()

    try:
        pp=round(total_no_of_placed_students[0][0]/total_no_of_applied_students[0][0]*100,2)
    except:
        return render_template("nothing_to_show.html")



    return render_template("students.html",tnos=total_no_of_students[0][0],
                           tnoas=total_no_of_applied_students[0][0],
                           tnops=total_no_of_placed_students[0][0],
                           pp=pp,
                           graph_image=generate_bar_graph(total_no_of_students,total_no_of_applied_students,total_no_of_placed_students))



#The search Bar Function ---same as student interview quesion search bar using RE
@app.route('/admin_dashboard/view_question/questions_search', methods=['GET'],endpoint="admin_questions_search_endpoint")
@admin_required

def questions_search():
    search_text = request.args.get('search_text').lower()


    if search_text:
        cur=mysql.connection.cursor()
        cur.execute("""
            SELECT Q.username, Q.userid, Q.question, Q.question_date, Q.tags, Q.company_name, SD.points , Q.q_id, Q.status
            FROM questions AS Q
            JOIN student_details AS SD ON Q.userid = SD.userid
            
            ORDER BY Q.q_id DESC
        """)
        all_questions=cur.fetchall()
        questions_data=list(all_questions)
        cur.close()
        questions_data1=[]
        for question in questions_data:
            rank = details.choose_rank(question[6])
            font_style=rank[0]
            name_color=rank[1]
            style=rank[2]
            weight=rank[3]
            size=rank[4]
            question+=(font_style,name_color,style,weight,size)
            if (re.search(r'{}'.format(re.escape(search_text)),str(question[0]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[1]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[2]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[3]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[4]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[5]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[6]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(question[7]).lower()) or
                re.search(r'{}'.format(re.escape(search_text)),str(details.q_prefix().lower()+str(question[7]).lower())+details.q_suffix().lower())):
                questions_data1.append(question)
    else:
        return redirect(url_for('admin_view_question_endpoint'))


    return render_template('questions_approval.html', questions_data=questions_data1,q_suffix=details.q_suffix(),q_prefix=details.q_prefix())



#The admin can view questions like what the students will see and deceide wheter to accept or reject a particular question
@app.route('/admin_dashboard/view_question', endpoint="admin_view_question_endpoint")
@admin_required

def admin_view_question():
    cur = mysql.connection.cursor()
    cur.execute("""
            SELECT Q.username, Q.userid, Q.question, Q.question_date, Q.tags, Q.company_name, SD.points , Q.q_id, Q.status
            FROM questions AS Q
            JOIN student_details AS SD ON Q.userid = SD.userid
            ORDER BY Q.q_id DESC
        """)
    all_questions=cur.fetchall()
    questions_data=list(all_questions)
    cur.close()
    questions_data1=[]
    for question in questions_data:
        rank = details.choose_rank(question[6])
        font_style=rank[0]
        name_color=rank[1]
        style=rank[2]
        weight=rank[3]
        size=rank[4]
        question+=(font_style,name_color,style,weight,size)
        questions_data1.append(question)
    cur=mysql.connection.cursor()
    cur.execute("SELECT COUNT(q_id) FROM questions")
    total_questions=cur.fetchone()
    cur.close()


        


    return render_template('questions_approval.html', questions_data=questions_data1,q_suffix=details.q_suffix(),q_prefix=details.q_prefix(),total_questions=total_questions,items_per_page=10)


#To update the new question status in database
@app.route('/update_question_status/<int:question_id>/<int:status>')
def update_question_status(question_id, status):
    update_question_in_database(question_id, status)
    return redirect(url_for('admin_view_question_endpoint'))

def update_question_in_database(question_id, status):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE questions SET status = %s WHERE q_id = %s", (status, question_id))
    mysql.connection.commit()
    cur.close()

#indivicual report for each student
@app.route('/admin_dashboard/student/individual_report' , endpoint="s_individual_report_endpoint")
@admin_required

def student_individual_report():
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT s.userid, s.name, COUNT(ac.company_name) AS num_applied,
                SUM(ac.application_status = 1) AS num_placed,
                SUM(ac.application_status = 0) AS num_rejected,
                s.batch, ac.company_name, ac.application_status
        FROM student_details s 
        LEFT JOIN applied_companies ac ON s.userid = ac.user_id
        WHERE s.graduation_year = %s
        GROUP BY s.userid, s.name, s.batch, ac.company_name, ac.application_status;
    """, (session['year'],))



    data = cur.fetchall()
    cur.execute("""
        SELECT s.userid, s.name, COUNT(ac.company_name) AS num_applied,
            SUM(ac.application_status = 1) AS num_placed,
            SUM(ac.application_status = 0) AS num_rejected,
            s.batch
        FROM student_details s 
        LEFT JOIN applied_companies ac ON s.userid = ac.user_id
        WHERE s.graduation_year = %s
        GROUP BY s.userid, s.name, s.batch;
    """, (session['year'],))

    
    data1=cur.fetchall()
    cur.close()

    temp_list=[]
    count_temp=0
    j=data1[count_temp]
    for i in data:

        #making sure no redundancy cause error(not required for real data)
        if i[0]!=j[0] or i[1]!=j[1] or i[5]!=j[5]:


            count_temp+=1
        j=data1[count_temp]
        total_applied=j[2]
        accepted=j[3]
        rejected=j[4]
        status="PENDING"
        if i[7]==1:
            status="PLACED"
        elif i[7]==0:
            status="REJECTED"
        else:
            pass
        temp_tuple=(i[0],i[1],i[5],total_applied,accepted,i[6],rejected,status)
        temp_list.append(temp_tuple)

    data=tuple(temp_list)


    return render_template('student_individual_report.html', data=data)


#bar Graph for branch


def generate_bar_graph_branch(branches,placed_list):

    colors = ['blue', 'orange', 'green', 'red', 'purple', 'pink', 'brown', 'gray', 'cyan']


    plt.bar(
            placed_list,branches,color=colors)
    plt.xlabel("<----Branch---->")
    plt.ylabel("<----No of Applications---->")
    plt.title("Branch Placement Graph")

    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png')
    image_stream.seek(0)

    image_base64 = base64.b64encode(image_stream.read()).decode('utf-8')

    plt.close()

    return image_base64

#individual report for each branch
@app.route('/admin_dashboard/branch/individual_report' , endpoint="b_individual_report_endpoint")
@admin_required

def branch_individual_report():
    cur = mysql.connection.cursor()

    branch_individual_report = []

    for i in details.branch_list:
        cur.execute("""
            SELECT  COUNT(ac.company_name) AS num_applied,
                    SUM(ac.application_status = 1) AS num_placed,
                    SUM(ac.application_status = 0) AS num_rejected
            FROM student_details s 
            LEFT JOIN applied_companies ac ON s.userid = ac.user_id 
            WHERE s.graduation_year = %s AND s.batch = %s;
        """, (session['year'], i))


        data = cur.fetchone()+(i,)
        branch_individual_report.append(data)

    
    
    cur.close()
    placed_list=[]
    for i in branch_individual_report:
        placed_list.append(i[0])
    return render_template("branch_individual_report.html",graph_image=generate_bar_graph_branch(placed_list,details.branch_list),branch_individual_report=branch_individual_report)

#the log table with name ,designation, login date and time
@app.route('/admin_dashboard/log_table' , endpoint="log_table_endpoint")
@admin_required

def log_table():

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM log_table ORDER BY id DESC")
    log_entries = cursor.fetchall()
    cursor.close()
    return render_template('log_table.html',log_entries=log_entries)

#admin logout function
@app.route('/admin_dashboard/logout' , endpoint="admin_logout_endpoint")
def admin_logout():
    session.clear()
    return redirect(url_for("login"))




@app.route('/admin_dashboard/upload_student_details_csv', methods=['POST'],endpoint="upload_student_details_csv_endpoint")
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        # Read CSV file and insert data into the database
        csv_data = csv.reader(file.stream.read().decode('utf-8').splitlines())
        next(csv_data)  # Skip header row

        cur = mysql.connection.cursor()

        for row in csv_data:
            userid, password, name, cgpa, dob, batch, points, graduation_year = row
            cur.execute("INSERT INTO student_details (userid, password, name, cgpa, dob, batch, points, graduation_year) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                           (userid, password, name, cgpa, dob, batch, points, graduation_year))

            cur.execute("INSERT INTO student_login (userid, password) VALUES (%s,%s)",(userid, password))

        mysql.connection.commit()
        cur.close()

        return redirect(url_for('college_admin_dashboard'))

@app.route('/admin_dashboard/delete_table', methods=['POST'],endpoint="admin_delte_table")
def delete_database():
    cur = mysql.connection.cursor()
    cur.execute("DROP TABLE student_details")
    cur.execute("DROP TABLE student_login")
    mysql.connection.commit()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS student_details (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    userid VARCHAR(50) NOT NULL,
                    password VARCHAR(50) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    cgpa FLOAT NOT NULL,
                    dob DATE NOT NULL,
                    batch VARCHAR(50) NOT NULL,
                    points INT NOT NULL,
                    applied_companies VARCHAR(255),
                    graduation_year INT,
                    accepted_companies VARCHAR(255),
                    rejected_companies VARCHAR(255),
                    student_pfp MEDIUMBLOB
                    
                )
            """)
    cur.execute("""
                CREATE TABLE IF NOT EXISTS student_login (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    userid VARCHAR(50) NOT NULL,
                    password VARCHAR(50) NOT NULL
                )
            """)
    cur.close()
    return redirect(url_for('college_admin_dashboard'))




#define in later version
@app.route('/admin_dashboard/database' , endpoint="admin_database_endpoint")
def database_table():

    return render_template('admin_database.html')


@app.route('/admin_dashboard/systems' , endpoint="systems_endpoint")
def database_table():

    return render_template('admin_system.html')


if __name__ == '__main__':
    app.run(debug=True)
