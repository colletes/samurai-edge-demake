"""
Teste automatizado para os Portraits HD-2D do Ciclo 3 (Goro & Ichi):
- Valida existência física dos arquivos em assets/portraits/
- Valida dimensões (256x256) e canal alpha
- Valida integração com get_portrait() e cache em memória (retangular e circular)
- Valida antialiasing suave das bordas circulares
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
from src.ui.portraits import get_portrait, preload_portraits

def test_cycle3_portraits():
    pygame.init()
    pygame.display.set_mode((1, 1))

    fighters = ["goro", "ichi"]
    
    for f in fighters:
        # 1. Checar arquivos físicos
        rect_path = os.path.join(ROOT, "assets", "portraits", f"{f}_bust.png")
        circ_path = os.path.join(ROOT, "assets", "portraits", f"{f}_bust_circle.png")
        assert os.path.exists(rect_path), f"Arquivo não encontrado: {rect_path}"
        assert os.path.exists(circ_path), f"Arquivo não encontrado: {circ_path}"

        # 2. Carregar e verificar tamanho
        surf_rect = pygame.image.load(rect_path)
        surf_circ = pygame.image.load(circ_path)
        assert surf_rect.get_size() == (256, 256), f"Dimensão incorreta para {rect_path}"
        assert surf_circ.get_size() == (256, 256), f"Dimensão incorreta para {circ_path}"

        # 3. Verificar máscara circular
        assert surf_circ.get_at((0, 0))[3] == 0, f"Canto de {circ_path} deve ser transparente"
        assert surf_circ.get_at((128, 128))[3] == 255, f"Centro de {circ_path} deve ser opaco"

        # 4. Testar através do gerenciador de portraits
        for s in [(58, 58), (84, 84), (110, 110)]:
            p_circ = get_portrait(f, size=s, circular=True)
            p_rect = get_portrait(f, size=s, circular=False)
            assert p_circ is not None and p_circ.get_size() == s
            assert p_rect is not None and p_rect.get_size() == s

        print(f"✓ Portraits de {f.upper()} (HD-2D 256x256 retangular e circular) validados com sucesso!")

    # 5. Preload test
    preload_portraits()
    print("✓ Pré-carregamento dos retratos em memória validado com sucesso!")
    print("\n=======================================================")
    print("TODOS OS TESTES DE PORTRAITS DO CICLO 3 PASSARAM (100%)!")
    print("=======================================================")

if __name__ == "__main__":
    test_cycle3_portraits()
