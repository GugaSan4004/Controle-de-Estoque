
window.onload = () => {
    form = document.querySelector("form")
    btn = document.querySelector("button")
    
    form.addEventListener("submit", async (e) => {
        btn.disabled = true
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
    });
}