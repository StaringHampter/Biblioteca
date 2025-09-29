document.addEventListener('DOMContentLoaded', function () {
    const btn = document.getElementById("editBtn");

    btn.addEventListener('click', (event) => {
        event.preventDefault(); 

        const id = btn.getAttribute("data-libro-id");

        fetch(`/modificar/${id}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify({
                "titulo": document.getElementById("titulo").value,
                "autor": document.getElementById("autor").value,
                "año": document.getElementById("año").value,
                "isbn": document.getElementById("isbn").value,
                "link": document.getElementById("link").value,
                "cantidad": document.getElementById("cantidad").value,
                "estante": document.getElementById("estante").value,
                "estanteria": document.getElementById("estanteria").value
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            alert(data.mensaje || "Libro modificado con éxito.");
        })
        .catch(error => {
		console.error(error);
		alert(data.mensaje || "Hubo un error. Puede que un campo esté vacío.")

	});
    });
});

function getCookie(name) {
    let cookieV = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieV = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieV; 
}
