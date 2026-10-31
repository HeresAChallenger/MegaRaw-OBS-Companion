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

## Criar a primeira release (GitHub Actions)

O workflow [Publish Windows release](../.github/workflows/release.yml) cria o ZIP Windows a partir dos arquivos versionados e publica a release `v1.4.0` sem upload manual.

1. Abra **Actions** no GitHub.
2. Selecione **Publish Windows release**.
3. Clique em **Run workflow → main → Run workflow**.
4. Aguarde a conclusão verde e abra **Releases**.
5. Confira o arquivo `MegaRaw_OBS_Companion_v1.4.0_Windows.zip` e as notas de lançamento.

O workflow executa testes, não inclui arquivos privados e usa o token temporário do GitHub Actions com `contents: write`. Não execute novamente se a release já existir.

Se a criação de releases pelo Actions estiver bloqueada, use **Releases → Draft a new release**, tag `v1.4.0`, título `MegaRaw OBS Companion v1.4.0`, a descrição de `RELEASE_NOTES.md` e anexe manualmente o ZIP Windows.

## Próximos passos opcionais

- Criar Issues templates para relatórios.
- Adicionar screenshots feitas com alertas demonstrativos, sem informações de terceiros.
- Avaliar outros idiomas e personalização visual sem comprometer o modo já estável.
