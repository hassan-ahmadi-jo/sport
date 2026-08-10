const profileSidebarBtnEls = document.querySelectorAll('.js-profile-sidebar-btn');
const profileContentAreaEl = document.getElementById('profile-content-area');
const profileLodingEl = document.getElementById('profile-loading');


const setProfileSidebarBtnClassList = function (btn) {
    const activatedBtn = document.querySelector('.profile-sidebar-btn-selected-mode');

    if (activatedBtn == btn) return;
    if (activatedBtn) {
        activatedBtn.classList.replace('profile-sidebar-btn-selected-mode', 'profile-sidebar-btn-normal-mode');
    }
    btn.classList.replace('profile-sidebar-btn-normal-mode', 'profile-sidebar-btn-selected-mode');
};

const getProfileContentData = async function (selected_btn) {
    const url = selected_btn.dataset.url;

    profileContentAreaEl.classList.add('hidden');
    profileLodingEl.classList.remove('hidden')
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
        profileContentAreaEl.classList.remove('hidden');
        profileLodingEl.classList.add('hidden')
    }
};

// selected profile sidebar btn
profileSidebarBtnEls.forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        if (btn.className.includes('profile-sidebar-btn-normal-mode')) {
            setProfileSidebarBtnClassList(btn);
            getProfileContentData(btn)
        };
    });
});



profileContentAreaEl.addEventListener('submit', async function (event) {
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
            const formSuccessEl = profileContentAreaEl.querySelector('.js-form-success');
            if (formSuccessEl) {
                formSuccessEl.classList.replace('hidden', 'flex');
            } else {
                alert('تغییرات با موفقیت اعمال شد.');
            }

        }

    } catch (error) {
        console.error(error);
        alert('خطا در ارسال فرم');
    };
});



/**
 * مدیریت آکاردئون انیمیشنی فاکتورها در پروفایل
 * پشتیبانی کامل از بارگذاری AJAX
 */
document.addEventListener('click', function (e) {
    const toggleBtn = e.target.closest('.js-invoice-toggle');
    if (!toggleBtn) return;

    const card = toggleBtn.closest('.js-invoice-card');
    if (!card) return;

    const body = card.querySelector('.js-invoice-body');
    const arrow = card.querySelector('.js-invoice-arrow');

    // بررسی وضعیت فعلی
    const isOpen = card.classList.contains('is-open');

    // ۱. (اختیاری) بستن سایر فاکتورهای بازشده برای آکاردئون تک‌گزینه‌ای
    document.querySelectorAll('.js-invoice-card.is-open').forEach(openCard => {
        if (openCard !== card) {
            openCard.classList.remove('is-open');
            const openBody = openCard.querySelector('.js-invoice-body');
            const openArrow = openCard.querySelector('.js-invoice-arrow');
            if (openBody) openBody.style.gridTemplateRows = '0fr';
            if (openArrow) openArrow.style.transform = 'rotate(0deg)';
        }
    });

    // ۲. تغییر وضعیت کارت کلیک‌شده
    if (isOpen) {
        card.classList.remove('is-open');
        if (body) body.style.gridTemplateRows = '0fr';
        if (arrow) arrow.style.transform = 'rotate(0deg)';
    } else {
        card.classList.add('is-open');
        if (body) body.style.gridTemplateRows = '1fr';
        if (arrow) arrow.style.transform = 'rotate(180deg)';
    }
});


