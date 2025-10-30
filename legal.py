# legal.py
def get_footer_js():
    return """
    <script>
    setTimeout(() => {
      const footer = document.createElement('div');
      footer.style.cssText = 'text-align:center; font-size:11px; color:#888; margin:20px 0; line-height:1.4;';
      footer.innerHTML = `
        <strong>Sistema Privado</strong> • Solo para personal y clientes de
        <strong>Hogar Familiar Inmobiliaria</strong> (CIF B-01755321).<br>
        <a href="/public/legal.html" target="_blank" style="color:#1a73e8;">Ver términos legales</a>
      `;
      document.querySelector('.main').appendChild(footer);
    }, 500);
    </script>
    """
