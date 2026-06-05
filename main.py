import tkinter as tk
from tkinter import messagebox

# Importa as implementações dos algoritmos de compressão
from elias_gamma_module import EliasGamma
from fibonacci_module import Fibonacci
from golomb_module import Golomb
from huffman_module import Huffman
from repetition_module import Repeticao
from hamming_module import Hamming74

# ========================
# INSTANCIAÇÃO DOS ALGORITMOS
# ========================

# Criamos objetos de cada algoritmo para reutilizar suas funções
golomb = Golomb()
elias_gamma = EliasGamma()
huffman = Huffman()
fibonacci = Fibonacci()
repeticao = Repeticao()
hamming = Hamming74()

# Variável global para guardar a árvore do Huffman
# IMPORTANTE:
# Diferente dos outros algoritmos, o Huffman precisa da árvore para decodificar
huffman_raiz = None

# Guarda o último resultado codificado (sem espaços) para inserção de erro
ultimo_resultado_codificado = None

# Guarda o padding do Hamming para usar na decodificação
hamming_padding = 0


def atualizar_historico():
    """Reescreve o histórico na caixa de texto."""
    historico_texto.config(state=tk.NORMAL)
    historico_texto.delete(1.0, tk.END)
    for linha in historico:
        historico_texto.insert(tk.END, linha + "\n")
    historico_texto.config(state=tk.DISABLED)


def executar_opcao(algoritmo, acao):
    """
    Função principal da aplicação.

    Ela decide:
    - qual algoritmo usar
    - se vai codificar ou decodificar
    """

    global huffman_raiz, ultimo_resultado_codificado, hamming_padding

    # ========================
    # ENTRADA DO USUÁRIO
    # ========================

    # Pega o texto digitado e remove espaços extras
    mensagem = entrada_mensagem.get().strip()

    # Validação básica: não permite entrada vazia
    if not mensagem:
        messagebox.showerror("Erro", "Por favor, digite uma mensagem ou bits.")
        return

    resultado = ""

    # ========================
    # CODIFICAÇÃO
    # ========================

    if acao == "Codificar":

        if algoritmo == "Golomb":
            # Retorna os bits e o valor de k usado
            resultado, k = golomb.encoder(mensagem)

            # Guarda no histórico
            historico.append(f"Codificado (Golomb, k={k}): {resultado}")

            # IMPORTANTE:
            # Golomb precisa do k para decodificar depois
            historico.append(f"⚠ Guarde o k={k} para decodificar!")

            # Preenche automaticamente o campo de k na interface
            entrada_k.config(state=tk.NORMAL)
            entrada_k.delete(0, tk.END)
            entrada_k.insert(0, str(k))

        elif algoritmo == "Elias-Gamma":
            resultado = elias_gamma.encoder(mensagem)
            historico.append(f"Codificado (Elias-Gamma): {resultado}")

        elif algoritmo == "Fibonacci":
            resultado = fibonacci.encoder(mensagem)
            historico.append(f"Codificado (Fibonacci): {resultado}")

        elif algoritmo == "Huffman":
            # Retorna os bits e a árvore (raiz)
            resultado, huffman_raiz = huffman.encoder(mensagem)

            # IMPORTANTE:
            # Precisamos guardar a árvore para decodificar depois
            historico.append(f"Codificado (Huffman): {resultado}")

        elif algoritmo == "Repetição":
            # Usa automaticamente o último resultado codificado
            if ultimo_resultado_codificado is None:
                messagebox.showerror("Erro", "Codifique uma mensagem com outro algoritmo antes de aplicar Repetição.")
                return

            r_valor = entrada_r.get().strip()
            if not r_valor.isdigit() or int(r_valor) < 1:
                messagebox.showerror("Erro", "Informe um valor de R válido (inteiro >= 1).")
                return

            r = int(r_valor)
            resultado = repeticao.encoder(ultimo_resultado_codificado, r)
            historico.append(f"Entrada para Repetição (bits anteriores): {ultimo_resultado_codificado}")
            historico.append(f"Codificado (Repetição, r={r}): {resultado}")

        elif algoritmo == "Hamming (7,4)":
            # Usa automaticamente o último resultado codificado
            if ultimo_resultado_codificado is None:
                messagebox.showerror("Erro", "Codifique uma mensagem com outro algoritmo antes de aplicar Hamming.")
                return

            try:
                resultado, hamming_padding = hamming.encoder(ultimo_resultado_codificado)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return

            historico.append(f"Entrada para Hamming (bits anteriores): {ultimo_resultado_codificado}")
            if hamming_padding > 0:
                historico.append(f"  (padding adicionado: {hamming_padding} bit(s))")
            historico.append(f"Codificado (Hamming 7,4): {resultado}")

        # Habilita inserção de erro após codificação
        ultimo_resultado_codificado = resultado.replace(" ", "")
        label_erro.config(text=f"Inserir erro (posição 0 a {len(ultimo_resultado_codificado) - 1}):")
        entrada_pos_erro.config(state=tk.NORMAL)
        botao_erro.config(state=tk.NORMAL)

        # Atualiza o histórico antes de preencher o campo de entrada
        atualizar_historico()

        # Preenche o campo de entrada com os bits gerados para facilitar decodificação
        entrada_mensagem.delete(0, tk.END)
        entrada_mensagem.insert(0, ultimo_resultado_codificado)
        return

    # ========================
    # DECODIFICAÇÃO
    # ========================

    elif acao == "Decodificar":

        # Validação binária (aceita espaços)
        partes = mensagem.split()
        if not all(all(c in "01" for c in parte) for parte in partes):
            messagebox.showerror("Erro", "A entrada deve conter apenas 0s e 1s.")
            return

        if algoritmo == "Golomb":
            # Lê o valor de k digitado pelo usuário
            k_valor = entrada_k.get().strip()

            # Validação: precisa ser número positivo
            if not k_valor.isdigit() or int(k_valor) <= 0:
                messagebox.showerror("Erro", "Informe um k válido (inteiro positivo) para decodificar com Golomb.")
                return

            resultado = golomb.decoder(mensagem, int(k_valor))

        elif algoritmo == "Elias-Gamma":
            resultado = elias_gamma.decoder(mensagem)

        elif algoritmo == "Fibonacci":
            resultado = fibonacci.decoder(mensagem)

        elif algoritmo == "Huffman":
            # Validação importante:
            # Não dá pra decodificar sem a árvore
            if huffman_raiz is None:
                messagebox.showerror("Erro", "Codifique algo com Huffman antes de decodificar!")
                return

            resultado = huffman.decoder(mensagem, huffman_raiz)

        elif algoritmo == "Repetição":
            r_valor = entrada_r.get().strip()
            if not r_valor.isdigit() or int(r_valor) < 1:
                messagebox.showerror("Erro", "Informe um valor de R válido (inteiro >= 1).")
                return

            r = int(r_valor)
            try:
                resultado, erros = repeticao.decoder(mensagem.replace(" ", ""), r)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return

            if erros:
                historico.append(f"Decodificado (Repetição, r={r}): {resultado}")
                historico.append(f"⚠ Erros detectados e corrigidos nos blocos: {erros}")
            else:
                historico.append(f"Decodificado (Repetição, r={r}): {resultado}")
                historico.append("✓ Nenhum erro detectado.")

            # Preenche o campo com os bits recuperados para facilitar próxima decodificação
            entrada_mensagem.delete(0, tk.END)
            entrada_mensagem.insert(0, resultado)
            atualizar_historico()
            return

        elif algoritmo == "Hamming (7,4)":
            try:
                resultado, erros = hamming.decoder(mensagem.replace(" ", ""), hamming_padding)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return

            if erros:
                historico.append(f"Decodificado (Hamming 7,4): {resultado}")
                for e in erros:
                    if e["corrigido"]:
                        historico.append(f"⚠ Erro no bloco {e['bloco']}, posição {e['posicao']} — corrigido.")
                    else:
                        historico.append(f"✗ Erro no bloco {e['bloco']}, posição {e['posicao']} — não corrigível.")
            else:
                historico.append(f"Decodificado (Hamming 7,4): {resultado}")
                historico.append("✓ Nenhum erro detectado.")

            # Preenche o campo com os bits recuperados para facilitar próxima decodificação
            entrada_mensagem.delete(0, tk.END)
            entrada_mensagem.insert(0, resultado)
            atualizar_historico()
            return

        # Adiciona resultado ao histórico
        historico.append(f"Decodificado ({algoritmo}): {resultado}")

    atualizar_historico()


def inserir_erro():
    """
    Inverte o bit na posição informada pelo usuário dentro do último resultado codificado.
    Registra o antes e depois no histórico e preenche o campo de entrada para facilitar
    a decodificação com erro.
    """
    global ultimo_resultado_codificado

    if ultimo_resultado_codificado is None:
        messagebox.showerror("Erro", "Codifique uma mensagem antes de inserir erros.")
        return

    pos_str = entrada_pos_erro.get().strip()
    if not pos_str.isdigit():
        messagebox.showerror("Erro", "Informe uma posição numérica válida.")
        return

    pos = int(pos_str)
    bits = ultimo_resultado_codificado

    if pos < 0 or pos >= len(bits):
        messagebox.showerror("Erro", f"Posição inválida. Escolha entre 0 e {len(bits) - 1}.")
        return

    # Inverte o bit na posição informada
    bit_original = bits[pos]
    bit_novo = "1" if bit_original == "0" else "0"
    bits_com_erro = bits[:pos] + bit_novo + bits[pos + 1:]

    historico.append(f"--- Inserção de erro ---")
    historico.append(f"Original:   {bits}")
    historico.append(f"Com erro:   {bits_com_erro}  (bit {pos}: {bit_original} → {bit_novo})")

    # Preenche o campo de entrada com os bits corrompidos para facilitar decodificação
    entrada_mensagem.delete(0, tk.END)
    entrada_mensagem.insert(0, bits_com_erro)

    atualizar_historico()


# ========================
# CRIAÇÃO DA INTERFACE
# ========================

# Cria a janela principal
janela = tk.Tk()
janela.title("Codificador e Decodificador - TI")

# Campo de entrada da mensagem
tk.Label(janela, text="Digite sua mensagem ou bits:").pack(pady=(10, 0))
entrada_mensagem = tk.Entry(janela, width=50)
entrada_mensagem.pack(pady=(0, 10))

# Campo para o parâmetro k do Golomb
tk.Label(janela, text="Parâmetro k (apenas para decodificação Golomb):").pack()

# Começa desabilitado (só é necessário em um caso específico)
entrada_k = tk.Entry(janela, width=10, state=tk.DISABLED)
entrada_k.pack(pady=(0, 5))

# Campo para o parâmetro R da Repetição
tk.Label(janela, text="Parâmetro R (apenas para Repetição):").pack()
entrada_r = tk.Entry(janela, width=10, state=tk.DISABLED)
entrada_r.insert(0, "3")
entrada_r.pack(pady=(0, 10))


def atualizar_campo_k(*args):
    """
    Controla visibilidade dos campos auxiliares conforme algoritmo/ação selecionados.
    """
    alg = algoritmo_var.get()
    acao = acao_var.get()

    # Campo k: só para Golomb + Decodificar
    if alg == "Golomb" and acao == "Decodificar":
        entrada_k.config(state=tk.NORMAL)
    else:
        entrada_k.config(state=tk.DISABLED)

    # Campo R: só para Repetição
    if alg == "Repetição":
        entrada_r.config(state=tk.NORMAL)
    else:
        entrada_r.config(state=tk.DISABLED)


# ========================
# MENUS DE SELEÇÃO
# ========================

# Escolha do algoritmo
algoritmo_var = tk.StringVar(value="Golomb")
algoritmo_var.trace_add("write", atualizar_campo_k)

algoritmo_menu = tk.OptionMenu(
    janela,
    algoritmo_var,
    "Golomb", "Elias-Gamma", "Fibonacci", "Huffman", "Repetição", "Hamming (7,4)"
)
algoritmo_menu.pack()

# Escolha da ação
acao_var = tk.StringVar(value="Codificar")
acao_var.trace_add("write", atualizar_campo_k)

acao_menu = tk.OptionMenu(
    janela,
    acao_var,
    "Codificar", "Decodificar"
)
acao_menu.pack(pady=(5, 10))


# ========================
# BOTÃO EXECUTAR
# ========================

# Chama a função principal passando as escolhas do usuário
executar_button = tk.Button(
    janela,
    text="Executar",
    command=lambda: executar_opcao(algoritmo_var.get(), acao_var.get())
)
executar_button.pack()


# ========================
# INSERÇÃO DE ERRO
# ========================

tk.Frame(janela, height=1, bg="gray").pack(fill=tk.X, padx=10, pady=(10, 0))

label_erro = tk.Label(janela, text="Inserir erro (posição):")
label_erro.pack(pady=(6, 0))

frame_erro = tk.Frame(janela)
frame_erro.pack(pady=(0, 10))

entrada_pos_erro = tk.Entry(frame_erro, width=8, state=tk.DISABLED)
entrada_pos_erro.pack(side=tk.LEFT, padx=(0, 5))

botao_erro = tk.Button(
    frame_erro,
    text="Inserir Erro",
    state=tk.DISABLED,
    command=inserir_erro
)
botao_erro.pack(side=tk.LEFT)


# ========================
# HISTÓRICO
# ========================

tk.Label(janela, text="Histórico:").pack(pady=(10, 0))

# Caixa de texto onde mostramos resultados
historico_texto = tk.Text(
    janela,
    wrap=tk.WORD,
    height=10,
    width=50,
    state=tk.DISABLED
)
historico_texto.pack(pady=(0, 10))

# Lista que guarda o histórico
historico = []


# ========================
# LOOP DA INTERFACE
# ========================

# Mantém a janela rodando
janela.mainloop()