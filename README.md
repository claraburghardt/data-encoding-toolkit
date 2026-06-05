# Data Encoding Toolkit

**Integrantes:** Patrícia Nagel e Clara Burghardt

Toolkit de codificação e detecção/correção de erros e comunicação cliente-servidor.

---

## Como executar

1. Inicie o servidor:
   ```
   python server.py
   ```
2. Em outro terminal, inicie o cliente:
   ```
   python main.py
   ```

---

## Fluxo geral

1. Digite uma mensagem no campo de entrada
2. Escolha o algoritmo e a ação (Codificar / Decodificar)
3. Clique em **Executar**
4. Opcionalmente, insira um erro em uma posição específica dos bits
5. Para algoritmos de detecção/correção (Repetição, Hamming, CRC-4), clique em **Enviar ao Servidor** para que o servidor verifique/corrija os bits

---

## Algoritmos de compressão

### Golomb
Codifica inteiros dividindo cada valor por um parâmetro `k`: o quociente é representado em unário e o resto em binário de tamanho fixo. O valor de `k` é calculado automaticamente com base na média dos valores ASCII da mensagem. **O valor de `k` é necessário para decodificar** — ele é exibido no histórico após a codificação.

- Entrada: texto
- Saída: bits
- Parâmetro necessário para decodificar: `k`

### Elias-Gamma
Codifica cada valor inteiro positivo com um prefixo de `n` zeros (onde `n = floor(log2(valor))`), um stop bit `1`, e o sufixo com os `n` bits menos significativos do valor. Funciona bem para valores pequenos.

- Entrada: texto
- Saída: bits

### Fibonacci (Zeckendorf)
Representa cada valor como soma única de números de Fibonacci não consecutivos (Teorema de Zeckendorf). O fim de cada símbolo é marcado pelo padrão `11` (dois uns consecutivos).

- Entrada: texto
- Saída: bits

### Huffman
Constrói uma árvore binária onde símbolos mais frequentes recebem códigos menores. A árvore é gerada a partir da mensagem codificada e é necessária para decodificar — **não feche nem recodifique antes de decodificar**.

- Entrada: texto
- Saída: bits
- Requisito: a árvore gerada na codificação deve estar disponível na sessão

---

## Algoritmos de detecção e correção de erros

Estes algoritmos são aplicados **sobre os bits gerados por um algoritmo de compressão**. Codifique uma mensagem primeiro, depois aplique um desses.

### Repetição
Cada bit é repetido `R` vezes. A decodificação usa votação majoritária para corrigir erros: se a maioria dos bits de um grupo for `1`, o bit original era `1`. Para melhor correção, use `R` ímpar (padrão: 3).

- Detecta e corrige erros por maioria
- Parâmetro: `R` (número de repetições)
- Exemplo com R=3: `1` → `111`, `0` → `000`; bloco `110` → corrigido para `1`

### Hamming (7,4)
Codifica blocos de 4 bits de dados em palavras de 7 bits, inserindo 3 bits de paridade nas posições 1, 2 e 4. A síndrome calculada na decodificação indica a posição exata do erro.

- Detecta até 2 erros por bloco
- Corrige 1 erro por bloco
- O valor de `padding` (bits extras adicionados ao último bloco) é guardado automaticamente

### CRC-4
Usa o polinômio gerador `G(x) = x⁴ + x + 1` (binário: `10011`). Anexa 4 bits de redundância ao final da mensagem. Na verificação, divide a mensagem recebida (com CRC) pelo mesmo polinômio — resto `0000` indica ausência de erro.

- **Apenas detecta erros, não corrige**
- 4 bits de redundância (CRC) são anexados ao final da mensagem

---

## Arquitetura

| Arquivo | Descrição |
|---|---|
| `main.py` | Interface gráfica (Tkinter) e lógica do cliente |
| `server.py` | Servidor TCP que recebe bits e aplica Repetição, Hamming ou CRC-4 |
| `golomb_module.py` | Implementação do código de Golomb |
| `elias_gamma_module.py` | Implementação do código de Elias-Gamma |
| `fibonacci_module.py` | Implementação do código de Fibonacci (Zeckendorf) |
| `huffman_module.py` | Implementação do código de Huffman |
| `repetition_module.py` | Implementação do código de Repetição |
| `hamming_module.py` | Implementação do código de Hamming (7,4) |
| `crc_module.py` | Implementação do CRC-4 |
