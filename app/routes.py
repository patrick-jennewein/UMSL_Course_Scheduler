from flask import render_template, request, json
from app import app
from app.middleware.course_parsing import parse_courses, generate_semester

@app.route('/')
@app.route('/index')
def index():
    semesters = ["Fall", "Spring"]
    certificates = [("None", ""), ("Artificial Intelligence", "AICERTReq"), ("Cybersecurity", "CYBERCERTReq"), ("Data Science", "DATACERTReq"), ("Mobile Apps and Computing", "MOBILECERTReq"), ("Internet and Web", "WEBCERTReq")]
    #num_3000_replaced_by_cert_core=0
    #cert_elective_courses_still_needed=0
    # create dictionaries for each course type
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
    # sort required courses by course number
    all_courses_list = sorted(all_courses_list, key=lambda d: d["course"])

    return render_template('index.html',
                           initial_load=True,
                           required_courses=all_courses_list,
                           required_courses_dict=json.dumps(all_courses),
                           json_required_courses=json.dumps(all_courses_list),
                           semesters=semesters,
                           certificates=certificates,
                           num_3000_replaced_by_cert_core=0,
                           cert_elective_courses_still_needed=0,
                           total_credits=0,
                           course_schedule=json.dumps([]),
                           include_summer=False,
                           semester_number=0,
                           minimum_semester_credits=list(map(lambda x: x, range(3, 22))), # create list for minimum credits dropdown
                           min_3000_course=5,
                           starting_credits=list(map(lambda x: x, range(0, 201))), # create list for minimum credits dropdown
                           core_credit_count = 0,
                           gen_ed_credits_still_needed=27,
                           minimum_summer_credits = list(map(lambda x: x, range(0, 13))),
                           semester_years = json.dumps({}),
                           user_name = "Student",
                           ge_taken = 0,
                           fe_taken = 0,
                           is_graduated = False,
                           required_courses_tuple = json.dumps([]),
                           certificate_choice = json.dumps([])
    )

@app.route('/schedule', methods=["POST"])
def schedule_generator():
    if "Print" in request.form.keys():
        course_schedule_display = json.loads(request.form["course_schedule"])
        total_credits = int(request.form["total_credits"])
        num_3000_replaced_by_cert_core = int(request.form["num_3000_replaced_by_cert_core"])
        min_3000_course = int(request.form["min_3000_course"])
        cert_elective_courses_still_needed = int(request.form["cert_elective_courses_still_needed"])
        ge_taken = 27 - int(request.form["gen_ed_credits_still_needed"])
        fe_taken = int(request.form["fe_taken"])
        c = json.loads(request.form["certificate_choice"])
        user_name = request.form["user_name"]
        certificate = c[0]
        total_elective_credits = int(request.form["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"])
        return render_template('printable.html',
                            course_schedule_display=course_schedule_display,
                            total_credits = total_credits,
                           num_3000_replaced_by_cert_core = num_3000_replaced_by_cert_core,
                           min_3000_course = min_3000_course,
                           cert_elective_courses_still_needed = cert_elective_courses_still_needed,
                           ge_taken = ge_taken,
                           fe_taken = fe_taken,
                           certificate = certificate,
                           total_elective_credits = total_elective_credits,
                           user_name = user_name)
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
                            min_3000_course=render_info["min_3000_course"],
                            include_summer=render_info["include_summer"],
                            certificates=render_info["certificate_choice"],
                            certificates_display = render_info["certificates_display"],
                            num_3000_replaced_by_cert_core=render_info["num_3000_replaced_by_cert_core"],
                            cert_elective_courses_still_needed=render_info["cert_elective_courses_still_needed"],
                            TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES=render_info["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"],
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
                            is_graduated = render_info['is_graduated'],
                            required_courses_tuple = render_info['required_courses_tuple'],
                            required_courses_tuple_display = render_info["required_courses_tuple_display"],
                            total_elective_credits = render_info["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"]
    )
