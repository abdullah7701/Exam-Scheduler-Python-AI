import numpy as np
import pandas as pd
import copy
import math
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

def import_data(fileDir):
    teachers_df = pd.read_csv(fileDir + 'teachers.csv')
    students_df = pd.read_csv(fileDir + 'studentNames.csv')
    rooms_df = pd.read_csv(fileDir + 'rooms.csv')
    courses_df = pd.read_csv(fileDir + 'courses.csv')
    registered_courses_df = pd.read_csv(fileDir + 'studentCourse.csv')

    teachers = list(teachers_df.iloc[:, 0])
    students = list(students_df.iloc[:, 0])
    rooms = {i + 1: capacity for i, capacity in enumerate(rooms_df.iloc[:, 1])}
    courses = {course_code: course_name for course_code, course_name in
               zip(courses_df.iloc[:, 0], courses_df.iloc[:, 1])}
    student_courses = {(student_name, course_code) for student_name, course_code in
                       zip(registered_courses_df.iloc[:, 1], registered_courses_df.iloc[:, 2])}

    return teachers, students, rooms, courses, student_courses

def random_solution(courses, students, rooms, num_days):
    exam_schedule = {}
    for course_code, course_name in courses.items():
        exam_schedule[course_code] = {
            'course': course_name,
            'room': random.sample(list(rooms.keys()), 1),
            'teacher': random.sample(teachers, 1),
            'time': random.choice([9, 14]),  # 9 AM or 2 PM
            'date': random.randint(1, num_days)  # Random date between 1 and num_days
        }
    return exam_schedule

def calculate_fitness(exam_schedule, student_courses, num_days):
    num_violations = 0
    for day in range(1, num_days + 1):
        for time in [9, 14]:
            exams_at_time = [course_code for course_code, exam in exam_schedule.items() if exam['date'] == day and exam['time'] == time]
            for student in students:
                num_exams = sum(1 for course_code in exams_at_time if (student, course_code) in student_courses)
                if num_exams > 1:
                    num_violations += 1

    for day in range(1, num_days + 1):
        for time in [9, 14]:
            exams_at_time = [exam for exam in exam_schedule.values() if exam['date'] == day and exam['time'] == time]
            teachers_at_time = [exam['teacher'][0] for exam in exams_at_time]
            if len(set(teachers_at_time)) != len(teachers_at_time):
                num_violations += 1

    return num_violations

def generate_neighbor_solution(current_solution, rooms, num_days):
    new_solution = copy.deepcopy(current_solution)

    exam_code, exam_info = random.choice(list(new_solution.items()))

    new_date = random.randint(1, num_days)

    new_solution[exam_code]['date'] = new_date
    new_solution[exam_code]['room'] = random.sample(list(rooms.keys()), 1)

    return new_solution

def simulated_annealing(initial_solution, student_courses, num_days, max_iterations, initial_temperature, cooling_rate):
    current_solution = initial_solution
    current_fitness = calculate_fitness(current_solution, student_courses, num_days)
    best_solution = current_solution.copy()
    best_fitness = current_fitness

    temperature = initial_temperature

    for i in range(max_iterations):
        new_solution = generate_neighbor_solution(current_solution, rooms, num_days)
        new_fitness = calculate_fitness(new_solution, student_courses, num_days)

        if new_fitness < current_fitness or random.uniform(0, 1) < math.exp((current_fitness - new_fitness) / temperature):
            current_solution = new_solution
            current_fitness = new_fitness

        if new_fitness < best_fitness:
            best_solution = new_solution
            best_fitness = new_fitness

        temperature *= cooling_rate

        print(f"Iteration {i + 1}: Fitness = {best_fitness}")

    return best_solution

def check_break_constraint(exam_schedule, num_days):
    num_violations = 0
    for day in range(1, num_days + 1):
        exams_at_time = [exam for exam in exam_schedule.values() if exam['date'] == day and exam['time'] == 13]  # 1 PM
        if exams_at_time:
            num_violations += 1
    return num_violations

def check_consecutive_exams_constraint(exam_schedule, student_courses, num_days):
    num_violations = 0
    for day in range(1, num_days + 1):
        exams_at_day = [exam for exam in exam_schedule.values() if exam['date'] == day]
        exams_at_day.sort(key=lambda x: x['time'])  # Sort exams by time on the day
        for i in range(len(exams_at_day) - 1):
            current_exam = exams_at_day[i]
            next_exam = exams_at_day[i + 1]
            if current_exam['time'] == 9 and next_exam['time'] == 14:  # Consecutive exams
                for student in students:
                    if (student, current_exam['course']) in student_courses and (student, next_exam['course']) in student_courses:
                        num_violations += 1
    return num_violations

def check_preferred_order_constraint(exam_schedule, student_courses):
    num_violations = 0
    for student in students:
        has_mg_course = any(course_code.startswith('MG') for (_, course_code) in student_courses if student == student)
        has_cs_course = any(course_code.startswith('CS') for (_, course_code) in student_courses if student == student)
        if has_mg_course and has_cs_course:
            mg_course_exam = next((exam for exam in exam_schedule.values() if exam['course'].startswith('MG') and (student, exam['course']) in student_courses), None)
            cs_course_exam = next((exam for exam in exam_schedule.values() if exam['course'].startswith('CS') and (student, exam['course']) in student_courses), None)
            if mg_course_exam and cs_course_exam:
                if mg_course_exam['date'] > cs_course_exam['date']:
                    num_violations += 1
    return num_violations


def check_faculty_meeting_constraint(exam_schedule, num_days):
    num_violations = 0
    half_days = math.ceil(num_days / 2)
    for day in range(1, half_days + 1):
        exams_at_day = [exam for exam in exam_schedule.values() if exam['date'] == day]
        if len(exams_at_day) == 0:
            num_violations += 1
    return num_violations

def calculate_soft_constraints(exam_schedule, student_courses, num_days):

    soft_constraints = {
        'Break on Friday': check_break_constraint(exam_schedule, num_days),
        'Consecutive Exams': check_consecutive_exams_constraint(exam_schedule, student_courses, num_days),
        'Preferred Order of MG and CS Courses': check_preferred_order_constraint(exam_schedule, student_courses),
        'Faculty Meeting Constraints': check_faculty_meeting_constraint(exam_schedule, num_days)
    }
    return soft_constraints

import tkinter as tk
from tkinter import ttk

def display_schedule_gui(exam_schedule_df_two_weeks, exam_schedule_df_three_weeks, soft_constraints_df_two_weeks, soft_constraints_df_three_weeks):
    # Create the main window for exam schedule
    exam_schedule_window = tk.Tk()
    exam_schedule_window.title("2-Week and 3-Week Exam Schedule")

    # Create a Frame for 2-week exam schedule
    exam_schedule_frame_two_weeks = ttk.Frame(exam_schedule_window)
    exam_schedule_frame_two_weeks.pack(pady=10)

    exam_schedule_label_two_weeks = tk.Label(exam_schedule_frame_two_weeks, text="2-Week Exam Schedule:", font=("Arial", 14, "bold"))
    exam_schedule_label_two_weeks.grid(row=0, column=0, columnspan=5, pady=5)

    exam_schedule_tree_two_weeks = ttk.Treeview(exam_schedule_frame_two_weeks, columns=('Course', 'Room', 'Date', 'Time', 'Teacher'), show='headings', height=15)
    exam_schedule_tree_two_weeks.grid(row=1, column=0, columnspan=5, padx=5)

    exam_schedule_tree_two_weeks.heading('Course', text='Course')
    exam_schedule_tree_two_weeks.heading('Room', text='Room')
    exam_schedule_tree_two_weeks.heading('Date', text='Date')
    exam_schedule_tree_two_weeks.heading('Time', text='Time')
    exam_schedule_tree_two_weeks.heading('Teacher', text='Teacher')

    # Add data to the Treeview widget for 2-week exam schedule
    for i, row in exam_schedule_df_two_weeks.iterrows():
        exam_schedule_tree_two_weeks.insert('', tk.END, values=(row['course'], row['room'], f"Day {row['date']}", f"{row['time']} {['AM', 'PM'][row['time'] == 14]}", row['teacher']))

    # Add a vertical scrollbar to the Treeview widget for 2-week exam schedule
    scrollbar_two_weeks = ttk.Scrollbar(exam_schedule_frame_two_weeks, orient="vertical", command=exam_schedule_tree_two_weeks.yview)
    scrollbar_two_weeks.grid(row=1, column=6, sticky="ns")
    exam_schedule_tree_two_weeks.configure(yscrollcommand=scrollbar_two_weeks.set)

    # Create a Frame for 3-week exam schedule
    exam_schedule_frame_three_weeks = ttk.Frame(exam_schedule_window)
    exam_schedule_frame_three_weeks.pack(pady=10)

    exam_schedule_label_three_weeks = tk.Label(exam_schedule_frame_three_weeks, text="3-Week Exam Schedule:", font=("Arial", 14, "bold"))
    exam_schedule_label_three_weeks.grid(row=0, column=0, columnspan=5, pady=5)

    exam_schedule_tree_three_weeks = ttk.Treeview(exam_schedule_frame_three_weeks, columns=('Course', 'Room', 'Date', 'Time', 'Teacher'), show='headings', height=15)
    exam_schedule_tree_three_weeks.grid(row=1, column=0, columnspan=5, padx=5)

    exam_schedule_tree_three_weeks.heading('Course', text='Course')
    exam_schedule_tree_three_weeks.heading('Room', text='Room')
    exam_schedule_tree_three_weeks.heading('Date', text='Date')
    exam_schedule_tree_three_weeks.heading('Time', text='Time')
    exam_schedule_tree_three_weeks.heading('Teacher', text='Teacher')

    # Add data to the Treeview widget for 3-week exam schedule
    for i, row in exam_schedule_df_three_weeks.iterrows():
        exam_schedule_tree_three_weeks.insert('', tk.END, values=(row['course'], row['room'], f"Day {row['date']}", f"{row['time']} {['AM', 'PM'][row['time'] == 14]}", row['teacher']))

    # Add a vertical scrollbar to the Treeview widget for 3-week exam schedule
    scrollbar_three_weeks = ttk.Scrollbar(exam_schedule_frame_three_weeks, orient="vertical", command=exam_schedule_tree_three_weeks.yview)
    scrollbar_three_weeks.grid(row=1, column=6, sticky="ns")
    exam_schedule_tree_three_weeks.configure(yscrollcommand=scrollbar_three_weeks.set)

    # Run the GUI event loop for exam schedule
    exam_schedule_window.mainloop()

    # Create a separate window for soft constraints
    soft_constraints_window = tk.Tk()
    soft_constraints_window.title("Soft Constraint Violations")

    # Create a Frame to contain the soft constraint violations data for 2-week
    soft_constraints_frame_two_weeks = ttk.Frame(soft_constraints_window)
    soft_constraints_frame_two_weeks.pack(pady=10)

    # Create a Label for the soft constraint violations section for 2-week
    soft_constraints_label_two_weeks = tk.Label(soft_constraints_frame_two_weeks, text="Soft Constraint Violations (2-Week):", font=("Arial", 14, "bold"))
    soft_constraints_label_two_weeks.grid(row=0, column=0, columnspan=5, pady=5)

    # Create a Treeview widget to display the soft constraint violations data in a table format for 2-week
    soft_constraints_tree_two_weeks = ttk.Treeview(soft_constraints_frame_two_weeks, columns=('Soft Constraint', 'Violations'), show='headings', height=10)
    soft_constraints_tree_two_weeks.grid(row=1, column=0, columnspan=5, padx=5)

    soft_constraints_tree_two_weeks.heading('Soft Constraint', text='Soft Constraint')
    soft_constraints_tree_two_weeks.heading('Violations', text='Violations')

    # Add data to the Treeview widget for 2-week
    for i, row in soft_constraints_df_two_weeks.iterrows():
        soft_constraints_tree_two_weeks.insert('', tk.END, values=(row['Soft Constraint'], row['Violations']))

    # Create a Frame to contain the soft constraint violations data for 3-week
    soft_constraints_frame_three_weeks = ttk.Frame(soft_constraints_window)
    soft_constraints_frame_three_weeks.pack(pady=10)

    # Create a Label for the soft constraint violations section for 3-week
    soft_constraints_label_three_weeks = tk.Label(soft_constraints_frame_three_weeks, text="Soft Constraint Violations (3-Week):", font=("Arial", 14, "bold"))
    soft_constraints_label_three_weeks.grid(row=0, column=0, columnspan=5, pady=5)

    # Create a Treeview widget to display the soft constraint violations data in a table format for 3-week
    soft_constraints_tree_three_weeks = ttk.Treeview(soft_constraints_frame_three_weeks, columns=('Soft Constraint', 'Violations'), show='headings', height=10)
    soft_constraints_tree_three_weeks.grid(row=1, column=0, columnspan=5, padx=5)

    soft_constraints_tree_three_weeks.heading('Soft Constraint', text='Soft Constraint')
    soft_constraints_tree_three_weeks.heading('Violations', text='Violations')

    # Add data to the Treeview widget for 3-week
    for i, row in soft_constraints_df_three_weeks.iterrows():
        soft_constraints_tree_three_weeks.insert('', tk.END, values=(row['Soft Constraint'], row['Violations']))

    # Run the GUI event loop for soft constraints
    soft_constraints_window.mainloop()

# Constants
fileDir = './test_dataset/'
num_days_two_weeks = 14
num_days_three_weeks = 21
max_iterations = 1000
initial_temperature = 1000.0
cooling_rate = 0.95

# Load data
teachers, students, rooms, courses, student_courses = import_data(fileDir)

# Generate initial solution for two weeks
initial_solution_two_weeks = random_solution(courses, students, rooms, num_days_two_weeks)

# Run simulated annealing algorithm to generate exam schedule for two weeks
exam_schedule_2_weeks = simulated_annealing(initial_solution_two_weeks, student_courses, num_days_two_weeks, max_iterations, initial_temperature, cooling_rate)

# Calculate soft constraints for two weeks
soft_constraints_two_weeks = calculate_soft_constraints(exam_schedule_2_weeks, student_courses, num_days_two_weeks)

# Generate initial solution for three weeks
initial_solution_three_weeks = random_solution(courses, students, rooms, num_days_three_weeks)

# Run simulated annealing algorithm to generate exam schedule for three weeks
exam_schedule_3_weeks = simulated_annealing(initial_solution_three_weeks, student_courses, num_days_three_weeks, max_iterations, initial_temperature, cooling_rate)

# Calculate soft constraints for three weeks
soft_constraints_three_weeks = calculate_soft_constraints(exam_schedule_3_weeks, student_courses, num_days_three_weeks)

# Convert the exam schedules to DataFrames
exam_schedule_df_two_weeks = pd.DataFrame(exam_schedule_2_weeks.values())
exam_schedule_df_three_weeks = pd.DataFrame(exam_schedule_3_weeks.values())

# Save exam schedules and soft constraint violations to CSV files
exam_schedule_df_two_weeks.to_csv('exam_schedule_two_weeks.csv', index=False)
exam_schedule_df_three_weeks.to_csv('exam_schedule_three_weeks.csv', index=False)

soft_constraints_df_two_weeks = pd.DataFrame(soft_constraints_two_weeks.items(), columns=['Soft Constraint', 'Violations'])
soft_constraints_df_three_weeks = pd.DataFrame(soft_constraints_three_weeks.items(), columns=['Soft Constraint', 'Violations'])

soft_constraints_df_two_weeks.to_csv('soft_constraints_two_weeks.csv', index=False)
soft_constraints_df_three_weeks.to_csv('soft_constraints_three_weeks.csv', index=False)

# Display the exam schedules and soft constraint violations in GUIs
display_schedule_gui(exam_schedule_df_two_weeks, exam_schedule_df_three_weeks, soft_constraints_df_two_weeks, soft_constraints_df_three_weeks)
