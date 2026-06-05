class Hamming74:
    """
    Código de Hamming (7,4) — variação com paridade baseada no diagrama de Venn.

    Codifica blocos de 4 bits de dados em palavras de 7 bits,
    onde os 3 bits de paridade são calculados por sobreposição de conjuntos
    (diagrama de Venn), conforme ensinado em aula.

    Estrutura do codeword (7 bits):
        d1  d2  d3  d4  p1  p2  p3
    onde:
        p1 = d1 ^ d3 ^ d2   (cobre o círculo 1)
        p2 = d2 ^ d3 ^ d4   (cobre o círculo 2)
        p3 = d1 ^ d3 ^ d4   (cobre o círculo 3)

    Capacidade:
        - Detecta erros duplos (retorna lista com erro não corrigível)
        - Corrige 1 erro de bit por bloco
    """

    def _calcular_paridades(self, bits: list) -> str:
        """
        Calcula os 3 bits de paridade para um bloco de 4 bits de dados.

        bits: lista ou string de 4 inteiros (d1 d2 d3 d4)

        Retorna:
            string com 3 bits de paridade: p1 p2 p3
        """
        d1, d2, d3, d4 = map(int, bits)
        p1 = d1 ^ d3 ^ d2   # cobre s1, s3, s4
        p2 = d2 ^ d3 ^ d4   # cobre s2, s3, s4
        p3 = d1 ^ d3 ^ d4   # cobre s1, s2, s4
        return f"{p1}{p2}{p3}"


    def _verificar_e_corrigir(self, encoded_bits: str) -> tuple:
        """
        Verifica e corrige um bloco de 7 bits (4 dados + 3 paridade).

        Parâmetros:
            encoded_bits: string de 7 bits

        Retorna:
            tuple (data_bits: list, erro_info: dict ou None)
            - data_bits: lista dos 4 bits de dados (corrigidos se necessário)
            - erro_info: None se sem erro, dict com 'corrigido' e 'posicao' se houve erro
        """
        data_bits    = list(encoded_bits[:4])
        parity_bits  = list(encoded_bits[4:])
        calc_parity  = list(self._calcular_paridades(data_bits))

        mismatches = [i for i in range(3) if parity_bits[i] != calc_parity[i]]

        # Sem erros
        if len(mismatches) == 0:
            return data_bits, None

        # Erro duplo — não corrigível
        if len(mismatches) > 1:
            # Tenta identificar e corrigir erros nos bits de dados
            # (lógica original do professor, por sobreposição de paridades)
            p = parity_bits
            c = calc_parity

            # Erro no d1 (t1): p1 != c1, p2 == c2, p3 != c3
            if p[0] != c[0] and p[1] == c[1] and p[2] != c[2]:
                data_bits[0] = '1' if data_bits[0] == '0' else '0'
                return data_bits, {"posicao": 1, "corrigido": True}

            # Erro no d2 (t2): p1 != c1, p2 != c2, p3 == c3
            if p[0] != c[0] and p[1] != c[1] and p[2] == c[2]:
                data_bits[1] = '1' if data_bits[1] == '0' else '0'
                return data_bits, {"posicao": 2, "corrigido": True}

            # Erro no d4 (t4): p1 == c1, p2 != c2, p3 != c3
            if p[0] == c[0] and p[1] != c[1] and p[2] != c[2]:
                data_bits[3] = '1' if data_bits[3] == '0' else '0'
                return data_bits, {"posicao": 4, "corrigido": True}

            # Erro em d3 (t3) — afeta todos os três bits de paridade
            if p[0] != c[0] and p[1] != c[1] and p[2] != c[2]:
                data_bits[2] = '1' if data_bits[2] == '0' else '0'
                return data_bits, {"posicao": 3, "corrigido": True}

            # Padrão não reconhecido — erro múltiplo não corrigível
            return data_bits, {"posicao": -1, "corrigido": False}

        # Erro simples nos bits de paridade (apenas 1 mismatch) — corrige a paridade
        return data_bits, {"posicao": f"p{mismatches[0] + 1}", "corrigido": True}


    def encoder(self, bits: str) -> tuple:
        """
        Codifica uma string de bits usando Hamming (7,4).

        A entrada é dividida em blocos de 4 bits.
        Se o último bloco tiver menos de 4 bits, é completado com zeros à direita (padding).

        Parâmetros:
            bits: string binária (ex: '10110010')

        Retorna:
            tuple (string codificada, padding: int)
            - string codificada: blocos de 7 bits concatenados, separados por espaço
            - padding: quantos zeros foram adicionados ao último bloco
        """
        if not bits or not all(c in "01" for c in bits):
            raise ValueError("A entrada deve ser uma string binária (0s e 1s).")

        padding = (4 - len(bits) % 4) % 4

        blocos_codificados = []

        for i in range(0, len(bits), 4):
            bloco = bits[i:i + 4].ljust(4, "0")   # completa com zeros se necessário
            paridade = self._calcular_paridades(bloco)
            blocos_codificados.append(bloco + paridade)

        return " ".join(blocos_codificados), padding


    def decoder(self, bits: str, padding: int = 0) -> tuple:
        """
        Decodifica e corrige erros em uma string codificada com Hamming (7,4).

        Parâmetros:
            bits: string binária codificada (blocos de 7 bits, com ou sem espaços)
            padding: zeros adicionados no encoder (retornado pelo encoder)

        Retorna:
            tuple (dados_decodificados: str, erros: list)
            - dados_decodificados: string binária com apenas os bits de dados
            - erros: lista de dicts com 'bloco', 'posicao', 'corrigido'
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
            bloco_str  = bits[i:i + 7]
            bloco_idx  = i // 7

            data_bits, erro_info = self._verificar_e_corrigir(bloco_str)

            if erro_info is not None:
                erros.append({
                    "bloco":     bloco_idx,
                    "posicao":   erro_info["posicao"],
                    "corrigido": erro_info["corrigido"],
                })

            dados += "".join(data_bits)

        # Remove o padding adicionado no encoder
        if padding > 0:
            dados = dados[:-padding]

        return dados, erros
