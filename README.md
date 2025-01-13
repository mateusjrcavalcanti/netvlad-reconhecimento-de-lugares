# NetVLAD VPR

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/UI-Gradio-F97316)
![PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![Torchvision](https://img.shields.io/badge/Backbone-ResNet--18-4B8BBE)
![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/tests-unittest-brightgreen)
![Status](https://img.shields.io/badge/status-prot%C3%B3tipo-blue)

Aplicação de **reconhecimento visual de lugares** usando descritores NetVLAD.

Projeto realizado na disciplina **Tópicos Avançados em Automação**, do curso de **Engenharia de Computação** da **UNIVASF**, no período **2024.1**.

O projeto permite visualizar um dataset rotulado, gerar descritores visuais para imagens de referência e reconhecer o local mais parecido a partir de uma imagem enviada pelo usuário.

## 👥 Autores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/mateusjrcavalcanti">
        <img src="https://avatars.githubusercontent.com/u/111059128?v=4" width="100px;" alt="Mateus Cavalcanti"/>
        <br />
        <sub><b>Mateus Cavalcanti</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://github.com/rodrigo-barboza">
        <img src="https://avatars.githubusercontent.com/u/62775400?v=4" width="100px;" alt="Rodrigo Barboza"/>
        <br />
        <sub><b>Rodrigo Barboza</b></sub>
      </a>
    </td>
  </tr>
</table>

## ✨ Funcionalidades

- 🖼️ Visualização das imagens do dataset agrupadas por classe/local.
- 🧠 Extração de descritores com ResNet-18 + NetVLAD.
- 💾 Armazenamento dos descritores em SQLite como BLOBs NumPy.
- 🔍 Reconhecimento visual por distância euclidiana.
- 🧭 Interface Gradio organizada em ordem de uso.
- 🔒 Aba de reconhecimento liberada apenas após a preparação dos descritores.
- 🔁 Hot reload para desenvolvimento.
- 🧪 Testes automatizados com `unittest`.
- 🛠️ Script Python para regenerar o CSV de labels.

## 🧩 Como Funciona

O fluxo lógico da aplicação é:

1. O arquivo `dataset/labeled_dataset.csv` associa cada imagem a uma classe/local.
2. A aba **1. Dataset** usa esse CSV para exibir as imagens agrupadas.
3. A aba **2. Preparar descritores** percorre as imagens do CSV.
4. Cada imagem é processada por ResNet-18 e pela camada NetVLAD.
5. O descritor resultante é salvo em `data/database.db`.
6. A aba **3. Reconhecer lugar** recebe uma imagem de consulta.
7. A imagem de consulta passa pelo mesmo pipeline de descritores.
8. O sistema compara a consulta com os descritores salvos.
9. A classe/local com menor distância é retornada como melhor correspondência.

## ✅ Pré-requisitos

- Python 3.12 ou superior.
- Sistema com espaço suficiente para instalar PyTorch.
- Acesso à internet na primeira instalação das dependências e, se necessário, para baixar pesos da ResNet-18.

## 🚀 Como Executar

Na raiz do projeto, crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Instale as dependências:

```bash
.venv/bin/pip install -r requirements.txt
```

Inicie a aplicação:

```bash
.venv/bin/python app/main.py
```

Abra no navegador:

```text
http://localhost:3000
```

## 🔁 Desenvolvimento com Hot Reload

Para desenvolver a interface e recarregar alterações automaticamente:

```bash
.venv/bin/gradio app/main.py --watch-dirs app
```

## 🧪 Passo a Passo Para Testar Pela Interface

1. Abra `http://localhost:3000`.
2. Acesse a aba **1. Dataset** e confira as classes/imagens disponíveis.
3. Vá para **2. Preparar descritores**.
4. Clique em **Gerar descritores do dataset**.
5. Aguarde a geração terminar.
6. A aba **3. Reconhecer lugar** será liberada.
7. Envie uma imagem de consulta.
8. Clique em **Reconhecer**.
9. Confira a melhor classe/local e a tabela de correspondências.

## 🗂️ Dataset e Labels

As imagens de referência ficam em:

```text
dataset/
```

O CSV de labels fica em:

```text
dataset/labeled_dataset.csv
```

Formato atual:

```csv
frame00041.png;bancadas_a;
```

Esse CSV é usado para:

- montar a galeria da aba **Dataset**;
- decidir quais imagens processar na geração dos descritores;
- salvar a classe/local junto com cada descritor.

Para regenerar o CSV a partir dos nomes dos frames:

```bash
python3 scripts/generate_labeled_dataset.py
```

## 🧠 Descritores e Modelo

O pipeline de extração usa:

- **ResNet-18** com pesos ImageNet do `torchvision`;
- **NetVLAD** para agregar as features visuais;
- **distância euclidiana** para comparar descritores.

Durante a execução, ResNet-18 e NetVLAD ficam carregados em memória. Isso evita recriar o modelo para cada imagem.

A camada NetVLAD usa seed fixa por padrão, o que torna o comportamento determinístico durante o processo da aplicação.

## 🎯 Pesos Treinados de NetVLAD

Por padrão, a camada NetVLAD é determinística, mas não treinada.

Para usar pesos treinados, coloque um checkpoint compatível em:

```text
data/netvlad_checkpoint.pt
```

Esse arquivo é ignorado pelo Git porque é um artefato local.

## 💾 Banco Local

Os descritores são armazenados em:

```text
data/database.db
```

Detalhes:

- o banco é criado automaticamente;
- descritores são salvos como BLOBs NumPy;
- o arquivo é ignorado pelo Git;
- se o schema antigo usava JSON/TEXT, a tabela de descritores é recriada automaticamente.

## 🧪 Testes Automatizados

Execute:

```bash
.venv/bin/python -m unittest discover -s tests
```

Os testes cobrem:

- geração do CSV de labels;
- resumo/validação do dataset;
- round-trip de descritores como BLOB no SQLite.

## 🧱 Estrutura do Projeto

```text
app/
  main.py         ponto de entrada da aplicação Gradio
  config.py       caminhos compartilhados
  database.py     armazenamento dos descritores em SQLite
  datasets.py     leitura do CSV, galeria e geração de descritores
  recognition.py  upload da consulta e comparação dos descritores
  ui.py           interface Gradio e callbacks
  netvlad/        modelo NetVLAD, comparador e extração de features

dataset/          imagens de referência versionadas
data/             estado local gerado, ignorado pelo Git
scripts/          scripts de manutenção
tests/            testes automatizados
```

## 🧯 Problemas Comuns

### A aba de reconhecimento não aparece

Gere os descritores primeiro na aba **2. Preparar descritores**.

### O banco mostra zero descritores

Isso pode acontecer após mudança de schema ou limpeza do banco local. Gere os descritores novamente.

### A primeira execução demora

PyTorch e os pesos da ResNet-18 podem ser carregados/baixados na primeira execução. Depois disso, o processo tende a ficar mais rápido.

### O CSV não bate com as imagens

Rode:

```bash
python3 scripts/generate_labeled_dataset.py
```

Depois atualize o status na aba **2. Preparar descritores**.
