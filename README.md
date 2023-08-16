# Exam-Scheduler-Python-AI
This code is for generating and optimizing exam schedules using simulated annealing. The code also checks soft constraints (breaks, consecutive exams, preferred order, faculty meetings), calculates violations, and displays  results using a tkinter GUI with two-week and three-week exam schedules.

Exam Schedule Optimization using Simulated Annealing
This repository contains a Python implementation of an exam schedule optimization algorithm using the simulated annealing technique. The code aims to create efficient exam schedules for educational institutions, considering various constraints such as room availability, teacher assignments, and student preferences.

Table of Contents
Introduction
Features
Installation
Usage
Data
Results
Contributing
License
Introduction
Managing exam schedules for educational institutions can be complex due to various factors such as room availability, teacher assignments, and student preferences. This Python code provides an optimization solution using the simulated annealing algorithm to create effective exam schedules while considering both hard and soft constraints.

Features
Import data from CSV files (teachers, students, rooms, courses, registered courses)
Generate random initial exam schedules
Perform simulated annealing optimization
Calculate violations for various soft constraints (breaks, consecutive exams, preferred order, faculty meetings)
Display optimized exam schedules and violation information in a graphical user interface (GUI)
Installation
Clone the repository:
bash
Copy code
git clone https://github.com/your-username/exam-schedule-optimization.git
cd exam-schedule-optimization
Install the required Python packages:
bash
Copy code
pip install -r requirements.txt
Usage
Place your CSV files containing teachers, students, rooms, courses, and registered courses in the test_dataset folder.
Modify the constants in the code as needed (e.g., fileDir, num_days_two_weeks, num_days_three_weeks, max_iterations, initial_temperature, cooling_rate).
Run the main script:
bash
Copy code
python main.py
The GUI will display the optimized exam schedules and soft constraint violation information.
Data
The data required for the optimization process should be provided in CSV format. The following CSV files are expected in the test_dataset folder:

teachers.csv: List of teachers' names
studentNames.csv: List of student names
rooms.csv: List of rooms and their capacities
courses.csv: List of course codes and names
studentCourse.csv: List of registered student courses
Results
The code generates optimized exam schedules for both two-week and three-week periods. It also calculates violations for various soft constraints and presents the results using a GUI.

Contributing
Contributions to this project are welcome. If you find any bugs or want to add new features, please submit an issue or a pull request.

License
This project is licensed under the MIT License.

Feel free to customize this template to include any additional information or sections that you think would be relevant to your project.
