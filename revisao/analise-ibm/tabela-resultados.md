# Resultados IBM por caso

Três blocos de 512 repetições por caso; 1.536 observações agregadas. As frequências abaixo são provenientes de `resultados-agregados.csv`. Cada bloco contém os 12 segmentos em uma sequência com reinicializações, não 12 trabalhos independentes.

| Implementação | Alvo | Acertos / 1.536 | Acerto (%) | Wilson marginal 95% (%) | Faixa entre blocos (%) | Previsão do modelo (%) |
|---|---|---:|---:|---:|---:|---:|
| Original | 00 | 577 | 37,57 | 35,18–40,02 | 36,52–38,28 | 59,53 |
| Original | 01 | 696 | 45,31 | 42,84–47,81 | 41,99–49,41 | 66,01 |
| Original | 10 | 595 | 38,74 | 36,33–41,20 | 37,89–40,43 | 63,83 |
| Original | 11 | 609 | 39,65 | 37,23–42,12 | 31,64–45,70 | 61,30 |
| Simplificada | 00 | 1089 | 70,90 | 68,58–73,12 | 63,67–80,27 | 85,51 |
| Simplificada | 01 | 1064 | 69,27 | 66,92–71,53 | 65,23–72,66 | 88,77 |
| Simplificada | 10 | 1077 | 70,12 | 67,78–72,35 | 63,28–77,34 | 87,64 |
| Simplificada | 11 | 1049 | 68,29 | 65,92–70,57 | 58,01–78,52 | 85,29 |
| Controle | 00 | 1431 | 93,16 | 91,79–94,32 | 89,84–96,88 | 99,32 |
| Controle | 01 | 1395 | 90,82 | 89,27–92,16 | 89,65–92,77 | 95,47 |
| Controle | 10 | 1430 | 93,10 | 91,72–94,26 | 90,43–96,88 | 97,03 |
| Controle | 11 | 1396 | 90,89 | 89,34–92,22 | 88,09–92,77 | 96,26 |

Os intervalos são marginais e descritivos sob aproximação binomial. Não representam toda a variação entre blocos nem intervalos simultâneos para os 12 casos. O modelo calcula probabilidades sem amostragem e não recebe intervalo binomial. Os controles incluem preparação, reinicialização e leitura. O limite de 88,89% aplica-se à convenção de custo das buscas, não à avaliação dos controles.

As contagens de cada bloco e a comparação pareada permanecem nos CSVs desta pasta. A interface exibiu seis segundos de QPU no total; a evidência está em `../composer/consumo-interface.json`.
