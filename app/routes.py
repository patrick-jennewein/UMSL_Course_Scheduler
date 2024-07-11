from flask import render_template, request, json
from app import app
from app.middleware.course_parsing import parse_courses, generate_semester

@app.route('/')
@app.route('/index')
def index():
    # set up defaults
    semesters = ["Fall", "Spring"]
    certificates = [
        ("Artificial Intelligence", "AICERTReq"),
        ("Cybersecurity", "CYBERCERTReq"),
        ("Data Science", "DATACERTReq"),
        ("Mobile Apps and Computing", "MOBILECERTReq"),
        ("Internet and Web", "WEBCERTReq")
    ]

    # create a list of all courses
    all_courses = parse_courses()
    all_courses_list = []
    for course in all_courses.items():
        prerequisite_description = ""
        if "prerequisite_description" in course[1].keys():
            prerequisite_description = course[1]["prerequisite_description"]
        course_info = {
            "course": course[0],
            "credits": course[1]["credit"],
            "course_number": course[1]["course_number"],
            "prerequisite_description": prerequisite_description
        }
        all_courses_list.append(course_info)
    all_courses_list = sorted(all_courses_list, key=lambda d: d["course"])

    return render_template('index.html',
                           initial_load=True,
                           required_courses=all_courses_list,
                           required_courses_dict=json.dumps(all_courses),
                           json_required_courses=json.dumps(all_courses_list),
                           semesters=semesters,
                           certificates=certificates,
                           cert_elective_courses_still_needed=0,#DROP
                           total_credits=0,
                           course_schedule=json.dumps([]),
                           include_summer=False,
                           semester_number=0,
                           minimum_semester_credits=list(map(lambda x: x, range(3, 22))), # create list for minimum credits dropdown
                           min_degree_electives=0,
                           starting_credits=list(map(lambda x: x, range(0, 201))), # create list for minimum credits dropdown
                           gen_ed_credits_still_needed=27,
                           minimum_summer_credits = list(map(lambda x: x, range(1, 13))),
                           semester_years = json.dumps({}),
                           user_name = "Student",
                           ge_taken = 0,
                           fe_taken = 0,
                           degree_choice = "BSComputerScience",
                           is_graduated = False,
                           required_courses_tuple = json.dumps([]),
                           certificate_choice = json.dumps([]),
                           selected_certificates = json.dumps([]),
    )

@app.route('/schedule', methods=["POST"])
def schedule_generator():
    if request.form.get('Print'):
        course_schedule_display = json.loads(request.form["course_schedule"])
        total_credits = int(request.form["total_credits"])
        min_degree_electives = int(request.form["min_degree_electives"])
        cert_elective_courses_still_needed = int(request.form["cert_elective_courses_still_needed"])
        ge_taken = 27 - int(request.form["gen_ed_credits_still_needed"])
        fe_taken = int(request.form["fe_taken"])
        degree_choice = str(request.form["degree_choice"])
        c = json.loads(request.form["certificate_choice"])
        user_name = request.form["user_name"]
        if(c != ""):
            certificate = c[0]
        else:
            certificate = ""
        total_elective_credits = int(request.form["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"])
        return render_template('printable.html',
                            course_schedule_display=course_schedule_display,
                            total_credits = total_credits,
                           min_degree_electives = min_degree_electives,
                           cert_elective_courses_still_needed = cert_elective_courses_still_needed,
                           ge_taken = ge_taken,
                           fe_taken = fe_taken,
                           degree_choice = degree_choice,
                           certificate = certificate,
                           total_elective_credits = total_elective_credits,
                           user_name = user_name)
    else:
        try:
            render_info = None
            if request.form.get('upload'):
                render_info = get_render_info_from_upload(request)
            else:
                render_info = generate_semester(request)
            return render_template('index.html',
                                required_courses_dict_list=render_info["required_courses_dict_list"],
                                required_courses_dict_list_unchanged=render_info["required_courses_dict_list_unchanged"],
                                semesters=render_info["semesters"],
                                total_credits=render_info["total_credits"],
                                course_schedule=render_info["course_schedule"],
                                course_schedule_display=render_info["course_schedule_display"],
                                courses_taken=render_info["courses_taken"],
                                list_of_required_courses_taken_display = render_info["list_of_required_courses_taken_display"],
                                semester_number=render_info["semester_number"],
                                waived_courses=render_info["waived_courses"],
                                current_semester=render_info["current_semester"],
                                minimum_semester_credits=render_info["minimum_semester_credits"],
                                min_degree_electives=render_info["min_degree_electives"],
                                include_summer=render_info["include_summer"],
                                certificates=render_info["certificate_choice"],
                                certificates_display = render_info["certificates_display"],
                                cert_elective_courses_still_needed=render_info["cert_elective_courses_still_needed"], #DROP
                                TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES=render_info["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"],#DROP
                                saved_minimum_credits_selection=render_info["saved_minimum_credits_selection"],
                                gen_ed_credits_still_needed=render_info['gen_ed_credits_still_needed'],
                                full_schedule_generation=render_info['full_schedule_generation'],
                                minimum_summer_credits=render_info['minimum_summer_credits'],
                                first_semester = render_info['first_semester'],
                                semester_years = render_info['semester_years'],
                                semester_years_display = render_info["semester_years_display"],
                                course_prereqs_for = render_info['course_prereqs_for'],
                                user_name = render_info['user_name'],
                                ge_taken = render_info['ge_taken'],
                                fe_taken = render_info['fe_taken'],
                                degree_choice = render_info['degree_choice'],
                                is_graduated = render_info['is_graduated'],
                                required_courses_tuple = render_info['required_courses_tuple'],
                                required_courses_tuple_display = render_info["required_courses_tuple_display"],
                                total_elective_credits = render_info["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"],
                                render_info=json.dumps(render_info),
            )
        except Exception as e:
            print(e)
            render_template('errors/500.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'txt'

def get_render_info_from_upload(request):
    # check if the post request has the file part
    if 'file' not in request.files:
        print('No file part')
        render_template('errors/500.html')
    file = request.files['file']
    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        print('No selected file')
        render_template('errors/500.html')
    if file and allowed_file(file.filename):
        file_content = file.read().decode()
        return json.loads(file_content)