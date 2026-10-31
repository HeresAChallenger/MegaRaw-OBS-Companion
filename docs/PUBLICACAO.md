# Publicar no GitHub

Repositório sugerido: `HeresAChallenger/MegaRaw-OBS-Companion`

## Criar o projeto

1. Acesse https://github.com/new e escolha **Owner: HeresAChallenger**.
2. Use o nome **`MegaRaw-OBS-Companion`**, descrição sugerida:
   `Overlay independente de conquistas RetroAchievements para OBS e Mega Drive original / Unofficial RetroAchievements OBS overlay.`
3. Marque **Public** e crie **sem inicializar README, .gitignore ou licença**, pois todos estão nesta pasta.
4. No terminal, abra a pasta que contém este `README.md` e execute:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial release: MegaRaw OBS Companion 1.4.0"
git remote add origin https://github.com/HeresAChallenger/MegaRaw-OBS-Companion.git
git push -u origin main
```

Se o Git indicar identidade ausente, configure `git config --global user.name` e `git config --global user.email` com os dados que deseja utilizar para commits. Para autenticar, use o navegador ou Git Credential Manager; **nunca insira um token no arquivo de código ou no endereço remoto**.

## Criar a primeira release

1. No repositório, abra **Releases → Draft a new release**.
2. Tag: `v1.4.0`; título: `MegaRaw OBS Companion v1.4.0`.
3. Use a descrição em `RELEASE_NOTES.md`.
4. Anexe o ZIP de distribuição (que contém apenas o auxiliar, a documentação e o áudio CC0).
5. Confira antes de publicar se não há nenhum segredo, log privado, executável ou arquivo do MEGA-RAW.

## Próximos passos opcionais

- Criar Issues templates para relatórios.
- Adicionar screenshots feitas com alertas demonstrativos, sem informações de terceiros.
- Avaliar outros idiomas e personalização visual sem comprometer o modo já estável.
