# VibeSync 🎧

VibeSync é um recomendador musical inteligente desenvolvido em Python com Streamlit. O sistema utiliza a API do Google Gemini para analisar a "vibe" do usuário e sugerir músicas fora do padrão, conectando-se à API do Spotify para buscar as capas dos álbuns e os links diretos de reprodução.

## Pré-requisitos

Para rodar este projeto, você precisará de:
* Python 3.8+ instalado.
* Uma conta no [Google AI Studio](https://aistudio.google.com/) para gerar sua API Key do Gemini.
* Uma conta no [Spotify for Developers](https://developer.spotify.com/) para gerar as credenciais da API.

## Configuração do Ambiente

1 - Instalar as dependencias:

pip install -r requirements.txt

2 - Configure as credenciais do Spotify:
Crie uma pasta oculta chamada .streamlit na raiz do projeto e dentro dela crie um arquivo chamado secrets.toml:

mkdir .streamlit
touch .streamlit/secrets.toml

3 - Abra o arquivo secrets.toml e insira o seu Client ID e Client Secret gerados no painel de desenvolvedor do Spotify:

SPOTIFY_CLIENT_ID = "seu_client_id_aqui"
SPOTIFY_CLIENT_SECRET = "seu_client_secret_aqui"

4 - Como executar:

streamlit run app.py
