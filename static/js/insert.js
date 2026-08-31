window.onload = () => {
    const form = document.querySelector("form")
    const btn = document.querySelector("button")
    const select = document.querySelector("select")

    select.addEventListener("change", (e) => {
        if (event.target.value === 'RECEIVE') {
            document.getElementById('note-id').hidden = false
        } else { 
            document.getElementById('note-id').hidden = true
        }
    })
    
    form.addEventListener("submit", async (e) => {
        btn.disabled = true
        btn.classList.remove("bg-green-800", "cursor-pointer")
        btn.classList.add("bg-gray-800", "cursor-pointer")
        btn.type = "button"

        e.preventDefault()

        let url = form.action;
        let method = form.method.toUpperCase();

        const formData = new FormData(form);

        const response = await fetch(url, {
            method,
            body: formData
        });

        const result = await response.json()

        alert(result.message)

        if (response.ok) {
            form.querySelectorAll('input:not([type="hidden"]), textarea').forEach(input => input.value = '');
        }

        btn.disabled = false
        btn.classList.remove("bg-gray-800", "cursor-pointer")
        btn.classList.add("bg-green-800", "cursor-pointer")
        btn.type = "submit"
    });
}