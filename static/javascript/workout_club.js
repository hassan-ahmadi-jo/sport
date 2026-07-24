const workoutDayBtnEls = document.querySelectorAll('.js-workout-day-btn');
const workoutContentAreaEl = document.getElementById('workout-content-area');
const workoutContentLoadingEl = document.getElementById('workout-content-loading');7
// workoutContentLoadingEl.classList.remove('hidden');



const setWorkoutBtnClassList = function (selected_btn) {
    workoutDayBtnEls.forEach(btn => {
        if (btn === selected_btn) {
            btn.classList.add('workout-day-btn-selected-mode');
            btn.classList.remove('workout-day-btn-normal-mode');
        } else {
            btn.classList.remove('workout-day-btn-selected-mode');
            btn.classList.add('workout-day-btn-normal-mode');
        }
    })
}

const getWorkoutDailyDetailData = function (btn) {
    setWorkoutBtnClassList(btn)
    url = btn.dataset.url
    workoutContentAreaEl.innerHTML = '';
    workoutContentLoadingEl.classList.remove('hidden');
    fetch(url).then(response => response.text())
        .then(html => {
            workoutContentAreaEl.innerHTML = html;
            workoutContentLoadingEl.classList.add('hidden');
        });
}

workoutDayBtnEls.forEach(btn => {
    btn.addEventListener('click', function () {
        getWorkoutDailyDetailData(btn)
    });
});

// getWorkoutDailyDetailData(workoutDayBtnEls[0]);
