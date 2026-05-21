// sessao.js — módulo de sessão compartilhado entre as abas do projeto

const Sessao = (() => {
    let _usuario = null;
    let _projetoId = null;
    let _token = null;
    let _prontoResolve;
    const _pronto = new Promise(r => { _prontoResolve = r; });

    function _capturarDaUrl() {
        const params = new URLSearchParams(window.location.search);
        const id = params.get('id');
        const token = params.get('token');
        if (id && token) {
            localStorage.setItem('projeto_id', id);
            localStorage.setItem('token', token);
            try {
                // Normaliza barra dupla (ex: //projeto/upload → /projeto/upload)
                // que ocorre quando o grupo de Projetos concatena a URL base com barra sobrando.
                const safePath = '/' + window.location.pathname.replace(/^\/+/, '');
                history.replaceState(null, '', safePath);
            } catch (e) {
                console.warn('[sessao] replaceState falhou (ignorado):', e.message);
            }
            return { id, token };
        }
        return null;
    }

    function _lerStorage() {
        return {
            id: localStorage.getItem('projeto_id'),
            token: localStorage.getItem('token')
        };
    }

    function _decodificarPayload(token) {
        try {
            const b64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
            return JSON.parse(atob(b64));
        } catch {
            return null;
        }
    }

    function _limparERediredir() {
        localStorage.removeItem('projeto_id');
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        localStorage.removeItem('nome');
        window.location.href = window.API?.LOGIN_URL
            || 'https://docuia-frontend-hdc8hzfqbqebc6cp.brazilsouth-01.azurewebsites.net/login';
    }

    async function _inicializar() {
        const daUrl = _capturarDaUrl();
        const { id, token } = daUrl || _lerStorage();

        if (!id || !token) {
            _limparERediredir();
            return;
        }

        _projetoId = id;
        _token = token;

        // Validação client-side: decodifica o payload e checa expiração.
        // A verificação de assinatura acontece no servidor a cada ação autenticada.
        const payload = _decodificarPayload(token);
        if (!payload) {
            console.warn('[sessao] Token malformado.');
            _limparERediredir();
            return;
        }
        if (payload.exp && Date.now() / 1000 > payload.exp) {
            console.warn('[sessao] Token expirado.');
            _limparERediredir();
            return;
        }

        _usuario = {
            user_id: payload.sub,
            email:   payload.email,
            nome:    payload.nome
        };
        localStorage.setItem('user_id', String(payload.sub || ''));
        localStorage.setItem('nome', payload.nome || '');
        localStorage.setItem('email', payload.email || '');

        _prontoResolve();

        // Atualiza o botão "Voltar para Projetos" com o id do projeto atual
        const btn = document.querySelector('.back-to-projects');
        if (btn) {
            const base = (window.API?.FRONT_PRINCIPAL_URL || '').replace(/\/$/, '');
            btn.href = base + '/projeto' + (_projetoId ? `?id=${_projetoId}` : '');
        }

        // Preenche dados do usuário na sidebar
        const nome  = _usuario?.nome  || '';
        const email = _usuario?.email || '';
        const nameEl   = document.getElementById('sidebar-user-name');
        const emailEl  = document.getElementById('sidebar-user-email');
        const avatarEl = document.querySelector('.profile-mini-avatar');
        if (nameEl)   nameEl.textContent  = nome  || 'Usuário';
        if (emailEl)  emailEl.textContent = email || '';
        if (avatarEl) avatarEl.textContent = nome ? nome.charAt(0).toUpperCase() : 'U';
    }

    // .catch() garante que erros inesperados não virem unhandled rejection
    _inicializar().catch(e => console.error('[sessao] Erro inesperado na inicialização:', e));

    return {
        /** Promise que resolve após sessão validada. Aguarde antes de fazer chamadas autenticadas. */
        pronto: _pronto,
        getProjetoId() { return _projetoId; },
        getToken()     { return _token; },
        getUsuario()   { return _usuario; },
        /** Para FormData, passe isJson=false (o browser define o Content-Type com boundary). */
        getHeaders(isJson = true) {
            const h = { 'Authorization': `Bearer ${_token}` };
            if (isJson) h['Content-Type'] = 'application/json';
            return h;
        }
    };
})();