from langchain_core.tools import tool

COURSES = {
    1: [
        ("MS-251", "Probability & Statistics", 3.0),
        ("GE-160", "Applications of ICT", 3.0),
        ("GE-169", "Applied Physics", 3.0),
        ("GE-167", "Discrete Structures", 3.0),
        ("HQ-001", "Quran Translation - I", 0.5),
        ("GE-190", "Functional English", 3.0),
    ],
    2: [
        ("CC-112", "Programming Fundamentals", 3.0),
        ("CC-112-L", "Programming Fundamentals Lab", 1.0),
        ("CC-110", "Digital Logic Design", 2.0),
        ("CC-110-L", "Digital Logic Design Lab", 1.0),
        ("MS-252", "Linear Algebra", 3.0),
        ("GE-191", "Expository Writing", 3.0),
        ("GE-163", "Islamic Studies", 2.0),
        ("HQ-002", "Quran Translation - II", 0.5),
    ],
    3: [
        ("CC-211", "Object Oriented Programming", 3.0),
        ("CC-211-L", "Object Oriented Programming Lab", 1.0),
        ("CC-215", "Database Systems", 3.0),
        ("CC-215-L", "Database Systems Lab", 1.0),
        ("CC-210", "Computer Organization & Assembly Language", 3.0),
        ("GE-162", "Calculus & Analytical Geometry", 3.0),
        ("GE-192", "Introduction to Management", 2.0),
        ("HQ-003", "Quran Translation - III", 0.5),
    ],
    4: [
        ("CC-213", "Data Structures", 3.0),
        ("CC-213-L", "Data Structures Lab", 1.0),
        ("CC-312", "Information Security", 3.0),
        ("CC-214", "Computer Networks", 3.0),
        ("CC-212", "Software Engineering", 3.0),
        ("DC-220", "Advanced Database Management Systems", 3.0),
        ("HQ-004", "Quran Translation - IV", 0.5),
    ],
    5: [
        ("CC-313", "Analysis of Algorithms", 3.0),
        ("CC-310", "Artificial Intelligence", 3.0),
        ("DC-320", "Theory of Automata and Formal Languages", 3.0),
        ("DC-321", "Human Computer Interaction", 3.0),
        ("DC-322", "Computer Architecture", 3.0),
        ("EC-330", "Web Technologies / Elective", 3.0),
        ("HQ-005", "Quran Translation - V", 0.5),
    ],
    6: [
        ("CC-311", "Operating Systems", 3.0),
        ("EC-333", "Mobile Application Development / Elective", 3.0),
        ("EC-324", "Software Construction & Development / Elective", 3.0),
        ("EC-335", "Machine Learning / Elective", 3.0),
        ("EC-334", "Game Design and Development / Elective", 3.0),
        ("MS-253", "Multivariable Calculus", 3.0),
        ("HQ-006", "Quran Translation - VI", 0.5),
    ],
    7: [
        ("CC-411", "Final Year Project - I", 2.0),
        ("DC-328", "Parallel & Distributed Computing", 3.0),
        ("EC-345", "Computer Vision / Elective", 3.0),
        ("EC-425", "Software Quality Engineering / Elective", 3.0),
        ("MS-254", "Technical and Business Writing", 3.0),
        ("GE-263", "Entrepreneurship", 2.0),
        ("GE-262", "Professional Practices", 2.0),
        ("HQ-007", "Quran Translation - VII", 0.5),
    ],
    8: [
        ("CC-412", "Final Year Project - II", 4.0),
        ("DC-421", "Compiler Construction", 3.0),
        ("UE-272", "Introduction to Marketing", 3.0),
        ("GE-168", "Ideology and Constitution of Pakistan", 2.0),
        ("GE-363", "Civics and Community Engagement", 2.0),
        ("HQ-008", "Quran Translation - VIII", 0.5),
    ],
}

# Total credit hours per semester
SEMESTER_HOURS = {
    1: 15.5,
    2: 15.5,
    3: 16.5,
    4: 16.5,
    5: 18.5,
    6: 18.5,
    7: 18.5,
    8: 14.5,
}


@tool
def marks_to_grade_points(marks: int) -> float:
    """Convert subject marks (0-100) to PUCIT grade points. Use this when student shares course marks.
    Args:
        marks: The numeric marks obtained in the course (0-100).
    """
    if marks >= 85:
        return 4.0
    if marks >= 80:
        return 3.7
    if marks >= 75:
        return 3.3
    if marks >= 70:
        return 3.0
    if marks >= 65:
        return 2.7
    if marks >= 61:
        return 2.3
    if marks >= 58:
        return 2.0
    if marks >= 55:
        return 1.7
    if marks >= 50:
        return 1.0
    return 0.0


@tool
def calculate_semester_gpa(grade_points: list[float], credit_hours: list[float]) -> float:
    """Calculate semester GPA from grade points and credit hours. Use this after converting course marks.
    
    Args:
        grade_points: List of grade points for each course (e.g. [4.0, 3.3, 2.7]).
        credit_hours: List of corresponding credit hours for each course (e.g. [3.0, 3.0, 3.0]).
    """
    if len(grade_points) != len(credit_hours) or len(grade_points) == 0:
        return 0.0

    total_weighted_points = 0.0
    total_credit_hours = 0.0

    for i in range(len(grade_points)):
        total_weighted_points += grade_points[i] * credit_hours[i]
        total_credit_hours += credit_hours[i]

    if total_credit_hours == 0.0:
        return 0.0

    return round(total_weighted_points / total_credit_hours, 2)


@tool
def calculate_new_cgpa(
    current_cgpa: float,
    completed_credit_hours: float,
    semester_gpa: float,
    semester_credit_hours: float,
) -> float:
    """Project new CGPA after completing a new semester. Use this when current CGPA and new semester GPA are known.
    
    Args:
        current_cgpa: Student's current cumulative GPA (e.g. 3.1).
        completed_credit_hours: Total credit hours completed before this semester (e.g. 64.0).
        semester_gpa: GPA obtained or expected in the new semester (e.g. 3.6).
        semester_credit_hours: Total credit hours in the new semester (e.g. 18.5).
    """
    total_credits = completed_credit_hours + semester_credit_hours
    if total_credits == 0.0:
        return 0.0

    old_total_points = current_cgpa * completed_credit_hours
    new_semester_points = semester_gpa * semester_credit_hours
    new_cgpa = (old_total_points + new_semester_points) / total_credits

    return round(new_cgpa, 2)


@tool
def required_gpa_for_target(
    target_cgpa: float,
    current_cgpa: float,
    completed_credit_hours: float,
    remaining_credit_hours: float,)->float:
    """Calculate the GPA required across remaining credit hours to hit a target CGPA. Use this for graduation target planning.
    
    Args:
        target_cgpa: The desired final target CGPA (e.g. 3.4).
        current_cgpa: The student's current CGPA (e.g. 3.0).
        completed_credit_hours: Total credit hours completed so far (e.g. 64.0).
        remaining_credit_hours: Credit hours remaining across future semesters (e.g. 55.5).
    """
    if remaining_credit_hours <= 0.0:
        return 0.0

    total_credits = completed_credit_hours + remaining_credit_hours
    needed_total_points = target_cgpa * total_credits
    current_total_points = current_cgpa * completed_credit_hours

    required_gpa = (needed_total_points - current_total_points) / remaining_credit_hours
    return round(required_gpa, 2)


@tool
def get_semester_courses(semester: int) -> str:
    """Get list of courses and credit hours for a given semester (1-8). Use this when user asks about semester subjects.
    
    Args:
        semester: The semester number (integer from 1 to 8).
    """
    if semester < 1 or semester > 8:
        return "Error: semester must be between 1 and 8"

    courses_list = COURSES[semester]
    output = f"Courses for Semester {semester}:\n"
    for code, title, cr in courses_list:
        output += f"- {code}: {title} ({cr} credit hours)\n"

    return output.strip()


@tool
def get_remaining_credit_hours(current_semester: int) -> float:
    """Calculate remaining credit hours left in degree after a given semester. Use this when calculating target GPA for future semesters.
    Args:
        current_semester: The completed or current semester number (integer from 1 to 8).
    """
    if current_semester < 1 or current_semester > 8:
        return 0.0

    remaining = 0.0
    for sem in range(current_semester + 1, 9):
        remaining += SEMESTER_HOURS[sem]

    return remaining


@tool
def save_report(filename: str, content: str) -> str:
    """Save calculation summary or plan to a file. Use ONLY when the user explicitly agrees or asks to save.
    
    Args:
        filename: The name of the file to save (e.g. 'plan.txt').
        content: The text summary or report content to write to the file.
    """
    if not filename.endswith(".txt"):
        filename = filename + ".txt"

    try:
        file = open(filename, "w", encoding="utf-8")
        file.write(content)
        file.close()
        return f"Successfully saved to {filename}"
    except Exception as e:
        return f"Error: Could not save report ({str(e)})"


ALL_TOOLS = [
    marks_to_grade_points,
    calculate_semester_gpa,
    calculate_new_cgpa,
    required_gpa_for_target,
    get_semester_courses,
    get_remaining_credit_hours,
    save_report,
]

