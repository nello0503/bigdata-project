# Note di progetto – Big Data pipeline

## Ambiente di sviluppo

Il progetto è sviluppato su Windows tramite WSL2 (Windows Subsystem for Linux) con Ubuntu, su un PC con 16 GB di RAM. WSL2 esegue un kernel Linux reale: evita i problemi di compatibilità di Spark/Hadoop su Windows nativo e riproduce l'ambiente Linux tipico dei cluster Big Data. Rispetto a una macchina virtuale tradizionale alloca la memoria in modo dinamico, lasciando più risorse a Spark e ai container.

| Componente | Versione | Ruolo |
|---|---|---|
| Ubuntu (WSL2) | 26.04 | Ambiente Linux |
| Java (OpenJDK) | 17.0.20.1 | Runtime richiesto da Spark (JVM) |
| Python | 3.14.4 | Linguaggio degli script |
| PySpark | 4.3.0 | Motore di elaborazione distribuita |
| pandas | 2.3.3 | Esplorazione dati (< 3 per compatibilità con PySpark) |
| pyarrow | 26.0.0 | Lettura/scrittura Parquet |
| Docker | 
'docker'
to

about

https://docs.docker.com/go/wsl2/ | Containerizzazione dei servizi |
| Docker Compose | 
The command 'docker' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.

For details about using Docker Desktop with WSL 2, visit:

https://docs.docker.com/go/wsl2/ | Orchestrazione dei container |
| Git / GitHub | 2.53.0 | Versionamento del codice |

## Motivazioni delle scelte

- Docker: ogni servizio (storage, Spark, database) gira in un container con versione fissata, quindi l'intera pipeline si avvia con un solo comando su qualsiasi macchina. Risponde al requisito di riproducibilità.
- Spark: elabora i dati in memoria e in parallelo; lo stesso codice gira in locale e su un cluster, quindi la soluzione è pronta a scalare anche se il dataset attuale è contenuto.
- Ambiente virtuale Python + requirements.txt: fissa le versioni delle librerie per ottenere gli stessi risultati in esecuzioni diverse.
- pandas < 3: PySpark non supporta ancora pienamente pandas 3, versione bloccata per evitare incompatibilità.
- Dati esclusi dal repository: i dataset non sono versionati per le dimensioni; vengono riscaricati dallo script di ingestion dalla fonte originale, citata nel report.

## Struttura del repository

~~~
bigdata-project/
├── data/raw/          dati scaricati, mai modificati (zona raw del data lake)
├── data/processed/    dati elaborati in formato Parquet
├── src/               script di ingestion, processing e query
├── notebooks/         esplorazione e prove
├── docs/              report e schemi architetturali
├── note.md            appunti su scelte e motivazioni
└── requirements.txt   dipendenze Python con versioni fissate
~~~

## Verifica dell'ambiente

Test eseguito con src/test_spark.py: creazione di un DataFrame Spark e scrittura in Parquet completate correttamente. I warning su loopback address e native-hadoop library sono attesi in ambiente WSL locale e non influiscono sul funzionamento.

## Dataset
(da completare)

## Domande di analisi
(da completare)
