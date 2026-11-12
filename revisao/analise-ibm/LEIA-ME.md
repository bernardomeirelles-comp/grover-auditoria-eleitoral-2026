# Análise das repetições IBM

Esta pasta é produzida por `python analisar-repeticoes.py`, a partir dos exports locais do Composer e do CSV de calibração. O programa não acessa nem envia trabalhos à IBM. O arquivo `resumo.json` informa quais blocos já foram recebidos; a análise de três blocos só está completa quando `complete_three_block_design` é `true`.

## O que foi conferido

Os resultados brutos têm esquema v2.0. Cada registrador contém uma matriz booleana de forma `[1, 512, 2]`, compactada em bits, comprimida com zlib e codificada em base64. O decodificador preserva a ordem das 512 medições. As duas colunas formam a resposta exibida como `c1c0`.

O QASM físico veio do próprio arquivo de informações do trabalho. Seus cinco índices físicos são convertidos em cinco índices locais, sem transpilar novamente. A análise conserva o mapeamento de cada medida: esse mapeamento pode mudar entre segmentos. Cada segmento tem cinco resets e duas medidas. As probabilidades ideais são calculadas exatamente por matriz densidade, na ordem dos bits clássicos. Além disso, uma execução ideal da sequência completa verifica os 12 registradores conjuntamente, incluindo os resets. Os hashes do QASM de entrada são conferidos contra o protocolo anterior à submissão.

Os arquivos `*-validacao.json` registram cada mapeamento, distribuição ideal, contagem de operações, profundidade e hash dos exports. Os QASM físico e compactado são preservados. A profundidade por segmento inclui reset e medida; não é tempo de execução.

## Estatísticas

`resultados-por-bloco.csv` conserva as quatro contagens de cada segmento, a frequência de acerto e o intervalo marginal de Wilson de 95%. `resultados-agregados.csv` combina somente o mesmo alvo e a mesma implementação entre os blocos disponíveis, com pesos iguais porque todos têm 512 medições. Também preserva o mínimo e o máximo observados entre blocos.

Os 12 segmentos pertencem à mesma sequência dentro de cada shot. Não são 12 execuções independentes do equipamento. `comparacao-pareada.csv` mantém, para cada alvo e bloco, quantas medições tiveram sucesso em ambas as implementações, somente em uma delas ou em nenhuma. Os intervalos de Wilson descrevem a amostragem marginal sob a aproximação binomial; não incorporam toda a variação temporal ou a dependência entre segmentos. Não são intervalos simultâneos para todos os alvos.

O compilador pode escolher qubits físicos e sequências de portas diferentes para os blocos. Os arquivos de validação registram essas escolhas, e o modelo usa a calibração correspondente a cada uma. Diferenças entre blocos misturam mapeamento, compilação, ordem dos segmentos e momento da execução; não isolam a deriva temporal do equipamento.

Os controles preparam as quatro respostas conhecidas após reset. Seus erros reúnem preparação, reset e leitura. Por isso, não devem ser chamados de medidas isoladas do erro de leitura.

## Aproximação com a calibração

O CSV de 11/11/2026 às 10:07:21 UTC é anterior às novas execuções. O modelo usa os qubits e as conexões efetivamente presentes nos QASM físicos, com as seguintes etapas:

1. Para cada porta, aplica relaxação térmica a partir de T1, T2 e duração. A população excitada de equilíbrio é aproximada por zero; T2 é limitado a 2T1 quando necessário.
2. Calcula a infidelidade média desse canal e acrescenta somente a despolarização residual necessária para atingir a infidelidade publicada da porta. A infidelidade total não é somada novamente à relaxação. Quando a relaxação calculada já excede o erro publicado, conserva apenas a relaxação e registra o caso em `modelo-portas.csv`.
3. Calcula exatamente a distribuição final de cada segmento isolado, iniciando os cinco qubits em zero. O reset é ideal no modelo.
4. Aplica a matriz de atribuição de leitura de cada um dos dois qubits medidos, usando separadamente as probabilidades de ler 0 após preparar 1 e de ler 1 após preparar 0. Não acrescenta outro canal térmico durante a leitura, pois a atribuição já reúne efeitos da medição.

A composição segue a construção documentada do [modelo de ruído de dispositivos do Qiskit Aer](https://qiskit.github.io/qiskit-aer/tutorials/2_device_noise_simulation.html). A duração única de porta de um qubit do CSV é usada para RX, SX e X; RZ é tratada como virtual. Essas são aproximações explícitas.

O modelo não inclui agendamento de esperas, erro de reset, vazamento para outros níveis, correlações de leitura, interferência entre qubits, erros coerentes, deriva temporal nem memória entre segmentos. Ele também não reconstrói a execução histórica de 6/11. Seus parâmetros não são ajustados às frequências observadas. A diferença entre previsão e observação mostra os limites desta aproximação; não identifica uma causa única do resultado físico.

`resultados-por-bloco.csv` separa a previsão com ruído de portas, a previsão com apenas atribuição de leitura e a previsão combinada. Essas probabilidades não têm intervalo de amostragem: foram calculadas por matriz densidade e transformação clássica exata. As contagens do hardware permanecem separadas.
