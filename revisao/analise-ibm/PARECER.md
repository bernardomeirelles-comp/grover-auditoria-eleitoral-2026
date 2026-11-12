# Parecer técnico das três execuções IBM

Os três blocos previstos foram recebidos e analisados. A validação passou para os 36 segmentos físicos, para as três sequências completas com resets e para a comparação com a tabela da interface: terceiro trabalho, registrador r00, contagens 411/27/44/30. O programa não enviou novos trabalhos.

Cada combinação de implementação e alvo reúne 1.536 medições (3 × 512). A tabela abaixo mantém os quatro alvos separados; os intervalos são marginais de Wilson de 95%.

| Implementação | Alvo | Acertos / 1.536 | Acerto | IC 95% | Modelo aproximado |
|---|---|---:|---:|---:|---:|
| Original | 00 | 577 | 37,57% | 35,18–40,02% | 59,53% |
| Original | 01 | 696 | 45,31% | 42,84–47,81% | 66,01% |
| Original | 10 | 595 | 38,74% | 36,33–41,20% | 63,83% |
| Original | 11 | 609 | 39,65% | 37,23–42,12% | 61,30% |
| Gray + cancelamento | 00 | 1089 | 70,90% | 68,58–73,12% | 85,51% |
| Gray + cancelamento | 01 | 1064 | 69,27% | 66,92–71,53% | 88,77% |
| Gray + cancelamento | 10 | 1077 | 70,12% | 67,78–72,35% | 87,64% |
| Gray + cancelamento | 11 | 1049 | 68,29% | 65,92–70,57% | 85,29% |
| Controle | 00 | 1431 | 93,16% | 91,79–94,32% | 99,32% |
| Controle | 01 | 1395 | 90,82% | 89,27–92,16% | 95,47% |
| Controle | 10 | 1430 | 93,10% | 91,72–94,26% | 97,03% |
| Controle | 11 | 1396 | 90,89% | 89,34–92,22% | 96,26% |

Gray + cancelamento apresentou maior frequência de acerto que a implementação original em todos os 12 pares alvo/bloco. O menor acerto agregado foi 68,29%, abaixo do equilíbrio de 88,89%. Pela convenção de reiniciar e verificar usada no estudo, 2/p corresponde a aproximadamente 2,929 consultas abstratas, contra 2,25 na referência clássica com promessa de um único alvo. Isso não é uma medida de tempo de execução.

Os circuitos originais usaram 108–180 portas CZ e profundidade 242–374; Gray + cancelamento usou 31–46 CZ e profundidade 74–106. Essas profundidades incluem reset e medida. A redução de recursos acompanha a melhora observada, mas esta comparação não isola uma causa física única.

Houve variação entre blocos. O conjunto físico foi [20,21,22,23,36] nos blocos 1 e 3 e [12,13,14,15,19] no bloco 2. Compilação, qubits, ordem dos segmentos e momento da execução participam dessa variação. Os controles agregados ficaram entre 90,82% e 93,16%; eles reúnem preparação, reset e leitura, sem medir apenas a leitura.

A aproximação com a calibração prevê 59,53–66,01% para original, 85,29–88,77% para Gray + cancelamento e 95,47–99,32% para os controles. Ela superestima os acertos agregados observados. O modelo usa relaxação e despolarização residual ajustadas à infidelidade publicada, além da atribuição de leitura. Não representa esperas agendadas, resets imperfeitos, memória entre segmentos, erros coerentes, vazamento, interferência entre qubits ou deriva. Portanto, não serve como diagnóstico causal nem reconstrução da execução antiga.

A interface informou 2 s de uso de QPU por trabalho, somando 6 s nos três trabalhos. São os valores exibidos pela plataforma; não representam o tempo total de preparação, fila, submissão, exportação e análise.

A figura `figuras/ibm-repeticoes.pdf` foi examinada em PNG a 96 dpi e em dimensões integrais. É vetorial, incorpora Times New Roman, não contém imagens rasterizadas nem grade de fundo. Usar largura total de texto (176,5 mm); altura 83,8 mm. Legendas ficam fora dos dados. Marcadores preenchidos mostram o agregado, vazios mostram os três blocos e barras indicam Wilson marginal. O gráfico histórico fica no suplemento.

O script `analisar-repeticoes.py`, os CSVs, os QASM extraídos e os JSONs de validação permitem reproduzir estes resultados sem acesso à IBM. Os limites completos estão em `LEIA-ME.md`. Nenhum arquivo LaTeX ou bibliográfico foi alterado nesta tarefa.
