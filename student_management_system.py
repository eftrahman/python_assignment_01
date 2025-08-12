from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json
import os
 
# ==============================
# SECTION 1: DATA MODEL CLASSES
# ==============================
 
@dataclass
class Person:
    """
    The most basic human we can code — name, age, and address.
    """
    name: str
    age: int
    address: str
 
    def display_person_info(self) -> None:
        """
        Politely tells you who they are and where they live.
        (Na, ekhane exact location share korben na…)
        """
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Address: {self.address}")
 
 
@dataclass
class Student(Person):
    """
    Represents a student, inheriting from Person.
    """
    student_id: str
    grades: Dict[str, str] = field(default_factory=dict)   
    courses: List[str] = field(default_factory=list)       
 
    # ------------------------------
    # Student-specific functionality
    # ------------------------------
    def add_grade(self, course_code: str, grade: str) -> None:
        """
        Add or update the grade for a subject/course.
        """
        self.grades[course_code] = grade
 
    def enroll_course(self, course_code: str) -> None:
        """
        Enroll in a specified course (store by course code). — no admission test here, bhai.
        """
        if course_code not in self.courses:
            self.courses.append(course_code)
 
    def display_student_info(self, course_lookup: Optional[Dict[str, "Course"]] = None) -> None:
        """
        Print all student details. If course_lookup is provided, show course names.
        """
        print("Student Information:")
        print(f"Name: {self.name}")
        print(f"ID: {self.student_id}")
        print(f"Age: {self.age}")
        print(f"Address: {self.address}")
 
        # Resolve course names if lookup provided, else show codes
        if course_lookup:
            enrolled_names = [course_lookup[cc].course_name for cc in self.courses if cc in course_lookup]
            print(f"Enrolled Courses: {', '.join(enrolled_names) if enrolled_names else 'None'}")
 
            # Show grades with course names where possible
            pretty_grades = {}
            for cc, g in self.grades.items():
                if cc in course_lookup:
                    pretty_grades[course_lookup[cc].course_name] = g
                else:
                    pretty_grades[cc] = g
            print(f"Grades: {pretty_grades if pretty_grades else '{}'}")
        else:
            print(f"Enrolled Courses: {', '.join(self.courses) if self.courses else 'None'}")
            print(f"Grades: {self.grades if self.grades else '{}'}")
 
 
@dataclass
class Course:
    """
    Represents a course.
    """
    course_name: str
    course_code: str
    instructor: str
    students: List[str] = field(default_factory=list)  # Store student IDs for compactness
 
    # ------------------------------
    # Course-specific functionality
    # ------------------------------
    def add_student(self, student_id: str) -> None:
        """
        Add a student to the course by student ID. 
        """
        if student_id not in self.students:
            self.students.append(student_id)
 
    def display_course_info(self, student_lookup: Optional[Dict[str, Student]] = None) -> None:
        """
        Print course details and enrolled students. If student_lookup is provided, show student names.
        """
        print("Course Information:")
        print(f"Course Name: {self.course_name}")
        print(f"Code: {self.course_code}")
        print(f"Instructor: {self.instructor}")
        if student_lookup:
            student_names = [student_lookup[sid].name for sid in self.students if sid in student_lookup]
            print(f"Enrolled Students: {', '.join(student_names) if student_names else 'None'}")
        else:
            print(f"Enrolled Students (IDs): {', '.join(self.students) if self.students else 'None'}")
 
 
# ==================================
# SECTION 2: IN-MEMORY "DATABASE"
# ==================================
 
class DataStore:
    """
    Holds in-memory collections of students and courses, and provides
    JSON for saving/loading.
    (Ekhane jinish harabe na, InshaAllah.)
    """
    def __init__(self) -> None:
        self.students: Dict[str, Student] = {}  # key: student_id
        self.courses: Dict[str, Course] = {}    # key: course_code
 
    # ------------------------------
    # CRUD helpers for Students
    # ------------------------------
    def add_student(self, student: Student) -> bool:
        if student.student_id in self.students:
            return False
        self.students[student.student_id] = student
        return True
 
    def get_student(self, student_id: str) -> Optional[Student]:
        return self.students.get(student_id)
 
    # ------------------------------
    # CRUD helpers for Courses
    # ------------------------------
    def add_course(self, course: Course) -> bool:
        if course.course_code in self.courses:
            return False
        self.courses[course.course_code] = course
        return True
 
    def get_course(self, course_code: str) -> Optional[Course]:
        return self.courses.get(course_code)
 
    # ------------------------------
    # Enrollment & Grades
    # ------------------------------
    def enroll(self, student_id: str, course_code: str) -> str:
        student = self.get_student(student_id)
        if not student:
            return "Error: Student ID not found."
        course = self.get_course(course_code)
        if not course:
            return "Error: Course code not found."
 
        # Enroll both ways
        student.enroll_course(course_code)
        course.add_student(student_id)
        return f"Student {student.name} (ID: {student.student_id}) enrolled in {course.course_name} (Code: {course.course_code})."
 
    def add_grade(self, student_id: str, course_code: str, grade: str) -> str:
        student = self.get_student(student_id)
        if not student:
            return "Error: Student ID not found."
        course = self.get_course(course_code)
        if not course:
            return "Error: Course code not found."
 
        # Must be enrolled before adding a grade
        if course_code not in student.courses:
            return "Error: Student must be enrolled in the course before assigning a grade."
 
        student.add_grade(course_code, grade)
        return f"Grade {grade} added for {student.name} in {course.course_name}."
 
    # ------------------------------
    # Persistence (Save/Load JSON)
    # ------------------------------
    def to_json(self) -> dict:
        """
        Serialize students and courses into a JSON-serializable dict.
        Keep references by IDs/codes to avoid circular structures.
        """
        return {
            "students": {
                sid: {
                    "name": s.name,
                    "age": s.age,
                    "address": s.address,
                    "student_id": s.student_id,
                    "grades": s.grades,
                    "courses": s.courses,
                } for sid, s in self.students.items()
            },
            "courses": {
                cc: {
                    "course_name": c.course_name,
                    "course_code": c.course_code,
                    "instructor": c.instructor,
                    "students": c.students,
                } for cc, c in self.courses.items()
            }
        }
 
    @staticmethod
    def from_json(data: dict) -> "DataStore":
        """
        Reconstruct a DataStore from the serialized dict.
        """
        ds = DataStore()
        # Rebuild students
        for sid, s in data.get("students", {}).items():
            ds.students[sid] = Student(
                name=s["name"],
                age=s["age"],
                address=s["address"],
                student_id=s["student_id"],
                grades=s.get("grades", {}),
                courses=s.get("courses", []),
            )
        # Rebuild courses
        for cc, c in data.get("courses", {}).items():
            ds.courses[cc] = Course(
                course_name=c["course_name"],
                course_code=c["course_code"],
                instructor=c["instructor"],
                students=c.get("students", []),
            )
        return ds
 
    def save_to_file(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_json(), f, indent=2)
 
    @staticmethod
    def load_from_file(path: str) -> "DataStore":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return DataStore.from_json(data)
 
 
# ==================================
# SECTION 3: CLI HELPER FUNCTIONS
# ==================================
 
DATA_FILE = "students_courses_data.json"
 
def prompt_int(prompt_text: str) -> int:
    """
    Robust integer input for age, with retry on invalid inputs.
    """
    while True:
        raw = input(prompt_text).strip()
        if raw.isdigit():
            return int(raw)
        print("Invalid input. Please enter a valid number.")
 
def add_new_student_cli(ds: DataStore) -> None:
    name = input("Enter Name: ").strip()
    age = prompt_int("Enter Age: ")
    address = input("Enter Address: ").strip()
    student_id = input("Enter Student ID: ").strip()
 
    # Validate presence
    if not all([name, address, student_id]):
        print("Error: Name, Address, and Student ID are required.")
        return
 
    student = Student(name=name, age=age, address=address, student_id=student_id)
    if ds.add_student(student):
        print(f"Student {student.name} (ID: {student.student_id}) added successfully.")
    else:
        print("Error: A student with this ID already exists.")
 
def add_new_course_cli(ds: DataStore) -> None:
    course_name = input("Enter Course Name: ").strip()
    course_code = input("Enter Course Code: ").strip()
    instructor = input("Enter Instructor: ").strip()
 
    # Validate presence
    if not all([course_name, course_code, instructor]):
        print("Error: Course Name, Course Code, and Instructor are required.")
        return
 
    course = Course(course_name=course_name, course_code=course_code, instructor=instructor)
    if ds.add_course(course):
        print(f"Course {course.course_name} (Code: {course.course_code}) created with instructor {course.instructor}.")
    else:
        print("Error: A course with this code already exists.")
 
def enroll_student_in_course_cli(ds: DataStore) -> None:
    student_id = input("Enter Student ID: ").strip()
    course_code = input("Enter Course Code: ").strip()
    msg = ds.enroll(student_id, course_code)
    print(msg)
 
def add_grade_for_student_cli(ds: DataStore) -> None:
    student_id = input("Enter Student ID: ").strip()
    course_code = input("Enter Course Code: ").strip()
    grade = input("Enter Grade: ").strip()
 
    if not grade:
        print("Error: Grade cannot be empty.")
        return
    msg = ds.add_grade(student_id, course_code, grade)
    print(msg)
 
def display_student_details_cli(ds: DataStore) -> None:
    student_id = input("Enter Student ID: ").strip()
    student = ds.get_student(student_id)
    if not student:
        print("Error: Student ID not found.")
        return
    # Show student info resolving course names
    student.display_student_info(course_lookup=ds.courses)
 
def display_course_details_cli(ds: DataStore) -> None:
    course_code = input("Enter Course Code: ").strip()
    course = ds.get_course(course_code)
    if not course:
        print("Error: Course code not found.")
        return
    # Show course info resolving student names
    course.display_course_info(student_lookup=ds.students)
 
def save_data_cli(ds: DataStore) -> None:
    ds.save_to_file(DATA_FILE)
    print("All student and course data saved successfully.")
 
def load_data_cli() -> DataStore:
    if not os.path.exists(DATA_FILE):
        print("No data file found. Starting with a new database.")
        return DataStore()
    ds = DataStore.load_from_file(DATA_FILE)
    print("Data loaded successfully.")
    return ds
 
 
# ==================================
# SECTION 4: MENU LOOP
# ==================================
 
MENU_TEXT = """
==== Student Management System ====
1. Add New Student
2. Add New Course
3. Enroll Student in Course
4. Add Grade for Student
5. Display Student Details
6. Display Course Details
7. Save Data to File
8. Load Data from File
0. Exit
"""
 
def main() -> None:
    ds = DataStore()
    while True:
        print(MENU_TEXT)
        choice = input("Select Option: ").strip()
 
        if choice == "1":
            add_new_student_cli(ds)
        elif choice == "2":
            add_new_course_cli(ds)
        elif choice == "3":
            enroll_student_in_course_cli(ds)
        elif choice == "4":
            add_grade_for_student_cli(ds)
        elif choice == "5":
            display_student_details_cli(ds)
        elif choice == "6":
            display_course_details_cli(ds)
        elif choice == "7":
            save_data_cli(ds)
        elif choice == "8":
            ds = load_data_cli()
        elif choice == "0":
            print("Exiting Student Management System. Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")
 
if __name__ == "__main__":
    # Running as a script launches the CLI menu.
    # Import and reuse DataStore & classes for testing if needed.
    main()
