// projeto_arquivos.js — extraído de templates/projeto/projeto_arquivos.html

// Menus
function toggleCompanyMenu() { document.getElementById("companyMenu").classList.toggle("show"); }
function toggleUserMenu() { document.getElementById("userMenu").classList.toggle("show"); }
window.addEventListener("click", function(e) {
    const userMenu = document.getElementById("userMenu"); const userBtn = document.querySelector(".user-toggle");
    if (userMenu && userBtn && !userMenu.contains(e.target) && !userBtn.contains(e.target)) userMenu.classList.remove("show");
    const compMenu = document.getElementById("companyMenu"); const compBtn = document.querySelector(".company-toggle");
    if (compMenu && compBtn && !compMenu.contains(e.target) && !compBtn.contains(e.target)) compMenu.classList.remove("show");
});

let arquivosGlobais = [];
let arquivoParaDeletarId = null;

document.addEventListener("DOMContentLoaded", async () => { await carregarArquivos(); });

async function carregarArquivos() {
    try {
        const response = await fetch(`http://localhost:5001/api/projetos/1/artefatos`);
        const data = await response.json();
        if (data.artefatos) {
            arquivosGlobais = data.artefatos;
            aplicarFiltroERenderizar();
        }
    } catch (error) { document.getElementById('dynamic-files-container').innerHTML = "<p>Erro ao carregar dados.</p>"; }
}

document.getElementById('select-filtro').addEventListener('change', aplicarFiltroERenderizar);
document.getElementById('input-pesquisa').addEventListener('input', aplicarFiltroERenderizar);

function aplicarFiltroERenderizar() {
    const valorSelect = document.getElementById('select-filtro').value;
    const termoPesquisa = document.getElementById('input-pesquisa').value.toLowerCase();

    let arquivosFiltrados = arquivosGlobais.filter(arq => {
        const nomeMatch = arq.nome_arquivo.toLowerCase().includes(termoPesquisa);
        const tagMatch = arq.tags.some(t => t.toLowerCase().includes(termoPesquisa));
        return nomeMatch || tagMatch;
    });

    if(valorSelect === 'recentes') arquivosFiltrados.sort((a,b) => new Date(b.data_upload) - new Date(a.data_upload));
    else if(valorSelect === 'antigos') arquivosFiltrados.sort((a,b) => new Date(a.data_upload) - new Date(b.data_upload));
    else if(valorSelect === 'az') arquivosFiltrados.sort((a,b) => a.nome_arquivo.localeCompare(b.nome_arquivo));
    else if(valorSelect === 'za') arquivosFiltrados.sort((a,b) => b.nome_arquivo.localeCompare(a.nome_arquivo));

    renderizarLista(arquivosFiltrados);
}

function renderizarLista(listaParaRenderizar) {
    const container = document.getElementById('dynamic-files-container');
    container.innerHTML = "";

    if(listaParaRenderizar.length === 0) {
        container.innerHTML = "<p style='color:#6b7280; padding: 20px 0;'>Nenhum documento encontrado.</p>";
        return;
    }

    listaParaRenderizar.forEach(arq => {
        const dataFormatada = new Date(arq.data_upload).toLocaleDateString('pt-BR');
        const tagsHtml = arq.tags.map(t => {
            let style = "";
            if (t.toLowerCase() === "upload") style = "background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe;";
            else if (t.toLowerCase().includes("repositório")) style = "background: #fce7f3; color: #9d174d; border: 1px solid #fbcfe8;";
            return `<span class="file-ai-tag" style="${style}">${t}</span>`;
        }).join(" ");

        // O evento onClick no item inteiro chama o Preview. O onclick do botão deletar usa event.stopPropagation() para não abrir o preview.
        const cardHtml = `
        <div class="file-item" onclick="abrirPreview(${arq.id})">
            <div class="file-icon-box"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg></div>
            <div class="file-info">
                <div class="file-name-row">
                    <span class="file-name">${arq.nome_arquivo}</span>
                    <span class="file-ai-tag" style="background:#f3f4f6; color:#374151;">✧ ${arq.tipo || "Não Classificado"}</span>
                </div>
                <div class="file-meta" style="margin-top: 6px; display:flex; gap:6px; flex-wrap:wrap; align-items:center;">${tagsHtml} &bull; ${dataFormatada}</div>
            </div>
            <div class="file-status-ok">Processado</div>
            <button class="file-delete" title="Remover" onclick="event.stopPropagation(); abrirModal(${arq.id}, '${arq.nome_arquivo}')"><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg></button>
        </div>`;
        container.innerHTML += cardHtml;
    });
}

// LOGICA DO SMART PREVIEW
const previewModal = document.getElementById('previewModal');
function abrirPreview(id) {
    const arquivo = arquivosGlobais.find(a => a.id === id);
    if(arquivo) {
        document.getElementById('prevName').innerText = arquivo.nome_arquivo;
        document.getElementById('prevType').innerText = arquivo.tipo || "Não Classificado";
        document.getElementById('prevDate').innerText = new Date(arquivo.data_upload).toLocaleDateString('pt-BR');
        document.getElementById('prevSummary').innerText = arquivo.resumo || "Resumo não gerado.";

        document.getElementById('prevTags').innerHTML = arquivo.tags.map(t => {
            let style = "background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 99px; font-size: 12px; font-weight: 500;";
            if (t.toLowerCase() === "upload") style = "background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 99px; font-size: 12px; font-weight: 500;";
            return `<span style="${style}">${t}</span>`;
        }).join("");

        previewModal.style.display = 'flex';
    }
}
function fecharPreview() { previewModal.style.display = 'none'; }

// LOGICA DO MODAL DE DELETAR
const modal = document.getElementById('deleteModal');
const chkConfirm = document.getElementById('chkConfirmDelete');
const btnConfirmDelete = document.getElementById('btnConfirmDelete');

function abrirModal(id, nome) {
    arquivoParaDeletarId = id; document.getElementById('modalFileName').innerText = nome;
    chkConfirm.checked = false; btnConfirmDelete.disabled = true; btnConfirmDelete.classList.remove('ativo');
    modal.style.display = 'flex';
}
function fecharModal() { modal.style.display = 'none'; arquivoParaDeletarId = null; }

chkConfirm.addEventListener('change', (e) => {
    btnConfirmDelete.disabled = !e.target.checked;
    e.target.checked ? btnConfirmDelete.classList.add('ativo') : btnConfirmDelete.classList.remove('ativo');
});

btnConfirmDelete.addEventListener('click', async () => {
    if(!arquivoParaDeletarId) return;
    btnConfirmDelete.innerText = "Deletando...";
    try {
        const res = await fetch(`http://localhost:5001/api/artefatos/${arquivoParaDeletarId}`, { method: 'DELETE' });
        if(res.ok) { fecharModal(); await carregarArquivos(); btnConfirmDelete.innerText = "Deletar Arquivo"; }
    } catch (e) { alert("Erro de rede."); }
});
