document.addEventListener( 'DOMContentLoaded', function() {
    const form = document.getElementById("ISBN-Form");
    form.addEventListener("submit", (evento) => {
        evento.preventDefault();
        const isbn = document.getElementById("SearchISBN").value;
        console.log(isbn);
        fetch(`/buscar_js/`, 
            {method: "POST",
            headers: {"Content-Type": "application/json",
                "X-CSRFToken": getCookie('csrftoken')
            },
            body: JSON.stringify({SearchISBN: isbn})
            }
    
        ).then(response => response.json()).then(data => {
            const container = this.getElementById("Resultados");
            container.innerHTML = " ";
            if (!data.exito) {
                container.innerHTML = `<p>No se encontraron resultados</p>
                <a href="/agregar_manualmente/">Agregar Manualmente?</a>`;
                return;
            }
            if (data.length ===0) {
                alert("No se encontraron resultados.")
            } else {
                console.log(data);
                data.resultados.forEach((libro, index) => {
                const div = document.createElement('div');
                div.classList.add("Libro");
                div.innerHTML = 
                `<h2>${libro.titulo}</h2>
                <p><strong>Autor: </strong>${libro.autor}</p>
                <p><strong>Año de publicación:</strong>${libro.año}</p>
                <p>ISBN: ${libro.isbn}</p>
                <button id="botónConfirmar-${index}" href="{% url 'agregar_libro' %}">Agregar</button>`;
                container.appendChild(div)

                document.getElementById(`botónConfirmar-${index}`).addEventListener("click", () => {
                    fetch(`/confirmar_libro/${index}`, {
                        method: "POST",
                        headers: {"Content-Type": "application/json",
                            "X-CSRFToken": getCookie('csrftoken'),
                    
                        },
                        body: JSON.stringify()

                    }).then( () => {
                        window.location.href = `/confirmar_libro/${index}/`
                    });

                })
            });

            }
            
            

            
        }).catch(error => console.log(error))
        
    });
    function getCookie(name){
            let cookieV = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';')
                for (let i = 0; i < cookies.length; i++){
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === 'name' + '=') {
                        cookieV = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }

            }
            return cookieV;

        };

    

    
});    

