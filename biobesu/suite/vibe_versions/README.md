# vibe_versions
## General
The `benchmark_data.tsv` input file is expected to have the following format:
```
id  gene_id    hpo_ids
01  1    HP:0001234,HP:0004321
02  29974    HP:0000888
```

IMPORTANT: The `id` field must be unique!

## VIBE v5.0

1. Download/unpack VIBE + resources:
    - [vibe-with-dependencies-5.0.3.jar](https://github.com/molgenis/vibe/releases/download/vibe-5.0.3/vibe-with-dependencies-5.0.3.jar)
    - [vibe-5.0.0-hdt.tar.gz](https://downloads.molgeniscloud.org/downloads/vibe/vibe-5.0.0-hdt.tar.gz)
    - [hp.owl](http://purl.obolibrary.org/obo/hp/releases/2018-03-08/hp.owl)

2. Run VIBE:
   ```bash
   biobesu vibe_versions 5.0 --jar vibe-with-dependencies-5.0.3.jar --hdt vibe-5.0.0-hdt/vibe-5.0.0.hdt --hpo hp.owl \
   --input benchmark_data.tsv --output vibe_5_0_output_dir
   ```

## VIBE v5.1

1. Download/unpack VIBE + resources:
    - [vibe-with-dependencies-5.1.0.jar](https://github.com/molgenis/vibe/releases/download/vibe-5.1.0/vibe-with-dependencies-5.1.0.jar)
    - [vibe-5.1.0-hdt.tar.gz](https://downloads.molgeniscloud.org/downloads/vibe/vibe-5.1.0-hdt.tar.gz)
    - [hp.owl](http://purl.obolibrary.org/obo/hp/releases/2018-03-08/hp.owl) (same as VIBE v5.0 benchmark)

2. Run VIBE:
   ```bash
   biobesu vibe_versions 5.1 --jar vibe-with-dependencies-5.1.0.jar --hdt vibe-5.1.0-hdt/vibe-5.1.0.hdt --hpo hp.owl \
   --input benchmark_data.tsv --output vibe_5_1_output_dir
   ```