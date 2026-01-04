let resend_interval;

document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordInput = document.getElementById('password');
    const icon = this.children[0];

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        passwordInput.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
});



// Form submission
document.querySelector('form#email-form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const email = formData.get('email');

    fetch(
        "/api/auth/verify_email",
        {
            method: "POST",
            body: formData
        }
    ).then(res => {
        return res.json();
    }).then(data => {
        if (data.success) {

            fetch("/api/auth/request_otp",
                {
                    method: "POST",
                    body: formData
                }
            ).then(res => {
                return res.json();
            }).then(data => {

                do_resend_timer();
                update_tabs("OTP");

                if (data.success) {
                    let otp_form = document.querySelector("form#otp-form");
                    let email_form = document.querySelector("form#email-form");

                    otp_form.querySelector("#email-span").textContent = email;

                    email_form.animate(
                        [
                            { opacity: 1 },
                            { opacity: 0 }
                        ],
                        {
                            easing: "ease-out",
                            duration: 300
                        }
                    ).addEventListener("finish", function () {
                        email_form.style.display = "none";
                        otp_form.style.display = "block";
                    });

                } else {
                    console.error(data);
                }

            });


        } else {
            console.error(data);
        }
    })



});

document.querySelector("form#otp-form").addEventListener("submit", function (e) {
    e.preventDefault();
    let formData = new FormData(this);

    fetch("/api/auth/verify_otp",
        {
            method: "POST",
            body: formData
        }
    ).then(res => {
        return res.json();
    }).then(data => {
        if (data.success) {
            console.log(data)
        } else {
            console.error(data);
        }
    });

});

document.querySelector("form#register-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const emailFormData = new FormData(email_form);

    Object.entries(emailFormData).forEach(entry => {

        let name = entry[0];
        let value = entry[1];
        formData.append(name, value);
    });

    fetch("/api/auth/verify_otp",
        {
            method: "POST",
            body: formData
        }
    ).then(res => {
        return res.json();
    }).then(data => {
        if (data.success) {
            console.log(data)
        } else {
            console.error(data);
        }
    });

});

document.querySelector("button#back-button").addEventListener("click", () => {
    let otp_form = document.querySelector("form#otp-form");
    let email_form = document.querySelector("form#email-form");

    update_tabs("Details");

    otp_form.querySelector("#email-span").textContent = "johndoe@email.com";
    otp_form.animate(
        [
            { opacity: 1 },
            { opacity: 0 }
        ],
        {
            easing: "ease-out",
            duration: 300
        }
    ).addEventListener("finish", function () {
        otp_form.style.display = "none";
        email_form.style.display = "block";

    });
});


let resend_code_btn = document.querySelector("button#resend_code");
resend_code_btn.addEventListener("click", function (event) {
    event.preventDefault();


    if (resend_interval !== undefined) {
        return;
    }

    let register_form = document.querySelector("form#register-form");
    const formData = new FormData(register_form);
    formData.append("request_new", true);

    fetch("/api/auth/request_otp",
        { method: "POST", body: formData }
    ).then(res => {
        return res.json();
    }).then(data => {
        if (data.success) console.log(data);
        else console.error(data);
    })

    do_resend_timer();
});

function do_resend_timer() {
    let resend_code_btn = document.querySelector("button#resend_code");
    let span = resend_code_btn.querySelector("span");

    span.textContent = "00:30";

    let start = new Date().getTime();

    resend_interval = setInterval(
        () => {
            let now = new Date().getTime();

            let elapsed_time = now - start;

            let display_time = `${30 - Math.floor(elapsed_time / 1000)}`

            span.textContent = `00:${display_time.padStart(2, "0")}`;

            if (elapsed_time > 30000) {
                clearInterval(resend_interval);
                resend_interval = undefined;
                span.textContent = "Resend Code";
            }
        },
        1000,
    );
}

function update_tabs(tab_name) {
    let progress_container = document.querySelector("div#progress-container");
    let tabs = progress_container.querySelectorAll("div.progress-label");
    let x = 0;

    switch (tab_name) {
        case "Details":
            x = 0;
            break;
        case "OTP":
            x = 1;
            break;
        case "Done":
            x = 2;
            break;
        default:
            return;
    }

    for (let i = 0; i < tabs.length; i++) {
        let tab = tabs[i];

        if (tab.classList.contains("progress-label-done")) {
            tab.classList.remove("progress-label-done");
        }

        if (tab.classList.contains("progress-label-active")) {
            tab.classList.remove("progress-label-active");
        }

        if (i <= x) {
            tab.classList.add("progress-label-done");
        }

        if (i == x) {
            tab.classList.add("progress-label-active");
        }

    }

}