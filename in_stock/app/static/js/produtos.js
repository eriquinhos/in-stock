document.addEventListener('DOMContentLoaded', function() {
    
    // 1. DADOS ORIGINAIS (MOCK)
    const products = [
        { codigo: 'PROD001', descricao: 'Café Premium 500g', categoria: 'Alimentos', vencimento: '30/12/2025', qtd: 50, preco: 25.90 },
        { codigo: 'PROD002', descricao: 'Açúcar Cristal 1kg', categoria: 'Alimentos', vencimento: '14/06/2026', qtd: 100, preco: 5.50 },
        { codigo: 'ELE005', descricao: 'Mouse Gamer RGB', categoria: 'Eletrônicos', vencimento: 'Indeterminado', qtd: 12, preco: 125.00 },
        { codigo: 'MOV003', descricao: 'Cadeira de Escritório', categoria: 'Móveis', vencimento: 'Indeterminado', qtd: 5, preco: 450.00 }
    ];

    // Variável que guarda o que está sendo exibido no momento (começa com tudo)
    let dadosAtuais = [...products];

    const tbody = document.getElementById('products_table_body');
    const searchInput = document.getElementById('searchInput');
    const btnExport = document.getElementById('btnExport');

    // --- FUNÇÃO DE RENDERIZAR ---
    function renderTable(data) {
        tbody.innerHTML = ''; 
        
        if(data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding:20px;">Nenhum item encontrado.</td></tr>';
            return;
        }

        data.forEach(product => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight: 600;">${product.codigo}</td>
                <td>${product.descricao}</td>
                <td>${product.categoria}</td>
                <td>${product.vencimento}</td>
                <td style="text-align: center;">${product.qtd}</td>
                <td>R$ ${product.preco.toFixed(2)}</td>
                <td style="text-align: center;">
                    <button class="action-btn"><i class="fa-solid fa-eye"></i></button>
                    <button class="action-btn"><i class="fa-solid fa-pen"></i></button>
                    <button class="action-btn delete"><i class="fa-solid fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // --- FILTRO (BUSCA) ---
    if(searchInput){
        searchInput.addEventListener('input', (e) => {
            const termo = e.target.value.toLowerCase();
            
            // Atualiza a variável global 'dadosAtuais' com o resultado do filtro
            dadosAtuais = products.filter(p => 
                p.descricao.toLowerCase().includes(termo) || 
                p.codigo.toLowerCase().includes(termo) ||
                p.categoria.toLowerCase().includes(termo)
            );
            
            renderTable(dadosAtuais);
        });
    }

    // --- FUNÇÃO EXPORTAR PARA EXCEL (XLSX COM TABELA) ---
    if(btnExport) {
        btnExport.addEventListener('click', async () => {
            if(dadosAtuais.length === 0) {
                alert("Não há dados para exportar!");
                return;
            }

            // 1. Cria um novo Workbook (Livro Excel)
            const workbook = new ExcelJS.Workbook();
            const worksheet = workbook.addWorksheet('Produtos');

            // 2. Prepara os dados para o formato da tabela
            // Transformamos a lista de objetos em lista de valores (Array de Arrays)
            const rows = dadosAtuais.map(item => {
                return [
                    item.codigo,
                    item.descricao,
                    item.categoria,
                    item.vencimento,
                    item.qtd,
                    item.preco // Passamos o número puro para o Excel formatar depois
                ];
            });

            // 3. Adiciona a Tabela com formatação automática
            worksheet.addTable({
                name: 'TabelaProdutos',
                ref: 'A1', // Começa na célula A1
                headerRow: true,
                totalsRow: false,
                style: {
                    theme: 'TableStyleMedium2', // Tema Azul/Cinza padrão do Excel (bonito)
                    showRowStripes: true,
                },
                columns: [
                    { name: 'Código', filterButton: true },
                    { name: 'Descrição', filterButton: true },
                    { name: 'Categoria', filterButton: true },
                    { name: 'Vencimento', filterButton: true },
                    { name: 'Quantidade', filterButton: true },
                    { name: 'Preço', filterButton: true }
                ],
                rows: rows,
            });

            // 4. Ajustes de Largura das Colunas (Para ficar legível)
            worksheet.columns.forEach((column, i) => {
                // Larguras manuais aproximadas para cada coluna
                const widths = [15, 35, 20, 15, 12, 15]; 
                column.width = widths[i];
            });

            // 5. Formatar a coluna de Preço (Coluna F) como Moeda (R$)
            // A coluna F é a 6ª coluna
            worksheet.getColumn(6).numFmt = '"R$" #,##0.00';
            worksheet.getColumn(5).alignment = { horizontal: 'center' }; // Centraliza Qtd

            // 6. Gerar e Baixar o arquivo
            const buffer = await workbook.xlsx.writeBuffer();
            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            saveAs(blob, 'Relatorio_Produtos_InStock.xlsx');
        });
    }
// ... (Seu código existente da tabela e exportação continua aqui) ...

    // --- LÓGICA DO MODAL (POP-UP) ---
    
    const modal = document.getElementById('modalCadastro');
    const btnNovoItem = document.getElementById('btnNovoItem');
    const btnFecharX = document.getElementById('btnFecharX');
    const btnCancelarModal = document.getElementById('btnCancelarModal');

    // --- EVENTOS DO MODAL ---

    // 1. Abrir Modal
    if(btnNovoItem) {
        btnNovoItem.addEventListener('click', () => {
            modal.classList.add('show');
        });
    }

    // Função apenas para fechar visualmente
    function fecharModal() {
        modal.classList.remove('show');
    }

    // 2. Botão "X" (Apenas fecha)
    if(btnFecharX) btnFecharX.addEventListener('click', fecharModal);

    // 3. Botão "Cancelar" (LIMPA E FECHA)
    if(btnCancelarModal) {
        btnCancelarModal.addEventListener('click', () => {
            // Pega o formulário e limpa todos os campos
            document.getElementById('formCadastro').reset(); 
            fecharModal();
        });
    }

    // 4. Clicar fora fecha (Opcional: se quiser que limpe ao clicar fora, adicione o reset aqui também)
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            fecharModal();
        }
    });

    // 5. Ao Enviar (Simulação de Sucesso)
    document.getElementById('formCadastro').addEventListener('submit', (e) => {
        e.preventDefault();
        alert("Produto criado com sucesso!");
        
        // Também é bom limpar quando dá certo!
        e.target.reset(); 
        fecharModal();
    });
    // --- NOTIFICAÇÕES (MANTIDO) ---
    const notifBtn = document.getElementById('notifBtn');
    const notifDropdown = document.getElementById('notifDropdown');
    if(notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            notifDropdown.classList.toggle('show');
        });
        document.addEventListener('click', (e) => {
            if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
                notifDropdown.classList.remove('show');
            }
        });
    }

    // Inicializa
    renderTable(products);
});