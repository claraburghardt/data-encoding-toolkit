class Repeticao:
    """
    Código de Repetição (Ri).

    Cada bit da mensagem codificada é repetido R vezes.
    Exemplo com R=3: bit '1' vira '111', bit '0' vira '000'.

    Correção de erro por votação majoritária:
    - '111' → 1 (correto)
    - '110' → 1 (corrigido)
    - '100' → 0 (corrigido — maioria é 0)
    - '000' → 0 (correto)
    """

    def encoder(self, bits: str, r: int) -> str:
        """
        Codifica uma string de bits repetindo cada bit R vezes.

        Parâmetros:
            bits: string binária (ex: '1011')
            r: número de repetições (deve ser ímpar para correção por maioria)

        Retorna:
            string binária codificada (ex: com r=3: '111000111111')
        """
        if r < 1:
            raise ValueError("O número de repetições deve ser pelo menos 1.")

        resultado = ""
        for bit in bits:
            if bit not in ("0", "1"):
                raise ValueError(f"Entrada inválida: '{bit}' não é um bit válido.")
            resultado += bit * r

        return resultado

    def decoder(self, bits: str, r: int) -> str:
        """
        Decodifica e corrige erros por votação majoritária.

        Parâmetros:
            bits: string binária codificada com repetição
            r: número de repetições usado na codificação

        Retorna:
            string binária decodificada (após correção por votação)
        """
        if r < 1:
            raise ValueError("O número de repetições deve ser pelo menos 1.")

        if len(bits) % r != 0:
            raise ValueError(
                f"Tamanho da entrada ({len(bits)}) não é múltiplo de r={r}."
            )

        resultado = ""
        erros = []

        for i in range(0, len(bits), r):
            bloco = bits[i:i + r]

            # Validação: só aceita 0s e 1s
            if not all(c in "01" for c in bloco):
                raise ValueError(f"Bloco inválido: '{bloco}'")

            uns = bloco.count("1")
            zeros = bloco.count("0")

            # Votação majoritária
            bit_corrigido = "1" if uns > zeros else "0"
            resultado += bit_corrigido

            # Registra se houve erro no bloco (bloco não é uniforme)
            if uns != r and zeros != r:
                erros.append(i // r)

        return resultado, erros
