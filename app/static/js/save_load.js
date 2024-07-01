function download_schedule() {
    var render_info = JSON.parse(document.getElementById("render_info").value);
    let course_schedule = document.getElementById("course_schedule").value;

    // update course_schedule since courses can be moved around by user
    render_info['course_schedule'] = course_schedule;
    render_info['course_schedule_display'] = JSON.parse(course_schedule);

    render_info = JSON.stringify(render_info);
    
    var filename = "course_schedule.txt";
 
    //creating an invisible element for creating a download file
    var element = document.createElement('a');
    element.setAttribute('href',
        'data:text/plain;charset=utf-8, '
        + encodeURIComponent(render_info));
    element.setAttribute('download', filename);
    document.body.appendChild(element);
    element.click();

    document.body.removeChild(element);
}