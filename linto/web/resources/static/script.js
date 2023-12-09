/*
    █ ▀█▀ ▀█ █   ▄▀█ █▄█ ▀█
    █ ░█░ █▄ █▄▄ █▀█ ░█░ █▄
    https://t.me/itzlayz
                            
    🔒 Licensed under the GNU AGPLv3
    https://www.gnu.org/licenses/agpl-3.0.html 
*/

async function unloadModule(cog) {
    try {
        await fetch('/unload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ "cog": cog, "linto": localStorage.getItem("linto") }),
        });
    } catch (error) {
        console.error('Error during module unloading:', error);
    }
}

async function discordEval() {    
    try {
        const code = document.getElementById("evalText").value;
        const evalResponse = document.getElementById("evalResponse");
        const response = await fetch('/eval', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ "code": code, "linto": localStorage.getItem("linto") }),
        });
        
        let evalresp = await response.text();
        evalResponse.innerText = evalresp;
    } catch (error) {
        console.error('Error during eval:', error);
    }
}

async function reloadLinto() {
    try {
        await fetch('/restart', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                {"linto": localStorage.getItem("linto")}
            )
        });
        location.reload();
    } catch (error) {
        console.error("Error during restarting:", error);
    }
}

async function changePassword() {
    const password = document.getElementById("chpassword").value;
    const resp = document.getElementById("passresp");
    if (password.length < 5) {
        resp.innerText = "The password must be at least 5 characters long";
        return
    }

    try {
        await fetch('/chpass', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(
                {"password": password, "curpassword": localStorage.getItem("linto")}
            )
        });
        location.replace(location.href + "login")
    } catch (error) {
        console.error('Error during changing password:', error);
    }
}


function toggleBlock(id) {
    const moduleBlock = document.getElementById(id);
    const btn = document.querySelector(`button[data-id="${id}"]`);

    moduleBlock.style.display = (moduleBlock.style.display === 'none') ? 'block' : 'none';
    if (btn)
    {
        btn.innerHTML = (moduleBlock.style.display === 'none') ? `Open ${id}` : `Close ${id}`;
    }
}

async function updateCount() {
    try {
        const response = await fetch('/consuming', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const data = await response.json();
        let cpu = document.getElementById("cpu");
        let memory = document.getElementById("memory");

        cpu.innerText = `💽 CPU: ±${data.cpu}%`;
        memory.innerText = `🧠 RAM: ±${data.memory}MB`;
    } catch (error) {
        console.error('Error during updating consuming:', error);
    }
}
