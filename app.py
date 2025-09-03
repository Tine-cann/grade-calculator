from flask import Flask, render_template_string, request

app = Flask(__name__)

html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Grade Calculator</title>
    <style>
        input[type=number] {
            width: 300px;
            padding: 8px;
            font-size: 16px;
        }
        form {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
        }
    </style>
</head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">

    <h1>Grade Calculator</h1>

    <form method="POST">
        <h2>Prelims</h2>
        <input type="number" name="absences_prelim" placeholder="Enter amount of Absences" min="0" step="1" required>
        <input type="number" name="prelim_exam_grade" placeholder="Enter Prelim Exam Grade" min="0" max="100" step="1" required>
        <input type="number" name="prelim_quizzes_grade" placeholder="Enter Quizzes Grade" min="0" max="100" step="1" required>
        <input type="number" name="prelim_requirements" placeholder="Enter Requirements Grade" min="0" max="100" step="1" required>
        <input type="number" name="prelim_recitation_grade" placeholder="Enter Recitation Grade" min="0" max="100" step="1" required>

        <h2>Midterms</h2>
        <input type="number" name="absences_midterms" placeholder="Enter amount of Absences" min="0" step="1" required>
        <input type="number" name="midterm_exam_grade" placeholder="Enter Midterm Exam Grade" min="0" max="100" step="1" required>
        <input type="number" name="midterm_quizzes_grade" placeholder="Enter Quizzes Grade" min="0" max="100" step="1" required>
        <input type="number" name="midterm_requirements" placeholder="Enter Requirements Grade" min="0" max="100" step="1" required>
        <input type="number" name="midterm_recitation_grade" placeholder="Enter Recitation Grade" min="0" max="100" step="1" required>

        <h2>Finals</h2>
        <input type="number" name="absences_finals" placeholder="Enter amount of Absences" min="0" step="1" required>
        <input type="number" name="finals_exam_grade" placeholder="Enter Final Exam Grade" min="0" max="100" step="1" required>
        <input type="number" name="finals_quizzes_grade" placeholder="Enter Quizzes Grade" min="0" max="100" step="1" required>
        <input type="number" name="finals_requirements_grade" placeholder="Enter Requirements Grade" min="0" max="100" step="1" required>
        <input type="number" name="finals_recitation_grade" placeholder="Enter Recitation Grade" min="0" max="100" step="1" required>
        <br>

        <button type="submit">Calculate Grades</button>
    </form>
    <br>
    <br>
    <br>

    <h1>Results</h1>
    {% if prelim_grade is not none %}
        <h3>Prelim Grade: {{ prelim_grade }}</h3>
        <h3>Midterms Grade: {{ midterm_grade }}</h3>
        <h3>Finals Grade: {{ finals_grade }}</h3>
        

        {% if failed_due_to_absences %}
            <h3>Overall Grade: {{ overall_grade }} FAILED</h3>
        {% elif failed_requirements_not_met %}
            <h3>Overall Grade: {{overall_grade}} FAILED</h3>
        {% elif passed_deanslister %}
            <h3>Overall Grade: {{ overall_grade }} PASSED (QUALIFIED FOR DEAN'S LIST)</h3>
        {% else %}
            <h3>Overall Grade: {{ overall_grade }} PASSED</h3>
        {% endif %}

        <br>
        <br>
        <p>To pass with 75%, you need a Midterm grade of 50% and a Final grade of 92%.</p>
        <p>To achieve 90%, you need a Midterm grade of 70% and a Final grade of 94%.</p>
    {% endif %}

    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}

    <script>
    document.querySelectorAll('input[type=number]').forEach(input => {
        input.addEventListener('keydown', function (e) {
            if (
                e.key === 'e' || e.key === 'E' ||
                e.key === '+' || e.key === '-' ||
                (e.key === '.' && this.value.includes('.'))
            ) {
                e.preventDefault();
            }
        });

        input.addEventListener('wheel', function (e) {
            e.preventDefault();
        });
    });
    </script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calculate():
    
    #display none when values are not calculated yet
    error = None
    prelim_grade = midterm_grade = finals_grade = overall_grade = None
    failed_due_to_absences = False
    failed_requirements_not_met = False
    passed_deanslister = False
    passed = False

    #requests values from form 
    if request.method == "POST":
        #catches missing value
        try:
            def get_float(field):
                val = request.form.get(field, "").strip()
                if val == "":
                    raise ValueError(f"Missing value for {field}")
                return float(val)

            # Get all form values
            prelim_absences = get_float("absences_prelim")
            prelim_exam = get_float("prelim_exam_grade")
            prelim_quiz = get_float("prelim_quizzes_grade")
            prelim_requirements = get_float("prelim_requirements")
            prelim_recitation = get_float("prelim_recitation_grade")

            midterm_absences = get_float("absences_midterms")
            midterm_exam = get_float("midterm_exam_grade")
            midterm_quiz = get_float("midterm_quizzes_grade")
            midterm_requirements = get_float("midterm_requirements")
            midterm_recitation = get_float("midterm_recitation_grade")

            finals_absences = get_float("absences_finals")
            finals_exam = get_float("finals_exam_grade")
            finals_quiz = get_float("finals_quizzes_grade")
            finals_requirements = get_float("finals_requirements_grade")
            finals_recitation = get_float("finals_recitation_grade")

            # Validate ranges
            absences = [prelim_absences, midterm_absences, finals_absences]
            grades = [
                prelim_exam, prelim_quiz, prelim_requirements, prelim_recitation,
                midterm_exam, midterm_quiz, midterm_requirements, midterm_recitation,
                finals_exam, finals_quiz, finals_requirements, finals_recitation
            ]

            #catches if values are valid or not
            if not all(0 <= a for a in absences):
                raise ValueError("Absences must be 0 or greater than 0.")
            if not all(0 <= g <= 100 for g in grades):
                raise ValueError("All grades must be between 0 and 100.")

            total_absences = sum(absences)

           

            #attendance calculation
            absence_penalty = 0 if total_absences == 0 else 10
            final_attendance = 100 - absence_penalty

            #gets the prelim class standing
            prelim_class_standing = round((prelim_quiz * 0.40) + 
                                          (prelim_requirements * 0.30) + 
                                          (prelim_recitation * 0.30), 2)

            #gets the midterm class standing
            midterms_class_standing = round((midterm_quiz * 0.40) + 
                                          (midterm_requirements * 0.30) + 
                                          (midterm_recitation * 0.30), 2)
            
            #gets the final class standing
            finals_class_standing = round((finals_quiz * 0.40) + 
                                          (finals_requirements * 0.30) + 
                                          (finals_recitation * 0.30), 2)

            #computation for prelim grade
            prelim_grade = round((prelim_exam * 0.60) +
                                 (final_attendance * 0.10) +
                                 (prelim_class_standing * 0.30), 2)

            #computation for midterm grade
            midterm_grade = round((midterm_exam * 0.60) +
                                  (final_attendance * 0.10) +
                                  (midterms_class_standing * 0.30), 2)

            #computation for final grade
            finals_grade = round((finals_exam * 0.60) +
                                 (final_attendance * 0.10) +
                                 (finals_class_standing * 0.30), 2)

            #computation for overall grade
            overall_grade = round(
                (prelim_grade * 0.20) + (midterm_grade * 0.30) + (finals_grade * 0.50), 2
            )

            #for overall grade status
            if total_absences >= 4:
                failed_due_to_absences = True
            elif midterm_grade >= 70 and finals_grade >= 94:
                passed_deanslister = True
            elif midterm_grade <= 50 and finals_grade <= 90:
                 failed_requirements_not_met = True
            else:
                passed = True

        except ValueError as e:
            error = str(e)  
    
    return render_template_string(
        html_template,
        prelim_grade=prelim_grade,
        midterm_grade=midterm_grade,
        finals_grade=finals_grade,
        overall_grade=overall_grade,
        failed_due_to_absences=failed_due_to_absences,
        error=error,passed_deanslister=passed_deanslister,
        failed_requirements_not_met=failed_requirements_not_met,
        passed=passed)

if __name__ == "__main__":
    app.run(debug=True)
