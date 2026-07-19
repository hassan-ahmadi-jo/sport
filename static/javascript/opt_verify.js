const otpRetryRemainingSecondsEl = document.getElementById('otp-retry-remaining-seconds');
const otpResendRemainingSecondsEl = document.getElementById('otp-resend-remaining-seconds');
const otpResendBtnEl = document.getElementById('otp-resend-btn')
const otpResendCountdownEl = document.getElementById('otp-resend-countdown');
const otpResendCountdownContainerEl = document.getElementById('otp-resend-countdown-container');


let resendRemainingTime = Math.max(parseInt(otpRetryRemainingSecondsEl.textContent, 10), parseInt(otpResendRemainingSecondsEl.textContent, 10));

const updateResendButtonState = function (remainTime) {
    if (remainTime > 0) {
        otpResendCountdownContainerEl.classList.remove('hidden');
        otpResendBtnEl.disabled = true;
    } else {
        otpResendCountdownContainerEl.classList.add('hidden');
        otpResendBtnEl.disabled = false;
    }
}

function generateRemainingTimeText(totalSeconds) {
    const seconds = Math.floor(totalSeconds % 60);
    const minutes = Math.floor(((totalSeconds - seconds) / 60) % 60);
    const hours = Math.floor((totalSeconds - 60 * minutes - seconds) / 3600);

    let hoursText = '';
    let minutesText = '';
    let secondsText = '';

    if (hours === 1) {
        hoursText = 'یک ساعت';
    } else if (hours > 1) {
        hoursText = `${hours} ساعت`;
    }
    
    if (hours > 0 && minutes > 0) {
        hoursText += ' و ';
    }

    if (minutes === 1) {
        minutesText = 'یک دقیقه';
    } else if (minutes > 1) {
        minutesText = `${minutes} دقیقه`;
    }
    
    if (seconds > 0 && minutes > 0 && hours === 0) {
        minutesText += ' و ';
    }

    if (seconds > 0 && hours === 0) {
        if (seconds === 1) {
            secondsText = 'یک ثانیه';
        } else {
            secondsText = `${seconds} ثانیه`;
        }
    }

    return hoursText + minutesText + secondsText;
}

const timer = setInterval(function () {
    resendRemainingTime -= 1;
    otpResendCountdownEl.textContent = generateRemainingTimeText(resendRemainingTime);
    if (resendRemainingTime <= 0) {
        updateResendButtonState(-1);
        clearInterval(timer);
    } 
}, 1000);

updateResendButtonState(resendRemainingTime);


