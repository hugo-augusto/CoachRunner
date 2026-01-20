# 🏃 CoachRunner Pro

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**CoachRunner Pro** é um sistema de planejamento de treinos de corrida via linha de comando (CLI). Ele atua como um treinador virtual inteligente, utilizando algoritmos para determinar o nível técnico do atleta e gerar planilhas semanais personalizadas, baseadas em metodologias científicas de treinamento esportivo.


## 📸 Screenshots

*(Adicione um print do seu terminal aqui para mostrar a interface colorida)*

## 🎯 Funcionalidades Principais

* **📊 Análise de Perfil:** Algoritmo que classifica o corredor (Amador a Elite) baseado no tempo de referência de 5km.
* **⏱️ Calculadora de Pace:** Conversão automática de tempo decimal para sexagesimal (ex: converte o cálculo interno `3.8` para `3:48 min/km`).
* **📅 Geração de Planilha:** Criação dinâmica de treinos semanais (Rodagem, Intervalado, Fartlek, Longão) respeitando a disponibilidade do usuário.
* **💾 Persistência de Dados:** Sistema de Save/Load utilizando JSON para armazenar múltiplos perfis de atletas.
* **🎨 Interface Rica:** Uso de códigos ANSI para uma experiência de terminal colorida e organizada.
* **📚 Embasamento Científico:** Treinos baseados em zonas de frequência e intensidade (Jack Daniels, Billat, Seiler).

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3 (100% Bibliotecas Padrão).
* **Armazenamento:** JSON.
* **Automação:** GNU Make (Makefile).
* **Paradigma:** Orientação a Objetos (Classes `Runner`, `TrainingType`, `CoachRunnerPro`).

## 🚀 Como Executar

Este projeto foi desenhado para ser leve, sem necessidade de instalar bibliotecas externas (`pip install` não é necessário).

### Pré-requisitos

* Python 3.x instalado.
* (Opcional) `Make` para utilizar os comandos de automação.

### Passo a Passo

1.  Clone o repositório:
    ```bash
    git clone [https://github.com/SEU_USUARIO/coachrunner-pro.git](https://github.com/SEU_USUARIO/coachrunner-pro.git)
    cd coachrunner-pro
    ```

2.  Execute utilizando o Makefile (Recomendado):
    ```bash
    make run
    ```

    *Ou execute diretamente com Python:*
    ```bash
    python3 coachrunner.py
    ```

## ⚙️ Comandos do Makefile

Para facilitar o desenvolvimento e manutenção, o projeto inclui um `Makefile`:

| Comando | Descrição |
| :--- | :--- |
| `make run` | Inicia a aplicação CLI. |
| `make clean` | Remove arquivos de cache (`__pycache__`, `.pyc`). |
| `make clean-data` | **Cuidado:** Apaga o banco de dados (`runners_data.json`) resetando o sistema. |
| `make check` | Executa verificação de sintaxe e tipos (Type Hints). |

## 📐 Estrutura do Projeto

```text
coachrunner-pro/
├── coachrunner.py      # Código fonte principal (Core Logic)
├── Makefile            # Automação de tarefas
├── runners_data.json   # Banco de dados (gerado automaticamente)
└── README.md           # Documentação
