# Reconhecimento Visual de Lugares com NetVLAD

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![Gradio](https://img.shields.io/badge/UI-Gradio-F97316)
![PyTorch](https://img.shields.io/badge/ML-PyTorch-EE4C2C?logo=pytorch&logoColor=white)
![Torchvision](https://img.shields.io/badge/Backbone-ResNet--18-4B8BBE)
![SQLite](https://img.shields.io/badge/Storage-SQLite-003B57?logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/tests-unittest-brightgreen)
![Status](https://img.shields.io/badge/status-prot%C3%B3tipo-blue)

Aplicação de **reconhecimento visual de lugares** usando descritores NetVLAD.

Projeto realizado na disciplina **Tópicos Avançados em Automação**, do curso de **Engenharia de Computação** da **UNIVASF**, no período **2024.1**.

O projeto permite visualizar e gerenciar datasets rotulados, gerar descritores visuais para imagens de referência e reconhecer o local mais parecido a partir de uma imagem enviada pelo usuário.

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
- 🗃️ Datasets organizados em `datasets/<dataset>/<classe>/`.
- ➕ Criação e remoção de datasets pela interface.
- 🏷️ Criação, renomeação e remoção de classes do dataset ativo.
- 📤 Upload e remoção de imagens na classe ativa.
- 🎞️ Extração de frames de vídeo por intervalos de tempo e classe.
- 🧠 Extração de descritores com ResNet-18 + NetVLAD.
- 💾 Armazenamento dos descritores em SQLite como BLOBs NumPy, separado por dataset.
- 🔍 Reconhecimento visual por distância euclidiana.
- 🖼️ Exibição da imagem de referência mais próxima no reconhecimento.
- 🧭 Interface Gradio organizada em ordem de uso.
- 🔒 Aba de reconhecimento liberada apenas após a preparação dos descritores.
- 🧾 Status visual por campos separados para descritores, classes, imagens, banco e próximo passo.
- 🔁 Hot reload para desenvolvimento.
- 🧪 Testes automatizados com `unittest`.

## 🧩 Como Funciona

O fluxo lógico da aplicação é:

1. A aba **1. Datasets** concentra a preparação dos dados.
2. Em **Ver datasets**, o usuário seleciona o dataset ativo e navega pelas classes/locais existentes.
3. O botão **Editar dataset** abre as ações do dataset ativo: classes, imagens, vídeo e remoção do dataset.
4. Em **Novo dataset**, o usuário cria um dataset vazio sem misturar o formulário de criação com a visualização de um dataset existente.
5. A edição do dataset ativo também pode extrair frames de um vídeo para classes definidas por intervalo de tempo.
6. A aba **2. Preparar descritores** percorre as imagens do dataset ativo.
7. Cada imagem é processada por ResNet-18 e pela camada NetVLAD.
8. O descritor resultante é salvo no banco SQLite daquele dataset.
9. A aba **3. Reconhecer lugar** recebe uma imagem de consulta.
10. A imagem de consulta passa pelo mesmo pipeline de descritores.
11. O sistema compara a consulta com os descritores salvos do dataset ativo.
12. A classe/local com menor distância é retornada, junto com a imagem de referência mais próxima e o top de correspondências.

## ✅ Pré-requisitos

- Python 3.12 ou superior.
- Sistema com espaço suficiente para instalar PyTorch.
- Acesso à internet na primeira instalação das dependências e, se necessário, para baixar pesos da ResNet-18.
- `opencv-python-headless` para extrair frames de vídeo.

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
2. Acesse a aba **1. Datasets**.
3. Em **Ver datasets**, selecione o dataset ativo.
4. Use o seletor **Classe/local** para conferir as imagens já cadastradas.
5. Para alterar o dataset ativo, clique em **Editar dataset**.
6. Em **Classes**, crie, renomeie ou remova classes/locais.
7. Em **Imagens**, envie imagens para a classe ativa ou remova uma imagem existente.
8. Em **Vídeo**, envie um vídeo, defina os intervalos de início/fim e informe a classe de destino de cada intervalo.
9. Em **Novo dataset**, crie outro dataset quando quiser começar uma base do zero.
10. Vá para **2. Preparar descritores**.
11. Clique em **Gerar descritores do dataset ativo**.
12. Aguarde a geração terminar.
13. A aba **3. Reconhecer lugar** será liberada para o dataset selecionado.
14. Envie uma imagem de consulta.
15. Clique em **Reconhecer**.
16. Confira a melhor classe/local, a imagem de referência mais próxima e a tabela de correspondências.

## 🗂️ Datasets

Os datasets ficam em:

```text
datasets/<nome_do_dataset>/<classe>/<imagem>
```

Exemplo:

```text
datasets/laboratorio_robotica/porta/frame02001.png
datasets/laboratorio_robotica/corredor/frame00721.png
```

O dataset atual foi migrado para esse padrão em `datasets/laboratorio_robotica/`, com uma subpasta para cada classe/local. O projeto não depende mais de um CSV de rótulos: a classe de cada imagem é definida pela pasta onde ela está.

Nomes de datasets e classes devem usar letras, números, hífen ou underscore, sem espaços.

## 🎞️ Extração de Frames de Vídeo

Na aba **1. Datasets > Ver datasets**, selecione o dataset ativo e clique em **Editar dataset**. Em seguida, abra a subaba **Vídeo** e informe:

- arquivo de vídeo;
- frames por segundo;
- intervalos com início, fim e classe.

Ao extrair, os frames são salvos diretamente em:

```text
datasets/<nome_do_dataset>/<classe>/frame_<tempo>.jpg
```

Classes informadas nos intervalos são criadas automaticamente quando ainda não existem.

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

Cada dataset usa um banco SQLite próprio:

```text
data/descriptors/<dataset>.db
```

Detalhes:

- o banco é criado automaticamente;
- descritores são salvos como BLOBs NumPy;
- os arquivos são ignorados pelo Git;
- se o schema antigo usava JSON/TEXT, a tabela de descritores é recriada automaticamente.

## 🧪 Testes Automatizados

Execute:

```bash
.venv/bin/python -m unittest discover -s tests
```

Os testes cobrem:

- listagem e resumo de datasets por diretório;
- remoção de imagem/classe;
- validação de intervalos de vídeo;
- round-trip de descritores como BLOB no SQLite.

## 🧱 Estrutura do Projeto

```text
app/
  main.py         ponto de entrada da aplicação Gradio
  config.py       caminhos compartilhados
  database.py     armazenamento dos descritores em SQLite
  datasets.py     leitura/gestão de datasets, galeria e geração de descritores
  recognition.py  upload da consulta e comparação dos descritores
  ui.py           interface Gradio e callbacks
  netvlad/        modelo NetVLAD, comparador e extração de features

datasets/         datasets versionados por diretório/classe
data/             estado local gerado, ignorado pelo Git
tests/            testes automatizados
```

## 🧯 Problemas Comuns

### A aba de reconhecimento não aparece

Gere os descritores primeiro na aba **2. Preparar descritores**.

### O banco mostra zero descritores

Isso pode acontecer após mudança de schema ou limpeza do banco local. Gere os descritores novamente.

### A primeira execução demora

PyTorch e os pesos da ResNet-18 podem ser carregados/baixados na primeira execução. Depois disso, o processo tende a ficar mais rápido.
