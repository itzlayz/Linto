/*
    █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
    █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
    https://t.me/itzlayz
                            
    🔒 Licensed under the GNU AGPLv3
    https://www.gnu.org/licenses/agpl-3.0.html 
*/

function redirect() {
    let cur = window.location.href;

    let newURL = cur.replace(/\/[^\/]*$/, "");
    window.location.href = newURL;
}

fetch("/authorize", {
    method: "POST",
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        "linto": localStorage.getItem("linto")
    })
})
    .then(response => {
        if (response.status !== 401) {
            redirect()
        }
    })
    .catch(error => console.error(error));

async function login() {
    try {
        const password = document.getElementById("password").value;
        const response = await fetch(
            "/authorize",
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ "linto": password })
            }
        );

        if (response.status !== 401) {
            localStorage.setItem("linto", password);
            
            redirect()
        } else {
            throw new Error("Invalid password");
        }
    } catch (error) {
        document.getElementById("response").innerText = error.message;
    }
}
