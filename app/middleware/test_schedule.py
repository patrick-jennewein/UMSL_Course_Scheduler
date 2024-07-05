GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# check degrees
def check_BSCS (degree, user_courses):
    print(f"Checking {degree}...")
    BSCS_core = [
        "CMP SCI 1000",
        "CMP SCI 1250",
        "CMP SCI 2250",
        "CMP SCI 2261",
        "CMP SCI 2700",
        "CMP SCI 2750",
        "CMP SCI 3010",
        "CMP SCI 3130",
        "CMP SCI 4250",
        "CMP SCI 4280",
        "CMP SCI 4500",
        "CMP SCI 4760",
        "MATH 1320",
        "MATH 1800",
        "MATH 1900",
        "MATH 2450",
        "MATH 3000",
        "ENGLISH 1100",
        "ENGLISH 3130",
        "INTDSC 1003"
    ]
    for course in BSCS_core:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")


def check_BS_ComputingTechnology(degree, user_courses):
    print(f"Checking {degree}...")
    BSComputing_Technology_core = [
        "CMP SCI 1000",
        "CMP SCI 1250",
        "CMP SCI 2250",
        "CMP SCI 2261",
        "CMP SCI 2700",
        "CMP SCI 2750",
        "CMP SCI 3010",
        "CMP SCI 4010",
        "CMP SCI 4500",
        "CMP SCI 4610",
        "INFSYS 3820",
        "INFSYS 3844",
        "MATH 1320",
        "MATH 3000",
        "ENGLISH 1100",
        "ENGLISH 3130",
        "INTDSC 1003"
    ]
    for course in BSComputing_Technology_core:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [1, "CMP SCI 3702", "CMP SCI 3780"],
        [1, "MATH 1100", "MATH 1800"]
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


def check_BS_Cyber(degree, user_courses):
    print(f"Checking {degree}...")
    BS_Cyber_core = [
        "CMP SCI 1250",
        "CMP SCI 2250",
        "CMP SCI 2261",
        "CMP SCI 2700",
        "CMP SCI 2750",
        "CMP SCI 3010",
        "CMP SCI 3130",
        "CMP SCI 3780",
        "CMP SCI 4700",
        "CMP SCI 4732",
        "CMP SCI 4750",
        "CMP SCI 4760",
        "CMP SCI 4782",
        "CMP SCI 4794",
        "INFSYS 3868",
        "INFSYS 3878",
        "MATH 1320",
        "MATH 3000",
        "ENGLISH 1100",
        "INTDSC 1003"
    ]
    for course in BS_Cyber_core:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [1, "ENGLISH 3120", "ENGLISH 3130"],
        [1, "CMP SCI 3702", "CMP SCI 3848"],
        [1, "MATH 1100", "MATH 1800"]
    ]
    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


def check_BS_DataScience(degree, user_courses):
    print(f"Checking {degree}...")
    BS_DataScience_core = [
        "MATH 1320",
        "MATH 4005",
        "CMP SCI 1250",
        "CMP SCI 4200",
        "CMP SCI 4342",
        "CMP SCI 2250",
        "CMP SCI 2261",
        "CMP SCI 3130",
        "CMP SCI 3411",
        "CMP SCI 4151",
        "CMP SCI 4340",
        "MATH 1900",
        "MATH 3000",
        "ENGLISH 1100",
        "INTDSC 1003"
    ]
    for course in BS_DataScience_core:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [1, "MATH 1800", "MATH 1100"],
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


# check certificates
def checkAI(cert, user_courses):
    print(f"Checking {cert}...")
    core_courses = [
        "CMP SCI 3130",
        "CMP SCI 4300"
    ]
    for course in core_courses:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [3, "CMP SCI 4151", "CMP SCI 4320", "CMP SCI 4340", "CMP SCI 4342",
         "CMP SCI 4370", "CMP SCI 4390", "CMP SCI 4420", ],
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")

def checkWeb(cert, user_courses):
    print(f"Checking {cert}...")
    core_courses = [
        "CMP SCI 3010",
        "CMP SCI 4010",
        "CMP SCI 4011",
        "CMP SCI 4012",
    ]
    for course in core_courses:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [1, "CMP SCI 4020", "CMP SCI 4610","CMP SCI 4730","CMP SCI 4750","CMP SCI 4794"],
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


def checkMobile(cert, user_courses):
    print(f"Checking {cert}...")
    core_courses = [
        "CMP SCI 4020",
        "CMP SCI 4220",
        "CMP SCI 4792"
    ]
    for course in core_courses:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [1, "CMP SCI 4010", "CMP SCI 4610", "CMP SCI 4750", "CMP SCI 4794"]
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


def checkCyber(cert, user_courses):
    print(f"Checking {cert}...")
    # check xors
    xors = [
        [1, "CMP SCI 3702", "INFSYS 3848"],
        [1, "CMP SCI 4730", "INFSYS 3842"],
        [1, "CMP SCI 4782", "INFSYS 3858"],
        [2, "CMP SCI 4700", "CMP SCI 4020", "CMP SCI 4732", "CMP SCI 4750", "CMP SCI 4792", "CMP SCI 4794", "INFSYS 3868","INFSYS 3878"]
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


def checkData(cert, user_courses):
    print(f"Checking {cert}...")
    core_courses = [
        "CMP SCI 4200",
        "CMP SCI 4340",
        "CMP SCI 4342"
    ]
    for course in core_courses:
        if course in user_courses:
            print(f"\t{course:<80}{GREEN}PASSED{RESET}")
        else:
            print(f"\t{course:<80}{RED}FAILED{RESET}")

    # check xors
    xors = [
        [2, "CMP SCI 3411","CMP SCI 4151","CMP SCI 4300","CMP SCI 4320","CMP SCI 4370","CMP SCI 4390", "MATH 4005"]
    ]

    for xor in xors:
        required_num = xor[0]
        intersection = set(user_courses) & set(xor)
        left_column = f"{required_num} of {xor[1:]}"
        if len(intersection) >= required_num:
            print(f"\t{left_column:<80}{GREEN}PASSED{RESET}")
            print(f"\t\tChose{intersection}")
        else:
            print(f"\t{left_column:<80}{RED}FAILED{RESET}")
            print(f"\t\tChose{intersection}")


def test_schedule(degree, user_courses_raw, certificate = ""):
    print()
    print("#################")
    print("#### TESTING ####")
    print("#################")

    user_courses = [course[0] for course in user_courses_raw]
    if degree == "BSComputerScience":
        check_BSCS(degree, user_courses)
    elif degree == "BSComputingTechnology":
        check_BS_ComputingTechnology(degree, user_courses)
    elif degree == "BSCyberSecurity":
        check_BS_Cyber(degree, user_courses)
    elif degree == "BSDataScience":
        check_BS_DataScience(degree, user_courses)
    else:
        print("DEGREE ERROR!")
    if certificate:
        if certificate == "Artificial Intelligence":
            checkAI(certificate, user_courses)
        elif certificate == "Cybersecurity":
            checkCyber(certificate, user_courses)
        elif certificate == "Data Science":
            checkData(certificate, user_courses)
        elif certificate == "Mobile Apps and Computing":
            checkMobile(certificate, user_courses)
        elif certificate == "Internet and Web":
            checkWeb(certificate, user_courses)
        else:
            print("CERTIFICATE ERROR!")
    print()
    print()