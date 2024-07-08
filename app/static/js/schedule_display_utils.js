function has_completed_course(element) {
    const course_num = element.getAttribute("courseNum");
    const semester_num = element.getAttribute("semesterNum");
    let is_completed = element.getAttribute("is_completed");

    let course_schedule = JSON.parse(document.getElementById("course_schedule").value);


    course_schedule[semester_num].schedule.some((course) => {
        if (course.course === course_num) {
            if (is_completed === "false") {
                course["is_completed"] = true;
                element.className = "fa fa-check-circle"
                element.style.color = "green"
                element.title = "Course has been taken/passed."
                element.setAttribute("is_completed", "true")
            } else {
                course["is_completed"] = false;
                element.className = "fa fa-check-circle-o"
                element.style.color = "blue"
                element.title = "Course has not been completed."
                element.setAttribute("is_completed", "false")
            }
            return true;
        }
    });

    var render_info = JSON.parse(document.getElementById("render_info").value);

    // update course_schedule since courses can be moved around by user
    render_info['course_schedule'] = JSON.stringify(course_schedule);
    render_info['course_schedule_display'] = course_schedule;

    // update render_info in case a user saves after updating if course is completed or not
    document.getElementById("render_info").value = JSON.stringify(render_info);
    // update course schedule in order to save is_completed
    document.getElementById("course_schedule").value = JSON.stringify(course_schedule);
}