# Projeto Final

Este é o projeto que fecha a disciplina. Ao longo do semestre, os projetos individuais treinaram fatias separadas do ciclo de um sistema de ML; aqui você vai juntar todas elas em um único trabalho, do começo ao fim: escolher um problema real, encontrar e tratar os dados, treinar um modelo e colocá-lo no ar — funcionando, acessível e demonstrável por qualquer pessoa.

Você trabalhará individual ou em equipe (até 5 pessoas). A regra de ouro é pense pequeno e completo, não grande e pela metade: é melhor um sistema simples que funciona de ponta a ponta do que uma ideia ambiciosa.

Para começar, escolha uma das trilhas a seguir. As Trilhas 1 a 3 já vêm com um problema e um conjunto de dados sugeridos, bom para quem quer ir direto ao ponto. A Trilha 4 é aberta: você propõe o próprio problema, no tema que quiser, e encontra os dados. Em qualquer trilha, a régua de saída é a mesma: **problema real, dado com fonte e licença claras, modelo treinado e sistema no ar e confiável até o Demo Day.**


> **Escolha sua trilha antes de começar:** [Ver as trilhas disponíveis](trilhas.md)


**Data da entrega: 13/07/26**

---

## O que você precisa fazer nesse projeto?

Independentemente da trilha, o trabalho é o mesmo caminho: levar uma ideia do problema até um sistema de ML que qualquer pessoa abre e usa. No fim, esse sistema precisa ser **deployable** e **reliable**.

#### Deployable → qualquer um pode usar

- Empacotado (Docker) e sobe com um comando.
- Uma pessoa de fora consegue usar sem você do lado explicando.
- Reproduzível: outra equipe faz clone → comando → sistema sobe.

#### Reliable → suporte para o mundo real

- Não quebra com entrada inválida, vazia ou inesperada — o sistema valida antes de processar.
- Tem um **fallback / degradação graciosa**: o que o sistema faz quando o modelo está fora do ar, uma API externa cai ou a resposta demora demais? (Ex.: devolver uma resposta padrão e avisar, em vez de estourar um erro.)
- Não mostra erro técnico cru para o usuário.
- Responde em tempo aceitável.

### O caminho do trabalho

1. **Enquadre o problema.** Defina a métrica de sucesso de negócio (o que conta como "deu certo" para o stakeholder) e a métrica técnica que você vai otimizar. Deixe claro quem usa o sistema e como.
2. **Prepare os dados.** Registre origem, licença, vieses conhecidos e como você limpou e dividiu o dado. Cuidado com **vazamento de dado** (treinar com informação que não existiria no momento da previsão).
3. **Construa e itere o modelo.** Comece por um baseline simples e melhore a partir dele. Registre seus experimentos (MLflow ou equivalente) e guarde o que **NÃO** funcionou, as tentativas falhas entram no relatório e contam pontos.
4. **Avalie de verdade.** Defina critérios de sucesso, monte um conjunto de teste e meça com métricas adequadas ao problema (não basta acurácia, pense em precisão/recall, erro, custo de cada tipo de erro). 
5. **Coloque em produção.** Empacote o sistema, exponha um ponto de uso e hospede em um serviço acessível por link.
6. **Monitore.** Deixe o sistema registrar o que está acontecendo: logs/traces das previsões, uma métrica de saúde, e um esboço de detecção de deriva (o dado de produção começou a fugir do dado de treino?).

> **DICA:** Use Spec Driven Development (SDD) como apresentamos em sala de aula.


## O que você entrega no fim

- O **relatório** no template.
- O **repositório**.


## Avaliação e entrega

### 1. O relatório

Cada equipe entrega um report (pode ser um `.md` ou um site) que vira página pública. Ele não é uma formalidade no fim: é onde você mostra as decisões que tomou e por quê. Um bom relatório permite que alguém entenda e avalie seu sistema sem precisar abrir o código. Cada seção abaixo diz o que esperamos.

#### Cabeçalho

Logo no topo, deixe o essencial visível: o link da aplicação ao vivo (com QR code), o link do repositório no GitHub e os integrantes da equipe.

#### Definição do problema

Descreva o problema que vocês estão resolvendo, dizendo qual trilha e qual projeto escolheram (ou, na Trilha 4, qual problema propuseram). Responda:

- Que dor é essa e por que importa?
- Quem são os stakeholders (os grupos que usam ou são afetados pelo sistema)?
- Qual a métrica de sucesso, tanto a de **negócio** (o que faz o stakeholder considerar que deu certo) quanto a **técnica**?

#### Como o sistema é montado

Aqui você descreve a engenharia da solução. Inclua:

- um **diagrama de arquitetura** mostrando as peças (entrada → modelo → resposta) e como elas se conectam;
- **model exploration:** quais abordagens vocês consideraram antes de decidir;
- **model/app deployment:** onde e como o sistema está hospedado, e como ele recebe os dados de inferência no ar;
- **CI/CD (se houver):** o que é testado ou implantado automaticamente. Mostre também a estratégia de confiabilidade: o que acontece quando uma dependência falha (o fallback).

#### Descrição do modelo

- **Datasets:** qual dado vocês usaram, origem, licença e o tratamento que fizeram.
- **Feature selection:** quais variáveis entraram no modelo e por quê.
- **Iterações do modelo:** o caminho do baseline simples até a versão final, incluindo o que não funcionou. Tentativas falhas bem explicadas contam pontos — mostram que vocês raciocinaram, não chutaram. Cuidado em deixar claro como evitaram vazamento de dado.

#### Avaliação do sistema

Esta seção responde à pergunta: **como vocês sabem que o sistema funciona?** Apresente:

- **Performance:** os critérios de sucesso, o conjunto de teste e as métricas adequadas ao problema (não basta acurácia — precisão/recall, erro, custo de cada tipo de erro, latência e, se usar API paga, custo por chamada).
- **UX:** a experiência de quem usa (é claro? rápido? o que acontece quando o sistema erra ou não tem certeza?).

#### Demonstração

Grave um vídeo demonstrando o sistema funcionando em casos de uso reais, passo a passo (prints ou GIFs). Pegue um usuário típico e siga o fluxo dele do início ao resultado. O objetivo é deixar claro o que o sistema faz na prática, não em teoria.

#### Reflexão sobre o que aprenderam

Sejam honestos. O que funcionou bem? O que não funcionou como planejado (decisões que voltaram atrás, limitações do dado, coisas que ficaram de fora)? E próximos passos: o que vocês fariam com mais tempo?

#### Impactos e ética

Pensando no seu problema (não em ética genérica): quem pode ser prejudicado por um erro do sistema, e como? Há risco de viés entre grupos (gênero, região, renda)? Há questões de privacidade ou segurança no dado ou no uso? O que vocês fizeram (ou recomendam fazer) para mitigar isso?

#### Referências

Dados, modelos, bibliotecas e materiais que vocês usaram.

---

## Datas e submissão

**Data da entrega: 13/07/26**

**Como submeter:**

1. Dentro da pasta do projeto final (projeto-final-2026-1), crie a subpasta no formato `(X-Y_nome_integrantes)`, onde **X** representa a trilha e **Y** o projeto;
2. Coloque todos os entregáveis dentro dessa pasta;
3. Abra um Pull Request para submissão seguindo o mesmo padrão da pasta: `(X-Y_nome_integrantes)`;