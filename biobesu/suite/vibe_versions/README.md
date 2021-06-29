# vibe_versions
## General
The `benchmark_data.tsv` input file is expected to have the following format:
```
id  gene_id    hpo_ids
01  1    HP:0001234,HP:0004321
02  29974    HP:0000888
```

## VIBE v5.0

1. Run VIBE:

   ```bash
   biobesu vibe_versions 5.0 --input benchmark_data.tsv --output output_dir --data vibe_data_dir/ --download
   ```

Note: If data is already downloaded previously, you can omit `--download`.
