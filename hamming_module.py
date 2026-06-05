class Hamming74:
    """
    Código de Hamming (7,4).

    Codifica blocos de 4 bits de dados em palavras de 7 bits,
    adicionando 3 bits de paridade nas posições 1, 2 e 4 (indexadas em 1).

    Estrutura do codeword (posições 1-7):
        p1  p2  d1  p3  d2  d3  d4
    onde p = bit de paridade, d = bit de dado.

    Capacidade:
        - Detecta até 2 erros de bit
        - Corrige 1 erro de bit por bloco (indica a posição exata)
    """

    # Posições dos bits de dados e paridade (indexadas em 1)
    _POS_DADOS    = [3, 5, 6, 7]
    _POS_PARIDADE = [1, 2, 4]

    def _calcular_paridades(self, bits: list) -> list:
        """
        Calcula os 3 bits de paridade para um bloco de 7 bits.
        Usa paridade par (XOR).

        bits: lista de 7 inteiros (0 ou 1), indexada em 0 (pos 0 = posição 1)
        """
        p1 = bits[2] ^ bits[4] ^ bits[6]   # posições 3, 5, 7
        p2 = bits[2] ^ bits[5] ^ bits[6]   # posições 3, 6, 7
        p3 = bits[4] ^ bits[5] ^ bits[6]   # posições 5, 6, 7
        return [p1, p2, p3]

    def encoder(self, bits: str) -> tuple:
        """
        Codifica uma string de bits usando Hamming (7,4).

        A entrada será dividida em blocos de 4 bits.
        Se o último bloco tiver menos de 4 bits, será completado com zeros à direita.

        Parâmetros:
            bits: string binária (ex: '10110010')

        Retorna:
            tuple (string codificada, padding: int)
            - string codificada: blocos de 7 bits concatenados
            - padding: quantos bits de zeros foram adicionados ao último bloco
        """
        if not bits or not all(c in "01" for c in bits):
            raise ValueError("A entrada deve ser uma string binária (0s e 1s).")

        padding = (4 - len(bits) % 4) % 4  # bits de zeros adicionados ao final

        resultado = ""
        for i in range(0, len(bits), 4):
            bloco = bits[i:i + 4].ljust(4, "0")
            d = [int(b) for b in bloco]  # d1 d2 d3 d4

            # Monta os 7 bits: posições 1,2 = paridade provisória 0, pos 3=d1,
            # pos 4=paridade provisória 0, pos 5=d2, pos 6=d3, pos 7=d4
            word = [0, 0, d[0], 0, d[1], d[2], d[3]]

            # Calcula e insere as paridades
            p1, p2, p3 = self._calcular_paridades(word)
            word[0] = p1  # posição 1
            word[1] = p2  # posição 2
            word[3] = p3  # posição 4

            resultado += "".join(str(b) for b in word)

        return resultado, padding

    def decoder(self, bits: str, padding: int = 0) -> tuple:
        """
        Decodifica e corrige erros em uma string codificada com Hamming (7,4).

        Parâmetros:
            bits: string binária codificada (comprimento deve ser múltiplo de 7)
            padding: bits de zeros adicionados no encoder (retornado pelo encoder)

        Retorna:
            tuple (dados_decodificados: str, erros: list)
        """
        bits = bits.replace(" ", "")

        if not bits or not all(c in "01" for c in bits):
            raise ValueError("A entrada deve ser uma string binária (0s e 1s).")

        if len(bits) % 7 != 0:
            raise ValueError(
                f"Tamanho da entrada ({len(bits)}) não é múltiplo de 7."
            )

        dados = ""
        erros = []

        for i in range(0, len(bits), 7):
            bloco_str = bits[i:i + 7]
            word = [int(b) for b in bloco_str]

            # Calcula síndrome: recalcula paridades e compara com as recebidas
            p1, p2, p3 = self._calcular_paridades(word)
            s1 = p1 ^ word[0]  # posição 1
            s2 = p2 ^ word[1]  # posição 2
            s3 = p3 ^ word[3]  # posição 4

            # Síndrome indica a posição do erro (em base 1)
            sindrome = s1 * 1 + s2 * 2 + s3 * 4

            bloco_idx = i // 7

            if sindrome != 0:
                if 1 <= sindrome <= 7:
                    # Corrige o bit na posição indicada
                    word[sindrome - 1] ^= 1
                    erros.append({
                        "bloco": bloco_idx,
                        "posicao": sindrome,
                        "corrigido": True
                    })
                else:
                    erros.append({
                        "bloco": bloco_idx,
                        "posicao": sindrome,
                        "corrigido": False
                    })

            # Extrai apenas os 4 bits de dados (posições 3, 5, 6, 7 → índices 2, 4, 5, 6)
            dados += str(word[2]) + str(word[4]) + str(word[5]) + str(word[6])

        # Remove o padding adicionado no encoder
        if padding > 0:
            dados = dados[:-padding]

        return dados, erros
