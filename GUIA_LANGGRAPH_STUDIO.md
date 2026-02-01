# 🚀 Guia LangGraph Studio

## ⚠️ Problemas Comuns

### Erro 1: "Connection failed"
Servidor não está rodando ou não é acessível.

### Erro 2: "Failed to initialize Studio - Unexpected token '<'"
Studio está recebendo HTML ao invés de JSON. Geralmente significa:
- CORS não configurado corretamente
- Endpoint retornando HTML (erro 404/500)
- Problema com `allow_private_network`

## ✅ Soluções (Tente nesta ordem)

### Solução 1: Usar Tunnel (OBRIGATÓRIO) ⭐

**⚠️ OBRIGATÓRIO:** O Studio está em HTTPS, então você PRECISA usar HTTPS também. O tunnel é a única forma de ter HTTPS local.

```bash
cd back-end
source venv/bin/activate
langgraph dev --tunnel
```

**⚠️ IMPORTANTE:** 
- Aguarde até ver a mensagem completa com a URL do tunnel (pode demorar 10-30 segundos)
- NÃO use URLs HTTP (`http://0.0.0.0:2024` ou `http://192.168.90.108:2024`) - isso causa erro "Mixed Content"

Você receberá algo como:
```
🚀 API: http://127.0.0.1:2024
🌐 Tunnel: https://xxxx-xxxx-xxxx.trycloudflare.com
🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=https://xxxx-xxxx-xxxx.trycloudflare.com
```

**No Studio:**
- Base URL: Use a URL do tunnel completa com HTTPS (ex: `https://xxxx-xxxx-xxxx.trycloudflare.com`)
- Advanced Settings → Allowed Origins: `https://smith.langchain.com`

**Se der erro `ERR_NAME_NOT_RESOLVED`:**
- O tunnel pode não ter inicializado completamente - aguarde mais tempo
- Verifique sua conexão com internet
- Tente reiniciar: pare (Ctrl+C) e rode `langgraph dev --tunnel` novamente

### Solução 2: Verificar Console do Navegador

1. Pressione **F12** no navegador (Edge/Chrome)
2. Vá na aba **Console**
3. Tente conectar no Studio
4. Veja qual erro aparece exatamente

Erros comuns:
- `ERR_BLOCKED_BY_PRIVATE_NETWORK_ACCESS` → Use Solução 1 (tunnel)
- `CORS policy` → Problema de CORS
- `Failed to fetch` → Problema de rede/firewall
- `Connection refused` → Servidor não está rodando

### Solução 3: Verificar se Servidor Está Acessível

Do **Windows PowerShell**, teste:
```powershell
curl http://192.168.90.108:2024/docs
```

Se não funcionar, problema é firewall/rede.

## 📝 Configuração Atual

- **Servidor:** `langgraph dev --host 0.0.0.0` (porta 2024)
- **IP WSL:** `192.168.90.108`
- **CORS configurado** no `langgraph.json`
- **Ollama rodando** (porta 11434)

## 🔧 Comandos Úteis

```bash
# Iniciar servidor normal
cd back-end
source venv/bin/activate
langgraph dev --host 0.0.0.0

# Iniciar com tunnel (recomendado)
langgraph dev --tunnel

# Verificar IP do WSL
hostname -I | awk '{print $1}'

# Verificar se servidor local está rodando
curl http://127.0.0.1:2024/ok
# Deve retornar: {"ok":true}

# Verificar se servidor responde via IP
curl http://192.168.90.108:2024/docs

# Verificar processos rodando
ps aux | grep langgraph
lsof -ti:2024
```

## 🎯 No Studio Web UI

1. Acesse: https://smith.langchain.com/studio/
2. Clique em "Connect to local server"
3. **Base URL:** 
   - ⚠️ **OBRIGATÓRIO:** Use a URL do tunnel com HTTPS (ex: `https://xxxx-xxxx-xxxx.trycloudflare.com`)
   - ❌ **NÃO use:** `http://0.0.0.0:2024` ou `http://192.168.90.108:2024` (causa erro Mixed Content)
4. **Advanced Settings → Allowed Origins:** `https://smith.langchain.com`
5. Clique em "Connect"

## 🔧 Solução para Erro "Mixed Content" (IMPORTANTE!)

**Erro:** `Mixed Content: The page at 'https://smith.langchain.com' was loaded over HTTPS, but requested an insecure resource 'http://...'`

**Causa:** Navegadores bloqueiam requisições HTTP de páginas HTTPS por segurança.

**Solução:** Você PRECISA usar HTTPS, ou seja, usar o tunnel:

```bash
cd back-end
source venv/bin/activate
langgraph dev --tunnel
```

**⚠️ IMPORTANTE:**
1. Aguarde até ver a URL completa do tunnel no terminal (pode demorar 10-30 segundos)
2. Use a URL do tunnel COMPLETA no Studio (ex: `https://xxxx-xxxx-xxxx.trycloudflare.com`)
3. NÃO use `http://0.0.0.0:2024` ou `http://192.168.90.108:2024` - isso causa Mixed Content!

**Se o tunnel não funcionar:**
- Verifique sua conexão com internet
- Tente reiniciar o servidor: pare (Ctrl+C) e rode `langgraph dev --tunnel` novamente
- Aguarde mais tempo para o tunnel inicializar

## 🔧 Solução para Erro "ERR_NAME_NOT_RESOLVED" (Tunnel)

Se você vê esse erro ao usar `--tunnel`:

1. **O tunnel pode não ter inicializado completamente:**
   - Aguarde 10-30 segundos após iniciar `langgraph dev --tunnel`
   - Verifique o terminal - deve mostrar a URL do tunnel claramente

2. **Verifique se o servidor local está funcionando:**
   ```bash
   curl http://127.0.0.1:2024/ok
   ```
   Deve retornar: `{"ok":true}`

3. **Se o tunnel não funcionar, use servidor local:**
   ```bash
   # Pare o servidor (Ctrl+C)
   # Reinicie sem tunnel:
   langgraph dev --host 0.0.0.0
   ```
   No Studio, use: `http://192.168.90.108:2024`

4. **Tente acessar a URL do tunnel diretamente no navegador:**
   - Abra: `https://reno-tail-updating-consultation.trycloudflare.com/info`
   - Se não carregar, o tunnel não está funcionando

## 🔧 Solução para Erro "Unexpected token '<'"

Se você vê esse erro, o Studio está recebendo HTML ao invés de JSON:

1. **Reinicie o servidor** após atualizar `langgraph.json`:
   ```bash
   # Pare o servidor (Ctrl+C)
   # Depois reinicie:
   cd back-end
   source venv/bin/activate
   langgraph dev --host 0.0.0.0
   ```

2. **Verifique se o servidor responde JSON:**
   ```bash
   curl http://192.168.90.108:2024/ok
   ```
   Deve retornar: `{"ok":true}` (JSON), não HTML

3. **No Studio, use Base URL sem barra final:**
   - ✅ Correto: `http://192.168.90.108:2024`
   - ❌ Errado: `http://192.168.90.108:2024/`

4. **Verifique o Console do navegador (F12):**
   - Veja qual requisição está falhando
   - Verifique se retorna HTML ou JSON

## 🔍 Entendendo o Problema: Tunnel vs Navegador

**O que está acontecendo:**

1. ✅ **Servidor local funciona:** `curl http://127.0.0.1:2024/ok` retorna `{"ok":true}`
2. ✅ **Tunnel está conectado:** Logs mostram "Registered tunnel connection"
3. ❌ **Navegador não resolve:** `ERR_NAME_NOT_RESOLVED` ao acessar URL do tunnel

**Por que isso acontece:**

O tunnel cria uma conexão do **servidor (WSL) → Cloudflare**, mas o **navegador (Windows)** precisa resolver o DNS do domínio `.trycloudflare.com`. Se o DNS não resolver, o navegador não consegue encontrar o servidor, mesmo que o tunnel esteja funcionando.

**Possíveis causas:**

1. **DNS do Windows não resolve `.trycloudflare.com`**
   - Firewall bloqueando DNS
   - DNS corporativo bloqueando Cloudflare
   - Configuração de DNS incorreta

2. **Firewall do Windows bloqueando Cloudflare**
   - Bloqueando conexões para `*.trycloudflare.com`
   - Bloqueando porta HTTPS (443)

3. **Rede/VPN bloqueando**
   - VPN corporativa bloqueando Cloudflare
   - Proxy bloqueando

**Como testar:**

Do **Windows PowerShell**, teste:
```powershell
# Testar DNS
nslookup visited-succeed-equivalent-sum.trycloudflare.com

# Testar conexão HTTPS
curl https://visited-succeed-equivalent-sum.trycloudflare.com/ok
```

Se ambos falharem, é problema de DNS/Firewall do Windows, não do servidor.

## 🚨 Se Tunnel Não Funcionar (ERR_NAME_NOT_RESOLVED)

Se você sempre vê `ERR_NAME_NOT_RESOLVED` mesmo com tunnel:

**Possíveis causas:**
1. Firewall bloqueando Cloudflare
2. DNS não resolvendo domínios `.trycloudflare.com`
3. Rede corporativa/VPN bloqueando
4. Problema de conectividade com Cloudflare

**Soluções:**

### Opção 1: Usar FastAPI Diretamente (SEM Studio)

O Studio é apenas para visualização. Você pode usar o endpoint diretamente:

```bash
cd back-end
source venv/bin/activate
fastapi dev ./src/main.py --host 0.0.0.0
```

Acesse: http://localhost:8000/docs

O endpoint `/stories/generate` funciona normalmente e usa LangGraph internamente. Você pode:
- Testar o endpoint diretamente
- Ver logs dos agentes no terminal
- Usar Postman/Insomnia para testar

### Opção 2: Verificar Firewall/DNS

Do Windows PowerShell, teste:
```powershell
# Testar DNS
nslookup visited-succeed-equivalent-sum.trycloudflare.com

# Testar conexão
curl https://visited-succeed-equivalent-sum.trycloudflare.com/info
```

Se não funcionar, pode ser firewall bloqueando Cloudflare.

### Opção 3: Usar VPN/Outra Rede

Se estiver em rede corporativa, tente:
- Desconectar VPN temporariamente
- Usar outra rede (hotspot do celular)
- Verificar se firewall corporativo bloqueia Cloudflare
