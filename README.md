# OverPoke 🟢

Overlay estilo Pokémon com contador e GIFs, criado em Python com **PyQt6**.  
Permite adicionar overlays transparentes sobre qualquer janela, incluindo jogos, com contador em estilo pixel atualizado por hotkey.

---

## Funcionalidades

- 🎨 Overlay transparente com GIF animado.  
- 🔢 Contador estilo pixel, atualizado por **hotkey**, funcionando até dentro de jogos.  
- 📏 Redimensionável e movível via drag e **resize handle pixel-style**.  
- 🖌 Vários temas: **FireRed**, **Emerald**, **Yellow**, **Minimal**.  
- 🔒 Lock/Unlock de overlays e hotkey configurável.  
- 🖥 System tray para acesso rápido e gerenciamento de overlays.  
- ➕ Suporte para múltiplos overlays simultâneos.

---

## Instalação

### Pré-requisitos

- **Python 3.11+**  
- Dependências Python:

```bash
pip install PyQt6 pynput
```
Como usar

Execute o script diretamente:

```bash
python overpoke.py
```

Ou utilize o .exe

OverPoke.exe

Uso

Clique no overlay ou use a hotkey configurada para incrementar o contador.

Arraste o overlay para mover.

Use o pixel resize handle no canto inferior direito para redimensionar.

System tray permite:

Mostrar/ocultar overlays

Fechar overlays

Alterar tema

Temas Disponíveis
Tema	Descrição
FireRed	Vermelho clássico Pokémon
Emerald	Verde estilo Pokémon Emerald
Yellow	Amarelo Pokémon Yellow
Minimal	Preto moderno minimalista
Contribuindo

Pull requests são bem-vindos!
Para bugs ou sugestões, abra uma issue no GitHub.
