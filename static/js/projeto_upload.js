function toggleCompanyMenu() { document.getElementById("companyMenu").classList.toggle("show"); }
function toggleUserMenu() { document.getElementById("userMenu").classList.toggle("show"); }

window.addEventListener("click", function(e) {
    const userMenu = document.getElementById("userMenu");
    const userBtn = document.querySelector(".user-toggle");
    if (userMenu && userBtn && !userMenu.contains(e.target) && !userBtn.contains(e.target)) {
        userMenu.classList.remove("show");
    }
    const compMenu = document.getElementById("companyMenu");
    const compBtn = document.querySelector(".company-toggle");
    if (compMenu && compBtn && !compMenu.contains(e.target) && !compBtn.contains(e.target)) {
        compMenu.classList.remove("show");
    }
});

(function () {
    const fileInput    = document.getElementById('fileInput');
    const uploadZone   = document.getElementById('uploadZone');
    const metaSection  = document.getElementById('uploadMetaSection');
    const fileNameInput = document.getElementById('uploadFileName');
    const fileExtInput  = document.getElementById('uploadFileExt');
    const btnEnviar    = document.getElementById('btnEnviarBackEnd');
    const btnLimpar    = document.getElementById('btnLimpar');
    const statusText   = document.getElementById('uploadStatus');
    let arquivoReal = null;

    document.getElementById('btnSelect').addEventListener('click', (e) => { e.preventDefault(); fileInput.click(); });

    fileInput.addEventListener('change', function () {
        if (this.files && this.files[0]) {
            arquivoReal = this.files[0];
            handleFile(this.files[0].name);
        }
    });

    uploadZone.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadZone.style.borderColor = '#3154ff';
    });

    uploadZone.addEventListener('dragleave', function (e) {
        if (!uploadZone.contains(e.relatedTarget)) {
            uploadZone.style.borderColor = '#93c5fd';
        }
    });

    uploadZone.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadZone.style.borderColor = '#93c5fd';
        const files = e.dataTransfer.files;
        if (files && files[0]) {
            arquivoReal = files[0];
            handleFile(files[0].name);
        }
    });

    function handleFile(filename) {
        const lastDot = filename.lastIndexOf('.');
        fileNameInput.value = lastDot > 0 ? filename.substring(0, lastDot) : filename;
        fileExtInput.value  = lastDot > 0 ? filename.substring(lastDot) : '';
        metaSection.style.display = 'flex';
        statusText.innerText = "";
    }

    btnLimpar.addEventListener('click', function(e) {
        e.preventDefault();
        arquivoReal = null;
        fileInput.value = "";
        metaSection.style.display = 'none';
        statusText.innerText = "";
    });

    btnEnviar.addEventListener('click', async function() {
        if (!arquivoReal) return;

        await Sessao.pronto;

        const token = Sessao.getToken();
        if (!token) {
            statusText.innerText = "Erro: Token de autenticação não encontrado. Faça login novamente.";
            statusText.style.color = "#ef4444";
            return;
        }

        const formData = new FormData();
        formData.append("projeto_id", Sessao.getProjetoId());
        formData.append("documento", arquivoReal);

        statusText.innerText = "Enviando e processando na IA... Aguarde.";
        statusText.style.color = "#3b82f6";

        try {
            const response = await fetch(`${window.API.UPLOAD}/api/upload`, {
                method: "POST",
                headers: Sessao.getHeaders(false),
                body: formData
            });

            if (response.ok) {
                statusText.innerText = "Processado com sucesso!";
                statusText.style.color = "#16a34a";
                setTimeout(() => window.location.href = "/projeto/arquivos", 1500);
            } else {
                statusText.innerText = "Erro ao processar arquivo. Verifique o console.";
                statusText.style.color = "#ef4444";
            }
        } catch (error) {
            statusText.innerText = "Erro de conexão com o servidor de Ingestão.";
            statusText.style.color = "#ef4444";
        }
    });
})();
