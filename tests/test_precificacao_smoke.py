import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from precificacao_dinamica import calcular_novo_preco


class PrecificacaoSmokeTests(unittest.TestCase):
    def test_calcular_novo_preco_returns_zero_for_invalid_cost(self):
        self.assertEqual(calcular_novo_preco(0), 0.0)
        self.assertEqual(calcular_novo_preco(-10), 0.0)

    def test_calcular_novo_preco_generates_psychological_price(self):
        novo_preco = calcular_novo_preco(100.0, margem_alvo=0.35)
        self.assertGreater(novo_preco, 0)
        centavos = int(round((novo_preco - int(novo_preco)) * 100))
        self.assertEqual(centavos, 90)


if __name__ == "__main__":
    unittest.main()
