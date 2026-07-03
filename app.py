import streamlit as st
import google.generativeai as genai
import typing
import json
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# -- 1. Configuração da Página --
st.set_page_config(page_title="VibeSync - Recomendador Musical", page_icon="🎧", layout="centered")

# -- 2. Inicialização do Spotify (via st.secrets) --
try:
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
        client_id=st.secrets["SPOTIFY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIFY_CLIENT_SECRET"]
    ))
except Exception as e:
    sp = None
    st.error(f"Falha ao conectar com o Spotify: {e}")

# -- 3. Estrutura de Dados JSON --
class MusicaRecomendada(typing.TypedDict):
    nome_musica: str
    artista: str
    genero: str
    motivo: str

class RespostaRecomendacao(typing.TypedDict):
    recomendacoes: list[MusicaRecomendada]

def buscar_info_spotify(nome_musica, artista):
    if not sp:
        return None, None
        
    queries = [f"track:{nome_musica} artist:{artista}", f"{nome_musica} {artista}"]
    
    for query in queries:
        try:
            results = sp.search(q=query, type='track', limit=1)
            items = results.get('tracks', {}).get('items', [])
            
            if items:
                track = items[0]
                imagens = track.get('album', {}).get('images', [])
                capa_url = imagens[0]['url'] if imagens else None
                link_spotify = track.get('external_urls', {}).get('spotify')
                return capa_url, link_spotify
                
        except SpotifyException as e:
            st.toast(f"Erro na API do Spotify: {e}")
            break 
            
    return None, None

# -- 4. Gerenciamento de Estado --
if "lista_musicas" not in st.session_state:
    st.session_state.lista_musicas = []

st.title("🎧 VibeSync: Encontre o seu Som")
st.write("Saindo da bolha musical: diga o que você está sentindo e nossa IA cuida do resto.")

with st.sidebar:
    st.header("⚙️ Configurações")
    api_key_input = st.text_input("Sua API Key do Google Gemini:", type="password")
    st.caption("A chave não é salva. Ela é usada apenas durante esta sessão.")

# Early Return: Interrompe a execução aqui se não houver chave
if not api_key_input:
    st.info("Insira sua API Key do Gemini na barra lateral para iniciar.")
    st.stop()

# -- 5. Configuração da IA --
genai.configure(api_key=api_key_input)

instrucao_sistema = """
Você é um curador musical especialista. Ajude usuários a encontrar novas músicas baseadas em suas "vibes".
Fuja de recomendações clichês.
REGRA 1: O campo 'motivo' deve conter no máximo 2 frases curtas e diretas.
REGRA 2: Retorne sempre em português nativo.
"""

model = genai.GenerativeModel('gemini-3.5-flash', system_instruction=instrucao_sistema)

# -- 6. Formulário Principal --
with st.expander("Nova Busca Musical 🔍", expanded=not st.session_state.lista_musicas):
    with st.form("formulario_busca"):
        vibe_usuario = st.text_input("Qual é a sua vibe ou momento atual?", placeholder="Ex: Estudando de madrugada com chuva...")
        referencias_usuario = st.text_input("Artistas ou gêneros de referência?", placeholder="Ex: Radiohead, Lo-fi, MPB...")
        
        if st.form_submit_button("Gerar Recomendações 🚀"):
            if not vibe_usuario or not referencias_usuario:
                st.warning("⚠️ Preencha a sua vibe e as referências.")
            else:
                with st.spinner("Analisando sua vibe e buscando a trilha sonora..."):
                    try:
                        resposta = model.generate_content(
                            f"Vibe: {vibe_usuario}. Referências: {referencias_usuario}. Recomende 4 músicas.",
                            generation_config=genai.GenerationConfig(
                                response_mime_type="application/json",
                                response_schema=RespostaRecomendacao,
                                temperature=0.6
                            )
                        )
                        st.session_state.lista_musicas = json.loads(resposta.text)["recomendacoes"]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Falha na execução: {e}")

# -- 7. Renderização de Resultados --
if st.session_state.lista_musicas:
    st.subheader("🎵 Suas Recomendações:")
    
    for musica in st.session_state.lista_musicas:
        nome = musica.get('nome_musica', 'Desconhecido')
        artista = musica.get('artista', 'Desconhecido')
        
        col_img, col_texto = st.columns([1, 3])
        capa_url, link_spotify = buscar_info_spotify(nome, artista)
        
        with col_img:
            if capa_url:
                st.image(capa_url, use_container_width=True)
            else:
                st.write("💿 Capa indisponível")
                
        with col_texto:
            st.write(f"**{nome}** - {artista}")
            st.write(f"**Gênero:** {musica.get('genero', 'N/A')}")
            st.write(f"**Motivo:** {musica.get('motivo', 'N/A')}")
            if link_spotify:
                st.markdown(f"[🎧 Ouvir no Spotify]({link_spotify})")
        st.divider()

    # -- Formulário de Refinamento --
    st.subheader("🔁 Aprofundar Busca")
    with st.form("formulario_refinamento"):
        pedido_extra = st.text_input("Peça mais no mesmo estilo:", placeholder="Ex: Gostei da vibe da música 2, dê sugestões com piano suave.")
        
        if st.form_submit_button("Refinar Recomendações") and pedido_extra:
            with st.spinner("Refinando suas recomendações..."):
                try:
                    contexto_atual = json.dumps(st.session_state.lista_musicas, ensure_ascii=False)
                    prompt_refinado = f"Recomendações atuais: {contexto_atual}. Pedido: '{pedido_extra}'. Gere 4 NOVAS músicas."
                    
                    resposta = model.generate_content(
                        prompt_refinado,
                        generation_config=genai.GenerationConfig(
                            response_mime_type="application/json",
                            response_schema=RespostaRecomendacao,
                            temperature=0.1
                        )
                    )
                    st.session_state.lista_musicas = json.loads(resposta.text)["recomendacoes"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Falha ao refinar busca: {e}")