document.addEventListener('DOMContentLoaded', function() {
    // Pegamos o botão pelo ID
    const botao = document.getElementById('open_sideBar');
    
    // Pegamos a sidebar pelo ID
    const sidebar = document.getElementById('sidebar');

    // Verificação de segurança (caso o elemento não exista)
    if(botao && sidebar) {
        botao.addEventListener('click', function () {
            sidebar.classList.toggle('open_sideBar');
        });
    } else {
        console.error("Elementos não encontrados! Verifique os IDs no HTML.");
    }
});