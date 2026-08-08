const profileSidebarBtnEls = document.querySelectorAll('.js-profile-sidebar-btn');
const profileContentAreaEl = document.getElementById('profile-content-area');


const setProfileSidebarBtnClassList = function(btn) {
    if (btn.className.includes('profile-sidebar-btn-normal-mode')) {
            const selectedBtn = document.querySelector('.profile-sidebar-btn-selected-mode');

            if (selectedBtn == btn) return;
            if (selectedBtn) {
                selectedBtn.classList.replace('profile-sidebar-btn-selected-mode', 'profile-sidebar-btn-normal-mode');
            }
        btn.classList.replace('profile-sidebar-btn-normal-mode', 'profile-sidebar-btn-selected-mode')};
};

const getProfileContentData = async function(selected_btn) {
    const url = selected_btn.dataset.url;

    profileContentAreaEl.style.opacity = '0.5';
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Network response was not ok');

        const html = await response.text();
        profileContentAreaEl.innerHTML = html;

        if (window.innerWidth < 1024) {
            document.getElementById('profile-content-area').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    } catch (error) {
        console.error('Fetch error:', error);
        profileContentAreaEl.innerHTML = '<p class="text-rose-500 p-4 text-center">خطا در بارگذاری اطلاعات. دوباره تلاش کنید.</p>';
    } finally {
        profileContentAreaEl.style.opacity = '1';
    } 
};

// selected profile sidebar btn
profileSidebarBtnEls.forEach(btn => {
    btn.addEventListener('click', function (e){
        e.preventDefault();

        setProfileSidebarBtnClassList(btn);
        getProfileContentData(btn);
    });
});


