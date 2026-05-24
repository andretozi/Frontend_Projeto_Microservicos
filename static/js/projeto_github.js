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
    const tipoPublico = document.getElementById('tipoPublico');
    const tipoPrivado = document.getElementById('tipoPrivado');
    const campoToken = document.getElementById('campoToken');
    const repoUrl = document.getElementById('repoUrl');
    const repoToken = document.getElementById('repoToken');
    const chkSincronizar = document.getElementById('chkSincronizar');
    const btnConectar = document.getElementById('btnConectar');
    const repoStatus = document.getElementById('repoStatus');

    function atualizaCampoToken() {
        campoToken.style.display = tipoPrivado.checked ? 'flex' : 'none';
    }
    tipoPublico.addEventListener('change', atualizaCampoToken);
    tipoPrivado.addEventListener('change', atualizaCampoToken);

    function setStatus(msg, cor) {
        repoStatus.innerText = msg;
        repoStatus.style.color = cor;
    }

    btnConectar.addEventListener('click', async function (e) {
        e.preventDefault();
        const url = repoUrl.value.trim();
        if (!url) {
            setStatus("Informe a URL do repositório.", "#ef4444");
            return;
        }

        const isPrivado = tipoPrivado.checked;
        let githubToken = null;
        if (isPrivado) {
            githubToken = repoToken.value.trim();
            if (!githubToken) {
                setStatus("Informe o token de acesso.", "#ef4444");
                return;
            }
        }

        const sincronizar = chkSincronizar.checked;

        await Sessao.pronto;

        const payload = {
            projeto_id: parseInt(Sessao.getProjetoId(), 10),
            url: url,
            is_private: isPrivado,
            token: isPrivado ? githubToken : null,
            sincronizar: sincronizar
        };

        setStatus("Conectando ao GitHub e analisando...", "#3b82f6");

        const endpoint = `${window.API.GITHUB}/api/github/conectar`;

        try {
            console.log("Payload enviado:", payload);
            const response = await fetch(endpoint, {
                method: "POST",
                headers: Sessao.getHeaders(),
                body: JSON.stringify(payload)
            });
            console.log("Status HTTP:", response.status, "OK:", response.ok);

            if (response.ok) {
                console.log("Resposta:", await response.clone().json().catch(() => "sem json"));
                setStatus("Repositório conectado com sucesso!", "#16a34a");
                setTimeout(() => window.location.href = "/projeto/arquivos", 1500);
            } else {
                try {
                    const errBody = await response.json();
                    let msg;
                    if (Array.isArray(errBody.detail)) {
                        msg = errBody.detail
                            .map(d => `${(d.loc || []).join('.')}: ${d.msg}`)
                            .join(' | ');
                    } else {
                        msg = errBody.detail || errBody.message || errBody.erro || JSON.stringify(errBody);
                    }
                    console.error("Corpo do erro (JSON):", errBody);
                    setStatus(`Erro ao conectar (${response.status}): ${msg}`, "#ef4444");
                } catch {
                    const errText = await response.text();
                    console.error("Corpo do erro (texto):", errText);
                    setStatus(`Erro ao conectar (${response.status}): ${errText || 'sem corpo'}`, "#ef4444");
                }
            }
        } catch (error) {
            console.error("Erro de rede:", error);
            setStatus(`Erro de conexão: ${error.message || error}`, "#ef4444");
        }
    });
})();
