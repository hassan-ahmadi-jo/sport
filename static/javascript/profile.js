const profileSidebarBtnEls = document.querySelectorAll('.js-profile-sidebar-btn');

if (window.innerWidth < 1024) {
    document.getElementById('profile-content-area').scrollIntoView({ behavior: 'smooth', block: 'start' });
}


// selected profile sidebar btn
profileSidebarBtnEls.forEach(btn => {
    btn.addEventListener('click', function (){
        if (btn.className.includes('profile-sidebar-btn-normal-mode')) {
            const selectedBtn = document.querySelector('.profile-sidebar-btn-selected-mode');
            selectedBtn.classList.replace('profile-sidebar-btn-selected-mode', 'profile-sidebar-btn-normal-mode');
            btn.classList.replace('profile-sidebar-btn-normal-mode', 'profile-sidebar-btn-selected-mode');
        }
    });
});


