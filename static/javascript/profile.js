const profileSidebarBtnEls = document.querySelectorAll('.js-profile-sidebar-btn');
const profileContentAreaEl = document.getElementById('profile-content-area');


const setProfileSidebarBtnClassList = function(btn) {
    const activatedBtn = document.querySelector('.profile-sidebar-btn-selected-mode');
    
        if (activatedBtn == btn) return;
        if (activatedBtn) {
            activatedBtn.classList.replace('profile-sidebar-btn-selected-mode', 'profile-sidebar-btn-normal-mode');
        }
        btn.classList.replace('profile-sidebar-btn-normal-mode', 'profile-sidebar-btn-selected-mode');
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
        if (btn.className.includes('profile-sidebar-btn-normal-mode')) {
            setProfileSidebarBtnClassList(btn);
            getProfileContentData(btn)};
    });
});



profileContentAreaEl.addEventListener('submit', async function(event) {
    const formEl = event.target.closest('.js-ajax-form');

    if (!formEl) return;

    event.preventDefault();

    const formData = new FormData(formEl);
    const csrfToken = profileContentAreaEl.querySelector('[name=csrfmiddlewaretoken]').value;
    const url = formEl.action;

    try {
        const response = await fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
                'X-Requested-With': 'XMLHttpRequest',
                "X-CSRFToken": csrfToken
            }
    });

    const wasSuccessful = response.ok && response.redirected;
    
    const html = await response.text();
    profileContentAreaEl.innerHTML = html;

    if (wasSuccessful) {
            alert('اطلاعات پروفایل با موفقیت ذخیره شد.');
        }

    } catch (error) {
        console.error(error);
        alert('خطا در ارسال فرم');
    };
});


