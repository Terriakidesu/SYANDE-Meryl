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
document.querySelector('form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);


    fetch(e.target.action,
        {
            method: "POST",
            body: formData
        }
    ).then(res => {
        return res.json()
    }).then(data => {

        if (data.success) window.location = "/";
        else {
            showErrorToast(data.message);
        };

    }).catch(error => {
        showErrorToast(`${error}`)
    });


});
