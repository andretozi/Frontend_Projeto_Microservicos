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
            // Remove id e token da barra de endereço sem recarregar
            history.replaceState(null, '', window.location.pathname);
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

        try {
            const resp = await fetch('/api/validar-sessao', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await resp.json();

            if (!data.valido) {
                _limparERediredir();
                return;
            }

            _usuario = { user_id: data.user_id, email: data.email, nome: data.nome };
            localStorage.setItem('user_id', String(data.user_id));
            localStorage.setItem('nome', data.nome || '');

        } catch {
            // Servidor inacessível: decodifica client-side só para verificar expiração
            const payload = _decodificarPayload(token);
            if (!payload || (payload.exp && Date.now() / 1000 > payload.exp)) {
                _limparERediredir();
                return;
            }
            _usuario = { user_id: payload.sub, email: payload.email, nome: payload.nome };
        }

        _prontoResolve();
    }

    _inicializar();

    return {
        /** Promise que resolve após sessão validada. Aguarde antes de fazer chamadas autenticadas. */
        pronto: _pronto,
        getProjetoId() { return _projetoId; },
        getToken()     { return _token; },
        getUsuario()   { return _usuario; },
        /** Retorna headers com Authorization. Para FormData, chame sem parâmetro (isJson=false). */
        getHeaders(isJson = true) {
            const h = { 'Authorization': `Bearer ${_token}` };
            if (isJson) h['Content-Type'] = 'application/json';
            return h;
        }
    };
})();