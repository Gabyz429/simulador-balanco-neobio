
# Simulador de Proteína no DDGS (Streamlit)

Aplicativo web simples para estimar o teor de proteína do DDGS a partir de WDG e xarope sem óleo (CDS), com possibilidade de reduzir a taxa de inclusão do xarope.

## Como rodar localmente
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o app:
   ```bash
   streamlit run app.py
   ```

## Como publicar (Streamlit Community Cloud)
1. Crie um repositório no GitHub e faça o upload de `app.py` e `requirements.txt`.
2. Acesse https://streamlit.io/cloud e clique em **Deploy an app**.
3. Conecte seu GitHub, escolha o repositório e a branch, e selecione `app.py` como arquivo principal.
4. Clique em **Deploy**. Pronto! Compartilhe a URL gerada com o seu time.

> Dica: personalize os valores padrão no app para refletir os dados da sua planta.
