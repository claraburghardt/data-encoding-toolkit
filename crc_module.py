class CRC4:
    """
    CRC-4 (Cyclic Redundancy Check).

    Polinômio gerador obrigatório: G(x) = x^4 + x + 1
    Representação binária: 10011

    Funcionamento:
        - Geração: divide a mensagem (+ 4 zeros) pelo polinômio via XOR
          e obtém o resto (4 bits = CRC)
        - Transmissão: anexa o CRC ao final da mensagem
        - Verificação: divide a mensagem recebida (com CRC) pelo polinômio;
          se o resto for 0000, não há erro detectado
    """

    POLINOMIO = "10011"  # x^4 + x + 1

    def _xor(self, a: str, b: str) -> str:
        """XOR bit a bit entre duas strings de mesmo tamanho."""
        return "".join("0" if a[i] == b[i] else "1" for i in range(len(a)))

    def _divisao_binaria(self, dividendo: str, divisor: str) -> str:
        """
        Realiza a divisão binária (módulo 2) e retorna o resto.

        Parâmetros:
            dividendo: string binária (mensagem + zeros de padding)
            divisor: string binária (polinômio gerador)

        Retorna:
            resto com len(divisor) - 1 bits
        """
        grau = len(divisor)
        resto = dividendo[:grau]

        for i in range(grau, len(dividendo) + 1):
            if resto[0] == "1":
                resto = self._xor(resto, divisor)
            else:
                resto = self._xor(resto, "0" * grau)

            # Remove o bit mais significativo e adiciona o próximo bit
            if i < len(dividendo):
                resto = resto[1:] + dividendo[i]
            else:
                resto = resto[1:]

        return resto  # 4 bits

    def encoder(self, bits: str) -> tuple:
        """
        Gera o CRC e retorna a mensagem com CRC anexado.

        Parâmetros:
            bits: string binária (mensagem original)

        Retorna:
            tuple (mensagem_com_crc: str, crc: str)
            - mensagem_com_crc: mensagem original + 4 bits de CRC
            - crc: os 4 bits de redundância gerados
        """
        if not bits or not all(c in "01" for c in bits):
            raise ValueError("A entrada deve ser uma string binária (0s e 1s).")

        # Acrescenta 4 zeros ao final (grau do polinômio)
        dividendo = bits + "0000"

        crc = self._divisao_binaria(dividendo, self.POLINOMIO)
        mensagem_com_crc = bits + crc

        return mensagem_com_crc, crc

    def verificar(self, bits: str) -> tuple:
        """
        Verifica se há erro na mensagem recebida (mensagem + CRC).

        Parâmetros:
            bits: string binária com CRC anexado

        Retorna:
            tuple (sem_erro: bool, resto: str)
            - sem_erro: True se o resto for '0000' (nenhum erro detectado)
            - resto: os 4 bits do resto da divisão
        """
        if not bits or not all(c in "01" for c in bits):
            raise ValueError("A entrada deve ser uma string binária (0s e 1s).")

        if len(bits) <= 4:
            raise ValueError("A entrada deve ter mais de 4 bits (mensagem + CRC).")

        resto = self._divisao_binaria(bits, self.POLINOMIO)
        sem_erro = resto == "0000"

        return sem_erro, resto
