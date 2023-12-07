async function unloadModule(cog) {
    try {
        await fetch('/unload', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cog }),
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
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
        });
        
        let evalresp = await response.text();
        evalResponse.innerText = evalresp;
    } catch (error) {
        console.error('Error during eval:', error);
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
        memory.innerText = `🧠 RAM: ±${data.memory}%`;
    } catch (error) {
        console.error('Error during updating consuming:', error);
    }
}
