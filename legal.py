import chainlit as cl

def get_footer_js():
    """
    Genera un elemento de JavaScript para inyectar un footer legal
    en la interfaz de Chainlit.
    """
    # Lee el contenido del HTML para el aviso legal
    try:
        with open("legal.html", "r", encoding="utf-8") as f:
            legal_html = f.read().replace("\n", "").replace("'", "\\'")
    except FileNotFoundError:
        legal_html = "<p>Error: No se encontró el archivo legal.html</p>"

    # Script para crear y mostrar el footer
    js_script = f"""
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Crear el botón o enlace del footer
            const footerLink = document.createElement('a');
            footerLink.innerText = 'Información Legal y de Privacidad';
            footerLink.href = '#';
            footerLink.style.textDecoration = 'underline';
            footerLink.style.cursor = 'pointer';
            footerLink.style.color = '#888';
            footerLink.style.fontSize = '12px';

            // Crear el contenedor del footer
            const footerContainer = document.createElement('div');
            footerContainer.style.textAlign = 'center';
            footerContainer.style.padding = '10px';
            footerContainer.style.borderTop = '1px solid #eee';
            footerContainer.style.marginTop = '20px';
            footerContainer.appendChild(footerLink);

            // Añadir el footer al final del contenedor principal del chat
            const mainContainer = document.querySelector('.MuiDrawer-root + div');
            if (mainContainer) {{
                mainContainer.appendChild(footerContainer);
            }}

            // Crear el modal
            const modal = document.createElement('div');
            modal.id = 'legalModal';
            modal.style.display = 'none';
            modal.style.position = 'fixed';
            modal.style.zIndex = '1000';
            modal.style.left = '0';
            modal.style.top = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.overflow = 'auto';
            modal.style.backgroundColor = 'rgba(0,0,0,0.5)';

            const modalContent = document.createElement('div');
            modalContent.style.backgroundColor = '#fefefe';
            modalContent.style.margin = '10% auto';
            modalContent.style.padding = '20px';
            modalContent.style.border = '1px solid #888';
            modalContent.style.width = '80%';
            modalContent.style.maxWidth = '800px';
            modalContent.style.borderRadius = '8px';
            modalContent.innerHTML = `{legal_html} <br><button id="closeModal">Cerrar</button>`;

            modal.appendChild(modalContent);
            document.body.appendChild(modal);

            // Eventos para abrir y cerrar el modal
            footerLink.onclick = function(e) {{
                e.preventDefault();
                modal.style.display = 'block';
            }};

            document.getElementById('closeModal').onclick = function() {{
                modal.style.display = 'none';
            }};

            window.onclick = function(event) {{
                if (event.target == modal) {{
                    modal.style.display = 'none';
                }}
            }};
        }});
    </script>
    """

    return cl.Message(content="", author="System", elements=[cl.Text(content=js_script, name="footer_script", display="inline")])
