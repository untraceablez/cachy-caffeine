# cachy-caffeine

*[Read in English](README.md)*

Um "modo cafeína" simples pra Linux (feito e testado no CachyOS/Arch + KDE Plasma),
igual o Caffeine do macOS: um ícone na bandeja que, quando ativado, impede a tela de
bloquear e o PC de suspender sozinho por inatividade.

Ícone de xícara cheia com fumaça = ativo. Contorno cinza vazio = inativo.

## Como funciona

- Ícone na bandeja via `AyatanaAppIndicator3` (GTK/PyGObject), apontando pra pasta
  `icons/` deste próprio repositório (`set_icon_theme_path`), então nunca depende do
  tema de ícones do sistema conseguir resolver ele
- As atualizações de ícone passam por `set_icon_full()`, que garante que o painel
  redesenha corretamente a cada mudança de estado
- Ativar dispara um `systemd-inhibit --what=idle:sleep` em background — esse é o
  mecanismo real que bloqueia suspensão/bloqueio, não o script em si
- Desativar (ou fechar o app) mata esse processo, e o comportamento normal de
  bloqueio/suspensão volta; a mesma limpeza roda automaticamente se o app fechar
  de qualquer jeito, então nunca fica um inibidor órfão rodando
- O estado nunca é persistido entre reinícios — sempre volta desativado, por design
  (igual ao Caffeine do Mac)

## Dependências

- Python 3
- PyGObject (`python-gobject` no Arch)
- `libayatana-appindicator` (ou `libappindicator-gtk3` como fallback)
- `systemd` (para o `systemd-inhibit`)

```bash
sudo pacman -S python-gobject libayatana-appindicator
```

## Instalar

```bash
./install.sh
```

Isso copia os arquivos para `~/.local/share/cachy-caffeine`, cria o comando
`cachy-caffeine` em `~/.local/bin`, e registra o autostart em
`~/.config/autostart/cachy-caffeine.desktop` (abre sozinho a cada login), além de
uma entrada no menu de aplicativos.

## Desinstalar

```bash
./uninstall.sh
```

## Uso

Clique no ícone da bandeja para abrir o menu e escolher "Enable caffeine" /
"Disable caffeine".
