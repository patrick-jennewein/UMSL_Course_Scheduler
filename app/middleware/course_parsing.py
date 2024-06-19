import xmltodict
import json
from collections.abc import Mapping
from typing import Union, Any
import math
import datetime
from itertools import chain
import os
import copy


def print_dictionary(course_dictionary: dict) -> None:
    """
    prints a dictionary in readable format.

    Parameters
    ----------
    course_dictionary:      dict
                            holds the information for the courses
    Returns
    ----------
    None
    """
    print(json.dumps(course_dictionary, indent=4))


def build_prerequisites(course: dict) -> list:
    """
    creates the list of pre-requisites for a given course.

    Parameters
    ----------
    course:     dict
                holds all information about a particular course, including
                `subject`, `course_number`, etc. (the keys of the dictionary).
    Returns
    ----------
    list
                this will hold either:
                - a single list of courses that are pre-requisites
                - a lists of lists: i.e. multiple lists of possible pre-requisites within a list.
    """
    # creates an empty list to hold any potential pre-requisites
    prereqs_list = []

    # determines if the course has a pre-requisite
    if ('prerequisite' in course.keys()):
        prereqs = course['prerequisite']['or_choice']

        # prerequisite is a dictionary (i.e. one pre-requisite exists)
        if isinstance(prereqs, Mapping):
            prereq = prereqs['and_required']
            if isinstance(prereq, list):
                prereqs_list.append([prereq])
            else:
                prereqs_list.append(prereq)

        # prerequisite is a list of dictionaries (i.e. multiple pre-requisites exist)
        else:
            for prereq in prereqs:
                # Checks if the prerequisite is an array or a comp sci/math class prerequisite
                prereq = prereq['and_required']
                if isinstance(prereq, list):
                    prereqs_list.append(prereq)
                elif (prereq.startswith('CMP SCI') or prereq.startswith('MATH')):
                    prereqs_list.append([prereq])
                elif ("ALEKS" in prereq):
                    prereqs_list.append(["ALEKS"])

    # flatten lists of >1 length to keep consistency
    if len(prereqs_list) == 1 and isinstance(prereqs_list[0], list):
        prereqs_list = prereqs_list[0]

    # return a list of pre-requisites
    return prereqs_list


def build_dictionary(courses: Union[dict, list]) -> dict:
    """
    Builds a dictionary with the information for each course included in a course type.

    Course type includes "core courses," "elective courses," etc.

    Parameters
    ----------
    courses:    dict or list
                holds the information for all courses of a certain type (core,
                electives, etc.).

                This parameter is a list of dictionaries if there are multiple courses of a certain type.
                In each dictionary, each key is the XML tag, i.e. `subject`, `course_number`, etc.
                with the corresponding value.

                This parameter is a single dictionary if there is only one course of that type.
                In the dictionary, each key is the XML tag, i.e. `subject`, `course_number`, etc.
                with the corresponding value.

    Returns
    ----------
    dict
                The finalized dictionary of the course type.
                Each key is the course subject and course number.
                The corresponding value is a dictionary holding all the information about that course.
    """

    # create empty dict to store course information
    updated_course_dict = {}

    # Checks if 'courses' is a dictionary
    if isinstance(courses, Mapping):
        courses = [courses]
    for course in courses:
        # add pre-requisites to dictionary
        course['prerequisite'] = build_prerequisites(course)

        key = course["subject"] + " " + course["course_number"]

        # add rest of information to dictionary
        course_dict = {
            key: course
        }
        if 'prerequisite_description' in course:
            pass

        # add list of semesters offered to dictionary
        course["semesters_offered"] = []
        if isinstance(course['rotation_term'], list):
            for term in course['rotation_term']:
                course["semesters_offered"].append(term['term'])
        else:
            course["semesters_offered"] = course['rotation_term']['term']

        if 'prerequisite_description' in course:
            course['prerequisite_description'] = course['prerequisite_description']
        # make final update to course dictionary
        updated_course_dict.update(course_dict)

    # return dictionary with finalized course type dictionary
    return updated_course_dict


def parse_courses() -> dict:
    """
    Parses relevant information from XML and return dictionaries.

    This function opens up the XML file, calls the build_dictionary function
    and returns the dictionary based upon the two parameters provided to
    the function.

    csbs_req is a dictionary that represents a section of parsed XML data. It
    holds each course type as a key and each value for the key is either:
        - a list(if only one course for that key exists) or
        - a dictionary (if multiple courses for that key exist)

    Returns
    ----------
    dict
                    The dictionary that holds all course information
    """
    # open xml document to begin parsing
    root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(root, 'xml/course_data.xml')) as fd:
        doc = xmltodict.parse(fd.read())

    # create a dictionary with course information to further parse
    csbs_req = doc["CSBSReq"]

    all_courses = build_dictionary(csbs_req["Electives"]["course"])
    all_courses.update(build_dictionary(csbs_req["OtherCourses"]["course"]))
    all_courses.update(build_dictionary(csbs_req["MathandStatistics"]["course"]))
    all_courses.update(build_dictionary(csbs_req["CoreCourses"]["course"]))

    # return finalized dictionary of the course type
    return all_courses

def parse_certificate(certificate_name) -> dict:
    """
    Parses relevant information from XML and return dictionaries.

    cscertificate_data.xml is a document that contains all course data for certificates in the computer science program.

    Params
    ----------
    certificate_name        string
                            is the name of the desired certificate. May have any of the following values:
                            AICERTReq
                            CYBERCERTReq
                            DATACERTReq
                            MOBILECERTReq
                            WEBCERTReq

    Returns
    ----------
    dict

    """
    # open xml document to begin parsing
    root = os.path.dirname(os.path.dirname(__file__))
    with open(os.path.join(root, 'xml/cscertificate_data.xml')) as fd:
        doc = xmltodict.parse(fd.read())

    # create a dictionary with course information to further parse
    certificate_data = doc["CSCertificates"]

    core_courses = build_dictionary(certificate_data[certificate_name]["CertCore"]["course"])
    elective_courses = build_dictionary(certificate_data[certificate_name]["CertElectives"]["course"])
    electives_needed = int(certificate_data[certificate_name]["NoOfElectives"]["num"])

    # return finalized dictionary of the course type
    return core_courses, elective_courses, electives_needed


def add_course(current_semester, course_info, current_semester_classes, course, courses_taken,
               total_credits_accumulated, current_semester_credits, course_category):
    # Add course, credits to current semester and list of courses taken, credits earned
    course_added = False
    if current_semester in course_info['semesters_offered']:
        current_semester_classes.append({
            'course': course,
            'name': course_info['course_name'],
            'description': course_info['course_description'],
            'credits': course_info['credit'],
            'category': course_category,
            'prerequisite_description': course_info['prerequisite_description'] if 'prerequisite_description' in course_info.keys() else '',
            'passed_validation': True
        })
        courses_taken.append(course)
        total_credits_accumulated = total_credits_accumulated + int(course_info['credit'])
        current_semester_credits = current_semester_credits + int(course_info['credit'])
        course_added = True
    return course_added, current_semester_classes, courses_taken, total_credits_accumulated, current_semester_credits


def build_semester_list(first_season="Fall", include_summer=True) -> list:
    possible_semesters = ["Fall", "Spring", "Summer"]

    # Reorder the seasons based on the user's preference for the first season
    first_index = possible_semesters.index(first_season)
    possible_seasons = possible_semesters[first_index:] + possible_semesters[:first_index]

    # Filter out seasons based on user preferences
    selected_semesters = []
    selected_semesters.append("Fall")
    selected_semesters.append("Spring")
    if include_summer:
        selected_semesters.append("Summer")

    if first_season not in selected_semesters:
        return ValueError("First season is not in selected seasons")
    if "Fall" not in selected_semesters or "Spring" not in selected_semesters:
        return ValueError("Fall or Spring must be selected")
    return [season for season in possible_seasons if season in selected_semesters]


def add_gen_ed_elective() -> dict:
    gen_ed_info = {
        'course': "GEN ED",
        'name': '[User Selects]',
        'description': '',
        'credits': 3,
        'category': "General Education",
        'passed_validation': True
    }
    return gen_ed_info


def add_free_elective() -> dict:
    free_elective_info = {
        'course': "FREE",
        'name': '[User Selects]',
        'description': '',
        'credits': 3,
        'category': 'Free Elective',
        'passed_validation': True
    }
    return free_elective_info

def print_course_list_information(certificate_core, cert_elective_courses_still_needed,
                                  certificate_electives, min_3000_course_still_needed,
                                  required_courses_tuple):
    print("Certificate Core (Necessary): ")
    for item in certificate_core.keys():
        print(f"{'':<40}{item}")
    print(f"Certificate Electives (Pick {cert_elective_courses_still_needed}): ")
    for item in certificate_electives.keys():
        print(f"{'':<40}{item}")
    print(f"{'3000+ Level Electives Still Needed:':<40}{min_3000_course_still_needed}")
    print("Required Course List:")
    for item in required_courses_tuple:
        if item in certificate_core.keys() and item[0] not in required_courses_tuple:
            print(f"\t{item} ***(Core of Certificate, Now Required)")
        elif item in certificate_electives.keys():
            print(f"\t{item} ***(Elective of Certificate)")
        else:
            print(f"\t{item}")


def graduation_check(total_credits_accumulated, required_courses_tuple, courses_taken,
                   min_3000_course_still_needed, cert_elective_courses_still_needed, gen_ed_credits_still_needed) -> bool:

    # assume that course generation is complete
    is_course_generation_complete = True

    # check that all required core (BSCS and certificate) has been taken
    error_messages = []
    for course in required_courses_tuple:
        if course not in courses_taken:
            error_messages.append(f"ERROR: Must take {course}")
            is_course_generation_complete = False
            break # leave 'for' loop if a course still needs to be taken

    # check all required electives have been taken
    # print(f"{'CMP SCI 3000+ courses needed:':<30}{min_3000_course_still_needed:}")
    if is_course_generation_complete and min_3000_course_still_needed != 0:
        is_course_generation_complete = False
        error_messages.append(f"ERROR: Must take {min_3000_course_still_needed} more 3000+ level electives.")

    # check that all certificates have been taken
    # print(f"{'Certificate courses needed:':<30}{cert_elective_courses_still_needed:}")
    if is_course_generation_complete and cert_elective_courses_still_needed != 0:
        is_course_generation_complete = False
        error_messages.append(f"ERROR: Must take {cert_elective_courses_still_needed} more certificate electives.")

     # check that all gen eds have been taken
    # print(f"{'Gen Ed courses needed:':<30}{gen_ed_credits_still_needed:}")
    if is_course_generation_complete and gen_ed_credits_still_needed != 0:
        is_course_generation_complete = False
        error_messages.append(f"ERROR: Must take {gen_ed_credits_still_needed} more general education electives.")

    # check credit hours
    # print(f"{'Total credits accumulated:':<30}{total_credits_accumulated:}/{120}")
    if is_course_generation_complete and total_credits_accumulated < 120:
        is_course_generation_complete = False
        error_messages.append(f"ERROR: Must have 120 credit hours completed. Only {total_credits_accumulated} completed.")

    # if is_course_generation_complete == False:
    #     print(error_messages)

    # check if ultimately finished
    return is_course_generation_complete

def update_semester(current_semester, include_summer) -> str:
    if current_semester == "Fall":
        return "Spring"
    elif current_semester == "Spring":
        if include_summer:
            return "Summer"
        else:
            return "Fall"
    else:
        return "Fall"
    
def initial_prerequisite_check(required_courses_dict, course, courses_taken, courses_for_graduation) -> bool:
    required_courses_taken = True
    for prereqs in required_courses_dict[course]["prerequisite"]:
        required_courses_taken = False
        if isinstance(prereqs, str):
            if ((prereqs in courses_taken) or (prereqs in courses_for_graduation)):
                required_courses_taken = True
                break
        elif (len(prereqs) == 1):
            if ((prereqs[0] in courses_taken) or (prereqs[0] in courses_for_graduation)):
                required_courses_taken = True
                break
        else:
            for prereq in prereqs:
                if ((prereq in courses_taken) or (prereq in courses_for_graduation)):
                    required_courses_taken = True
                else:
                    required_courses_taken = False
                # if there's one failure in the list of required courses then stop looping
                if not required_courses_taken:
                    break
            # if all the courses in the prerequisite list have been taken, so we don't need to check other prerequisites
            if required_courses_taken:
                break
    return not required_courses_taken

def get_semester_years(selected_season) -> dict:
    # calculate user's current time and season
    seasons_from_month = {
        1: 'Spring',
        2: 'Spring',
        3: 'Spring',
        4: 'Spring',
        5: 'Spring',
        6: 'Summer',
        7: 'Summer',
        8: 'Fall',
        9: 'Fall',
        10: 'Fall',
        11: 'Fall',
        12: 'Fall'
    }
    first_month_of_seasons = {
        'Spring': 1,
        'Summer': 6,
        'Fall': 8
    }
    current_date = datetime.datetime.now()
    current_month = int(current_date.month)
    current_year = int(current_date.year)
    current_season = seasons_from_month[current_month]
    semester_years = {}

    # planning for Spring
    if(selected_season == 'Spring'):
        # if in first month of Spring, plan for this Spring
        if (current_month <= first_month_of_seasons[selected_season]):
            semester_years = {
                'Spring': current_year,
                'Summer': current_year,
                'Fall': current_year
            }
        # if NOT in first month of Spring, plan for next Spring
        else:
            semester_years = {
                'Spring': current_year + 1,
                'Summer': current_year + 1,
                'Fall': current_year + 1
            }

    # planning for Fall
    elif(selected_season == 'Fall'):
        # if in first month of Fall, plan for this Fall
        if (current_month <= first_month_of_seasons[selected_season]):
            semester_years = {
                'Spring': current_year + 1,
                'Summer': current_year + 1,
                'Fall': current_year
            }
        # if NOT in first month of Fall, plan for next Fall
        elif (current_month > first_month_of_seasons[selected_season]):
            semester_years = {
                'Spring': current_year + 2,
                'Summer': current_year + 2,
                'Fall': current_year + 1
            }

    elif(selected_season == 'Summer'):
        # if in first month of Summmer, plan for this Summer
        if (current_month <= first_month_of_seasons[selected_season]):
            semester_years = {
                'Spring': current_year + 1,
                'Summer': current_year,
                'Fall': current_year
            }
        # if NOT in first month of Fall, plan for next Fall
        elif (current_month > first_month_of_seasons[selected_season]):
            semester_years = {
                'Spring': current_year + 2,
                'Summer': current_year + 1,
                'Fall': current_year + 1
            }
    print()
    return semester_years


def generate_semester(request): # -> dict[Union[str, Any], Union[Union[str, list, int, list[Any], None], Any]]:
    # get information from user form, routes.py
    course_schedule = json.loads(request.form["course_schedule"])
    current_semester = request.form["current_semester"]
    semester = int(request.form["semester_number"])
    generate_complete_schedule = True if "generate_complete_schedule" in request.form.keys() else False
    num_3000_replaced_by_cert_core = int(request.form["num_3000_replaced_by_cert_core"])  # default is 0
    first_semester = request.form["first_semester"]
    semester_years = json.loads(request.form["semester_years"])
    user_name = request.form["user_name"]


    # credit hour trackers
    ge_taken = int(request.form["ge_taken"])
    free_elective_credits_accumulated = int(request.form["fe_taken"])
    gen_ed_credits_still_needed = int(request.form["gen_ed_credits_still_needed"]) - ge_taken if semester == 0 else int(request.form["gen_ed_credits_still_needed"])
    cert_elective_courses_still_needed = int(request.form["cert_elective_courses_still_needed"])  # default is 0
    min_3000_course_still_needed = int(request.form["min_3000_course"]) # default is 5
    total_credits_accumulated = int(request.form["total_credits"]) if semester != 0 else int(request.form["total_credits"]) + ge_taken + free_elective_credits_accumulated

    # print out student information
    # print(f"{'Student:':<40}{user_name}")
    # print(f"{'General Education Credits Earned:':<40}{27 - gen_ed_credits_still_needed}")
    # print(f"{'Free Elective Credits Earned:':<40}{free_elective_credits_accumulated}")
    # print(f"{'Total Credits Incoming:':<40}{total_credits_accumulated}")

    # set up default variables (also used for counter on scheduling page)
    TOTAL_CREDITS_FOR_GRADUATION = 120
    TOTAL_CREDITS_FOR_BSCS = 71
    TOTAL_CREDITS_FOR_BSCS_ELECTIVES = 15
    TOTAL_CREDITS_FOR_GEN_EDS = 27
    TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES = 0 # set in first semester and maintained by request.form in subsequent semesters
    DEFAULT_CREDIT_HOURS = 3
    course_categories = {
        'R': 'BSCS',
        'E': 'BSCS',
        'C': 'BSCS',
        'G': 'General Education',
        'F': 'Free Elective',
        'O': 'Other'
    }

    # user enters credits for upcoming semester
    min_credits_per_semester = int(request.form["minimum_semester_credits"])
    summer_credit_count = int(request.form["minimum_summer_credits"])
    temp_min_credits_per_semester = None

    # set up scheduler variables, overwritten below
    include_summer = False
    courses_taken = []
    waived_courses = None
    required_courses_dict_list = []
    has_passed_math_placement_exam = False
    is_graduated = False

    # set up certificate variables
    # certificate_option = False
    certificate_core = {}
    certificate_electives = {}
    certificate_choice_xml_tag = ""
    certificate_choice_name = ""

    course_prereqs_for = None


    # if the first semester, overwrite schedular variables from above
    if semester == 0:
        temp_min_credits_per_semester = min_credits_per_semester
        first_semester = request.form["current_semester"]

        if (first_semester == "Summer"):
            min_credits_per_semester = summer_credit_count

        semester_years = get_semester_years(first_semester)
        if "include_summer" in request.form.keys():
            include_summer = True if request.form["include_summer"] == "on" else False

        if ("courses_taken" in request.form.keys()):
            courses_taken = request.form.getlist("courses_taken")

        if ("aleks_check" in request.form.keys()):
            has_passed_math_placement_exam = True

        # Do we need separate selects for waived/taken courses or should we combine them to one?
        # If they say taken, do we need to add the credits to the total accumulated credits?
        # ensure waived courses cannot be added when building a semester and remove any duplicates
        if ("waived_courses" in request.form.keys()):
            courses_taken.extend(request.form.getlist("waived_courses"))
            courses_taken = list(dict.fromkeys(courses_taken))

        # if user elects to complete a certificate, get course data for that certificate and decrease electives accordingly
        certificate_choice = request.form["certificate_choice"].split(",")
        certificate_choice_name = certificate_choice[0]
        certificate_choice_xml_tag = certificate_choice[1]

        if (certificate_choice_xml_tag != ""):
            certificate_core, certificate_electives, cert_elective_courses_still_needed = parse_certificate(certificate_choice_xml_tag)

            # Update counters according to certificate addition
            min_3000_course_still_needed -= cert_elective_courses_still_needed
            TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES = cert_elective_courses_still_needed * DEFAULT_CREDIT_HOURS
            #certificate_option = True

        # determine the semesters that user will be enrolled in
        user_semesters = build_semester_list(current_semester, include_summer)

        # generate required courses
        all_courses_dict = json.loads(request.form['required_courses_dict'])

        # if a certificate was selected, add the required certificate courses to required courses and update counters
        if certificate_core:
            num_courses_in_base_csdeg = len(all_courses_dict)
            all_courses_dict.update(certificate_core)
            num_3000_replaced_by_cert_core = len(all_courses_dict) - num_courses_in_base_csdeg
            # print(f"{'3000+ Electives Used in Certificate':<40}{num_3000_replaced_by_cert_core}")

            # update counters according to certificate selection
            min_3000_course_still_needed -= num_3000_replaced_by_cert_core

        ############################################################################
        ### Note to self: after 'if' statements of course rules, loop through list to build course dictionary
        # filter out all non-required courses and then return a just the course numbers as a list and convert that list to a tuple
        courses_for_graduation = sorted(({k:v for (k,v) in all_courses_dict.items() if "required" in v.keys() and v['required'] == 'true'}).keys())
        required_courses_tuple = tuple(copy.deepcopy(courses_for_graduation))

        print(f"{courses_for_graduation=}")

        for course in required_courses_tuple:
            should_add_prereqs = initial_prerequisite_check(all_courses_dict, course, courses_taken, courses_for_graduation)
            temp_courses_to_add = []
            if should_add_prereqs:
                print(f"{course=}")
                for prereqs in all_courses_dict[course]["prerequisite"]:
                    required_courses_taken = False
                    if isinstance(prereqs, str):
                        if (prereqs not in courses_for_graduation) and (prereqs not in courses_taken):
                            courses_for_graduation.append(prereqs)
                            print(f'Missing course: {prereqs}')
                            break
                    elif (len(prereqs) == 1):
                        if (prereqs[0] not in courses_for_graduation) and (prereqs[0] not in courses_taken):
                            courses_for_graduation.append(prereqs[0])
                            print(f'Missing course: {prereqs[0]}')
                            break
                    else:
                        # Potential improvement: Decide a better way to add prerequisites instead of just taking first pre
                        for prereq in prereqs:
                            if (prereq not in all_courses_dict.keys()):
                                temp_courses_to_add = []
                                break
                            if ((prereq not in courses_for_graduation) and (prereq not in courses_taken)):
                                temp_courses_to_add.append(prereq)
                        if (len(temp_courses_to_add) > 0):
                            courses_for_graduation.extend(temp_courses_to_add)
                            break
        ############################################################################

        # remove University course - INTDSC 1003 - if user has required credits
        if total_credits_accumulated >= 24:
            courses_for_graduation.remove('INTDSC 1003') 
        ## Handle MATH 1045 checks first because it's an unnecessary course if MATH 1030 and MATH 1035 exist
        if ('MATH 1045' in courses_taken) and (('MATH 1030' not in courses_taken) or ('MATH 1035' not in courses_taken)):
            if "MATH 1030" in courses_for_graduation:
                courses_for_graduation.remove('MATH 1030')
            if "MATH 1035" in courses_for_graduation:
                courses_for_graduation.remove('MATH 1035')
        # MATH 1045 is redundant if MATH 1030 and MATH 1035 are going to be courses used
        if ('MATH 1045' not in courses_taken) and ('MATH 1030' in courses_for_graduation) and ('MATH 1035' in courses_for_graduation) and ("MATH 1045" in courses_for_graduation):
            courses_for_graduation.remove('MATH 1045')
        ## Remove optional courses if they are no longer required due to courses already taken
        if ('ENGLISH 3130' in courses_taken) and ('ENGLISH 1100' not in courses_taken) and ('ENGLISH 1100' in courses_for_graduation):
            courses_for_graduation.remove('ENGLISH 1100')
        if ('MATH 1800' in courses_taken):
            if ('MATH 1320' in courses_taken) and ('MATH 1030' not in courses_taken) and ("MATH 1030" in courses_for_graduation):
                courses_for_graduation.remove('MATH 1030')
            if ("MATH 1035" in courses_for_graduation) and ('MATH 1035' not in courses_taken) and ("MATH 1035" in courses_for_graduation):
                courses_for_graduation.remove('MATH 1035')
        # MATH 1100 is only required for CMP SCI 4732
        if ('CMP SCI 4732' not in courses_for_graduation) and ('MATH 1100' not in courses_taken) and ("MATH 1100" in courses_for_graduation):
            courses_for_graduation.remove('MATH 1100')
        if has_passed_math_placement_exam:
            if ('MATH 1320' in courses_taken) and ('MATH 1030' not in courses_taken) and ("MATH 1030" in courses_for_graduation):
                courses_for_graduation.remove('MATH 1030')
            if "MATH 1035" in courses_for_graduation:
                courses_for_graduation.remove('MATH 1035')
            if "MATH 1045" in courses_for_graduation:
                courses_for_graduation.remove('MATH 1045')
            courses_taken.append("ALEKS")
        
        for course in courses_taken:
            if course in courses_for_graduation:
                courses_for_graduation.remove(course)

        required_courses_dict = {}
        for course in courses_for_graduation:
            course_dict = {
                course: all_courses_dict[course]
            }
            required_courses_dict.update(course_dict)
        
        # convert required courses dictionary to list for easier processing
        required_courses_dict_list = sorted(list(required_courses_dict.items()), key=lambda d: d[1]["course_number"])
        courses_dict_list_unchanged = copy.deepcopy(required_courses_dict_list)

        prereqs_for_dict = {}

        for course_data in required_courses_dict.items():
            prereq_for_list = []
            key = course_data[0]
            course = course_data[1]
            for prereq in course['prerequisite']:
                if isinstance(prereq, str):
                    prereq_for_list.append(prereq)
                else:
                    prereq_for_list.extend(list(chain.from_iterable(course['prerequisite'])))
            prereq_for_list = list(set(prereq_for_list))

            for prereq in prereq_for_list:
                if prereq not in prereqs_for_dict.keys():
                    prereqs_for_dict[prereq] = [key]
                else:
                    prereqs_for_dict[prereq].append(key)

        course_prereqs_for = prereqs_for_dict

        # print information for certificates and proposed course schedule, update tuple
        # print_course_list_information(certificate_core, cert_elective_courses_still_needed, certificate_electives,
                                      # min_3000_course_still_needed, required_courses_tuple)

    # if NOT the first semester
    elif semester != 0:
        required_courses_dict_list = json.loads(request.form['required_courses_dict_list'])
        courses_dict_list_unchanged = json.loads(request.form['required_courses_dict_list_unchanged'])
        course_prereqs_for = json.loads(request.form["course_prereqs_for"])
        user_semesters = request.form["semesters"]
        include_summer = True if request.form["include_summer"] == "True" else False
        temp_min_credits_per_semester = int(request.form["saved_minimum_credits_selection"])
        is_graduated = True if request.form["is_graduated"] == "True" else False

        certificate_choice = json.loads(request.form["certificate_choice"])
        certificate_choice_name = certificate_choice[0]
        certificate_choice_xml_tag = certificate_choice[1]
        TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES = int(request.form["TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES"])

        if ("courses_taken" in request.form.keys()):
            courses_taken = json.loads(request.form["courses_taken"])

        required_courses_tuple = json.loads(request.form["required_courses_tuple"])

    # adjust credit parameters for scheduling
    credits_for_3000_level = 60  # 3000+ level credits will not be taken before this many credits earned

    # start with a blank semester
    current_semester_credits = 0
    current_semester_classes = []
    current_semester_cs_math_credits_per_semester = 0
    current_CS_elective_credits_per_semester = 0
    is_course_generation_complete = False

    # create header for console
    # if(generate_complete_schedule):
    #     print(f"{'Min credits Fall/Spring:':<40} {min_credits_per_semester}")
    #     print(f"{'Min credits for summer:':<40} {summer_credit_count}\n\n")
    # elif(not generate_complete_schedule):
    #     print(f"Minimum credits for upcoming semester: {min_credits_per_semester}\n\n")
    # print(f"Status:\t{'Num:':<15}{'Course Name:':<40} "
    #       f"{'Cr of Min:':<5}"
    #       f"{'Total':>15}/{TOTAL_CREDITS_FOR_GRADUATION}:")
    


    if not is_graduated:
        # loop through to generate a semester or a whole schedule
        while (not is_course_generation_complete):
            course_added = False

            # adjust credit ratios for scheduling
            max_core_credits_per_semester = math.ceil(min_credits_per_semester * 2/3)
            max_CS_math_total_credits = min_credits_per_semester - 3
            max_CS_elective_credits_per_semester = 6

            # first, attempt to add a required course
            for index, x in enumerate(required_courses_dict_list):
                course: str = x[0]  # holds course subject + number
                course_info: dict = x[1]  # holds all other information about course
                concurrent = None
                if "concurrent" in course_info.keys():
                    concurrent = course_info["concurrent"]

                # add course to schedule if not already added AND current semester doesn't have too many core credits
                if (course not in courses_taken and current_semester_credits < max_core_credits_per_semester):

                    # if the course has no pre-requisites
                    if len(course_info["prerequisite"]) == 0:
                        course_added, current_semester_classes, courses_taken, total_credits_accumulated, current_semester_credits \
                            = add_course(
                            current_semester, course_info, current_semester_classes, course, courses_taken,
                            total_credits_accumulated, current_semester_credits, course_categories['R'])

                    # if the course has at least one pre-requisite
                    else:
                        # look up list of pre-requisites for current course
                        course_added = False
                        prereqs = course_info["prerequisite"]

                        # iterate through pre-requisites for the current course
                        required_courses_taken = False
                        for prereqs in course_info["prerequisite"]:
                            # if there is only one pre-requisite (a string)
                            if isinstance(prereqs, str):
                                # ENGLISH 3130 has a special prerequisite of at least 48 credit hours before the class can be taken
                                if (course == "ENGLISH 3130"):
                                    if (total_credits_accumulated >= 48) and (prereqs in courses_taken):
                                        course_added, current_semester_classes, courses_taken, total_credits_accumulated, current_semester_credits \
                                            = add_course(
                                            current_semester, course_info, current_semester_classes, course, courses_taken,
                                            total_credits_accumulated, current_semester_credits, course_categories['R']
                                        )
                                        break

                                # add the current course because pre-requisite has already been taken
                                elif (prereqs in courses_taken) and (
                                        # `not any(current...)` verifies the prereq is not in the current semester class list of dictionaries
                                        (not any(current['course'] == prereqs for current in current_semester_classes)) or (prereqs == concurrent)):
                                    required_courses_taken = True
                                else:
                                    required_courses_taken = False

                            # if there is a list of pre-requisites
                            else:
                                # if there is only one pre-requisite
                                if (len(prereqs) == 1):

                                    # add the current course because pre-requisite has already been taken
                                    if (prereqs[0] in courses_taken) and (
                                            (not any(current['course'] == prereqs[0] for current in current_semester_classes))
                                            or (prereqs[0] == concurrent)):
                                        course_added, current_semester_classes, courses_taken, total_credits_accumulated, current_semester_credits = add_course(
                                            current_semester, course_info, current_semester_classes, course, courses_taken,
                                            total_credits_accumulated, current_semester_credits, course_categories['R']
                                        )
                                        break

                                # if there is >1 pre-requisite
                                else:
                                    # iterate through each pre-requisite
                                    for prereq in prereqs:
                                        if (prereq in courses_taken) and (
                                                # `not any(current...)` verifies the prereq is not in the current semester class list of dictionaries
                                                (not any(current['course'] == prereq for current in current_semester_classes)) or (prereq == concurrent)):
                                            required_courses_taken = True
                                        else:
                                            required_courses_taken = False
                                        if not required_courses_taken:
                                            break

                                    # add the current course because pre-requisite has already been taken
                                    if required_courses_taken:
                                        course_added, current_semester_classes, courses_taken, total_credits_accumulated, current_semester_credits = add_course(
                                            current_semester, course_info, current_semester_classes, course, courses_taken,
                                            total_credits_accumulated, current_semester_credits, course_categories['R']
                                        )
                                        required_courses_taken = False
                                        break
                        if required_courses_taken:
                            course_added, current_semester_classes, courses_taken, total_credits_accumulated, current_semester_credits = add_course(
                                current_semester, course_info, current_semester_classes, course, courses_taken,
                                total_credits_accumulated, current_semester_credits, course_categories['R']
                            )

                    # if the course was added, update semester info
                    if course_added:
                        current_semester_cs_math_credits_per_semester += int(course_info['credit'])
                        # print(f"Added: \t{course:<15}{course_info['course_name'][:40]:<40} "
                        #     f"{current_semester_credits:<2} of {min_credits_per_semester:<2}"
                        #     f"{total_credits_accumulated:>15}")
                        
                        is_graduated = graduation_check(
                                total_credits_accumulated, required_courses_tuple,
                                courses_taken, min_3000_course_still_needed,
                                cert_elective_courses_still_needed, gen_ed_credits_still_needed)

                        # if current semester is fully generated or generating the whole schedule and has graduated, then stop generation
                        if (current_semester_credits >= min_credits_per_semester) or (generate_complete_schedule and is_graduated):
                            current_semester_info = {
                                'semester': current_semester,
                                'semester_number': semester,
                                'credits': current_semester_credits,
                                'schedule': current_semester_classes,
                                'year': semester_years[current_semester]
                            }
                            course_schedule.append(current_semester_info)

                            # if only generating a semester stop here
                            if not generate_complete_schedule:
                                is_course_generation_complete = True

                            # reset semester info
                            current_semester_credits = 0
                            current_semester_classes = []
                            semester += 1
                            current_semester_cs_math_credits_per_semester = 0
                            current_CS_elective_credits_per_semester = 0
                            current_semester = update_semester(current_semester, include_summer)

                            if is_graduated and generate_complete_schedule:
                                is_course_generation_complete = True
                                break
                            else:
                                if(current_semester == first_semester):
                                    semester_years = {key: value + 1 for key, value in semester_years.items()}
                                    # print(f"\nNext Semester, {current_semester} {semester_years[current_semester]}")
                                # ensure summer credit hours are not F/Sp credit hours
                                if (current_semester == "Summer" and generate_complete_schedule):
                                    min_credits_per_semester = summer_credit_count
                                elif (current_semester != "Summer" and generate_complete_schedule):
                                    min_credits_per_semester = temp_min_credits_per_semester

                        required_courses_dict_list.pop(index)
                        break

            # second, if a required course was NOT added above, add some kind of elective
            if (not course_added):
                # if user CANNOT take 3000+ level class, due to needing more credit
                if total_credits_accumulated < credits_for_3000_level:
                    if gen_ed_credits_still_needed >= DEFAULT_CREDIT_HOURS:
                        current_semester_classes.append(add_gen_ed_elective())
                        gen_ed_credits_still_needed -= DEFAULT_CREDIT_HOURS
                        # print(f"Added: \t{'GEN ED':<15}{'[User Selects]':<40} "
                        #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                        #     f"{total_credits_accumulated + 3:>15}")
                    else:
                        current_semester_classes.append(add_free_elective())
                        free_elective_credits_accumulated += DEFAULT_CREDIT_HOURS
                        # print(f"Added: \t{'FREE ELEC':<15}{'[User Selects]':<40} "
                        #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                        #     f"{total_credits_accumulated + 3:>15}")
                # if user CAN take 3000+ level classes
                else:
                    # user elects for a certificate
                    if certificate_choice_xml_tag != "":
                        """
                        check to ensure enough room is in schedule for another CMP SCI class based on 4 conditions:
                            1. The amount of CMP SCI 3000 elective credit is less than pre-determined maximum
                            2. Total credit count of CS/MATH is less than pre-determined maximum 
                            3. There are still CMP SCI 3000 electives to take
                            4. There are still certificate electives to take

                        if all 4 four conditions fail, add a General Education elective or Free Elective
                        """
                        # condition 1 and 2
                        if (current_CS_elective_credits_per_semester <= (max_CS_elective_credits_per_semester - 3)) and \
                                (current_semester_cs_math_credits_per_semester <= (max_CS_math_total_credits - 3) or \
                                 (max_CS_math_total_credits - 3) <= 0):
                            # condition 3: if non-elective 3000-level courses are still needed, add these primarily
                            if min_3000_course_still_needed > 0:
                                current_semester_classes.append({
                                        'course': "CMP SCI 3000+",
                                        'name': '[User Selects]',
                                        'description': '',
                                        'credits': 3,
                                        'category': 'CS Elective',
                                        'passed_validation': True
                                    })

                                # increment current semester credits, decrement courses needed
                                current_semester_cs_math_credits_per_semester += DEFAULT_CREDIT_HOURS
                                current_CS_elective_credits_per_semester += DEFAULT_CREDIT_HOURS
                                min_3000_course_still_needed -= 1
                                # print(f"Added: \t{'COMP SCI 3000+':<15}{'[User Selects]':<40} "
                                #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                #     f"{total_credits_accumulated + 3:>15}")

                            # condition 4: if elective 3000-level courses are still needed, add these secondarily
                            elif cert_elective_courses_still_needed > 0:
                                current_semester_classes.append({
                                        'course': f"CMP SCI {certificate_choice_name} Elective",
                                        'name': '[User Selects]',
                                        'description': '',
                                        'credits': 3,
                                        'category': course_categories['C'],
                                        'passed_validation': True
                                    })

                                # increment current semester credits, decrement courses needed
                                current_semester_cs_math_credits_per_semester += DEFAULT_CREDIT_HOURS
                                current_CS_elective_credits_per_semester += DEFAULT_CREDIT_HOURS
                                cert_elective_courses_still_needed -= 1
                                # print(f"Added: \t{'CMP SCI CERT':<15}{'[User Selects]':<40} "
                                #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                #     f"{total_credits_accumulated + 3:>15}")

                            # all 4 conditions fail.
                            # add a general education elective
                            elif gen_ed_credits_still_needed > 0:
                                current_semester_classes.append(add_gen_ed_elective())
                                # print(f"Added: \t{'GEN ED':<15}{'[User Selects]':<40} "
                                #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                #     f"{total_credits_accumulated + 3:>15}")
                                gen_ed_credits_still_needed -= DEFAULT_CREDIT_HOURS
                            # add a free elective
                            else:
                                current_semester_classes.append(add_free_elective())
                                free_elective_credits_accumulated += DEFAULT_CREDIT_HOURS
                                # print(f"Added: \t{'FREE ELEC':<15}{'[User Selects]':<40} " 
                                #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}" 
                                #     f"{total_credits_accumulated + 3:>15}")

                        # if condition 1 or 2 fail, add a type of elective for balance
                        else:
                            if gen_ed_credits_still_needed > 0:
                                current_semester_classes.append(add_gen_ed_elective())
                                gen_ed_credits_still_needed -= DEFAULT_CREDIT_HOURS
                                # print(f"Added: \t{'GEN ED':<15}{'[User Selects]':<40} "
                                #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                #    f"{total_credits_accumulated + 3:>15}")
                            else:
                                current_semester_classes.append(add_free_elective())
                                free_elective_credits_accumulated += DEFAULT_CREDIT_HOURS
                                # print(f"Added: \t{'FREE ELEC':<15}{'[User Selects]':<40} "
                                #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                #     f"{total_credits_accumulated + 3:>15}")


                    # user does NOT elect for a certificate
                    elif certificate_choice_xml_tag == "":
                        """
                        check to ensure enough room is in schedule for another CMP SCI class based on 3 conditions:
                            1. There are still CMP SCI 3000 electives to take
                            2. The amount of CMP SCI 3000 elective credit is less than pre-determined maximum
                            3. Total credit count of CS/MATH is less than pre-determined maximum 
                        """
                        # condition 1, 2, and 3
                        if min_3000_course_still_needed > 0 and \
                                (current_CS_elective_credits_per_semester <= (max_CS_elective_credits_per_semester - 3)) and \
                                (current_semester_cs_math_credits_per_semester <= (max_CS_math_total_credits - 3) or \
                                 (max_CS_math_total_credits - 3) <= 0):
                            current_semester_classes.append({
                                'course': "CMP SCI 3000+",
                                'name': '[User Selects]',
                                'description': '',
                                'credits': 3,
                                'category': course_categories['E'],
                                'passed_validation': True
                            })
                            current_semester_cs_math_credits_per_semester += DEFAULT_CREDIT_HOURS
                            current_CS_elective_credits_per_semester += DEFAULT_CREDIT_HOURS
                            min_3000_course_still_needed -= 1
                            # print(f"Added: \t{'CMP SCI 3000+':<15}{'[User Selects]':<40} "
                            #     f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                            #     f"{total_credits_accumulated + 3:>15}")

                        # if condition 1, 2, or 3 fail, add a type of elective for balance
                        else:
                            if gen_ed_credits_still_needed > 0:
                                current_semester_classes.append(add_gen_ed_elective())
                                gen_ed_credits_still_needed -= DEFAULT_CREDIT_HOURS
                                print(f"Added: \t{'GEN ED':<15}{'[User Selects]':<40} "
                                    f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                    f"{total_credits_accumulated + 3:>15}")
                            else:
                                current_semester_classes.append(add_free_elective())
                                free_elective_credits_accumulated += DEFAULT_CREDIT_HOURS
                                # print(f"Added: \t{'FREE ELEC':<15}{'[User Selects]':<40} "
                                    # f"{current_semester_credits + 3:<2} of {min_credits_per_semester:<2}"
                                    # f"{total_credits_accumulated + 3:>15}")

                # regardless of the type of elective, add the credits
                total_credits_accumulated = total_credits_accumulated + DEFAULT_CREDIT_HOURS
                current_semester_credits = current_semester_credits + DEFAULT_CREDIT_HOURS

                is_graduated = graduation_check(
                                total_credits_accumulated, required_courses_tuple,
                                courses_taken, min_3000_course_still_needed,
                                cert_elective_courses_still_needed, gen_ed_credits_still_needed)

                # if current semester is fully generated or generating the whole schedule and has graduated, then stop generation
                if (current_semester_credits >= min_credits_per_semester) or (generate_complete_schedule and is_graduated):
                    current_semester_info = {
                        'semester': current_semester,
                        'semester_number': semester,
                        'credits': current_semester_credits,
                        'schedule': current_semester_classes,
                        'year': semester_years[current_semester]
                    }
                    course_schedule.append(current_semester_info)

                    # if only generating a semester stop here
                    if not generate_complete_schedule:
                        is_course_generation_complete = True

                    # reset semester info
                    current_semester_credits = 0
                    current_semester_classes = []
                    semester += 1
                    current_semester_cs_math_credits_per_semester = 0
                    current_CS_elective_credits_per_semester = 0
                    current_semester = update_semester(current_semester, include_summer)

                    if(current_semester == first_semester):
                        semester_years = {key: value + 1 for key, value in semester_years.items()}
                        # print(f"\nNext Semester, {current_semester} {semester_years[current_semester]}")
                    # ensure summer credit hours are not F/Sp credit hours
                    if (current_semester == "Summer" and generate_complete_schedule):
                        min_credits_per_semester = summer_credit_count
                    elif (current_semester != "Summer" and generate_complete_schedule):
                        min_credits_per_semester = temp_min_credits_per_semester

                    if is_graduated and generate_complete_schedule:
                        is_course_generation_complete = True
                        break
    else:
        # If generating new semester after graduation requirements complete, generate empty semester
        current_semester_info = {
            'semester': current_semester,
            'semester_number': semester,
            'credits': current_semester_credits,
            'schedule': current_semester_classes,
            'year': semester_years[current_semester]
        }
        course_schedule.append(current_semester_info)

        semester += 1
        current_semester = update_semester(current_semester, include_summer)

        if(current_semester == first_semester):
                            semester_years = {key: value + 1 for key, value in semester_years.items()}
                            # print(f"\nNext Semester, {current_semester} {semester_years[current_semester]}")

    if (current_semester != "Summer" and not generate_complete_schedule):
        min_credits_per_semester = temp_min_credits_per_semester

    minimum_semester_credits = None

    if is_graduated:
        minimum_semester_credits = list(map(lambda x: x, range(0, 1)))
    elif current_semester == "Summer":
        minimum_semester_credits = list(map(lambda x: x, range(0, 13)))
    else:
        minimum_semester_credits = list(map(lambda x: x, range(3, 22)))

    # print(f'{certificate_choice=}')
    #print(f'{certificate_option=}')
    # print(f'{certificate_choice_xml_tag=}')

    # print(f'{min_credits_per_semester=}')
    # print(f'{temp_min_credits_per_semester=}')

    # Calculating counter values (credits for ELECTIVES)
    accumulated_gen_eds = (TOTAL_CREDITS_FOR_GEN_EDS - gen_ed_credits_still_needed)
    accumulated_certificates = (TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES - (cert_elective_courses_still_needed* DEFAULT_CREDIT_HOURS))
    accumulated_3000 = (TOTAL_CREDITS_FOR_BSCS_ELECTIVES - ((min_3000_course_still_needed + cert_elective_courses_still_needed + num_3000_replaced_by_cert_core)*DEFAULT_CREDIT_HOURS))
    modified_total_for_3000 = (TOTAL_CREDITS_FOR_BSCS_ELECTIVES - (TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES+ (num_3000_replaced_by_cert_core*DEFAULT_CREDIT_HOURS)))
    modified_accumulated_3000 = (modified_total_for_3000 -(min_3000_course_still_needed*DEFAULT_CREDIT_HOURS))

    # print(f"{min_3000_course_still_needed=} {cert_elective_courses_still_needed=} {num_3000_replaced_by_cert_core=}")
    # print(f'TOTAL_CREDITS_FOR_GEN_EDS:               {accumulated_gen_eds:>2} / {TOTAL_CREDITS_FOR_GEN_EDS}')
    # print(f'TOTAL_CREDITS_FOR_BSCS_ELECTIVES:        {accumulated_3000:>2} / {TOTAL_CREDITS_FOR_BSCS_ELECTIVES}')
    # print(f'TOTAL_CREDITS_FOR_BSCS_ELECTIVES after certificate added: {modified_accumulated_3000} / {modified_total_for_3000}')
    # print(f'TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES: {accumulated_certificates:>2} / {TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES}')
    # print(f'Total Free Electives Accumulated:        {free_elective_credits_accumulated:<5}')
    # for course, info in required_courses_dict_list:
    #     print(f'{course}', end=", ")
    # print("\n")
    # print(f'{required_courses_dict_list=}')


    # complete graduation check
    # print("Certificate Electives Still Needed ", cert_elective_courses_still_needed)
    # print("Gen Eds Still Needed ", gen_ed_credits_still_needed)
    # print("Total Credits Accumulated ", total_credits_accumulated)
    # print("Required Courses Tuple ", required_courses_tuple)
    # print("Min 3000+ courses ", min_3000_course_still_needed)
    # print("courses taken", courses_taken)

    return {
        "required_courses_dict_list": json.dumps(required_courses_dict_list),
        "required_courses_dict_list_unchanged": json.dumps(courses_dict_list_unchanged),
        "semesters": user_semesters,
        "total_credits": total_credits_accumulated,
        "course_schedule": json.dumps(course_schedule),
        "course_schedule_display": course_schedule,
        "courses_taken": json.dumps(courses_taken),
        "list_of_required_courses_taken_display": courses_taken,
        "semester_number": semester,
        "waived_courses": waived_courses,
        "current_semester": current_semester,
        "minimum_semester_credits": minimum_semester_credits,
        "min_3000_course": min_3000_course_still_needed,
        "include_summer": include_summer,
        "certificate_choice": json.dumps(certificate_choice),
        "certificates_display": certificate_choice,
        "num_3000_replaced_by_cert_core": num_3000_replaced_by_cert_core,
        "cert_elective_courses_still_needed": cert_elective_courses_still_needed,
        "TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES": TOTAL_CREDITS_FOR_CERTIFICATE_ELECTIVES,
        "saved_minimum_credits_selection": min_credits_per_semester,
        "gen_ed_credits_still_needed": gen_ed_credits_still_needed,
        "full_schedule_generation": generate_complete_schedule,
        "minimum_summer_credits": summer_credit_count,
        "first_semester": first_semester,
        "semester_years": json.dumps(semester_years),
        "semester_years_display": semester_years,
        "course_prereqs_for": json.dumps(course_prereqs_for),
        "user_name": user_name,
        "fe_taken": free_elective_credits_accumulated,
        "ge_taken": ge_taken,
        "is_graduated": is_graduated,
        "required_courses_tuple": json.dumps(required_courses_tuple),
        "required_courses_tuple_display": required_courses_tuple
    }
