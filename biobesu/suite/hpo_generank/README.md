# hpo_generank
## General
The `benchmark_data.tsv` input file is expected to have the following format:
```
id  gene_id    hpo_ids
01  1    HP:0001234,HP:0004321
02  29974    HP:0000888
```

## Lirical

1. [Download][lirical_download] lirical (tested with v1.3.0).

2. Run `java -jar LIRICAL.jar download` (see [here][lirical_prepare] for more information).

3. Download [phenotype.hpoa][hpoa_download] and add this to the `data` folder from LIRICAL.

4. Run lirical:

   ```bash
   biobesu hpo_generank lirical --jar /path/to/lirical-1.3.0/LIRICAL.jar \
   --hpo /path/to/hp.obo --input /path/to/benchmark_data.tsv \
   --output /path/to/dir/output --lirical_data /path/to/dir/lirical/data \
   --runner_data /path/to/tmp/dir/
   ```

Note: `--runner_data` is needed for designating a location where the runner can download temporary data to. When executing the runner multiple times, using the same path skips re-downloading the same data every time.




[lirical_download]: https://github.com/TheJacksonLaboratory/LIRICAL/releases/tag/v1.3.0
[lirical_prepare]: https://lirical.readthedocs.io/en/latest/setup.html#the-download-command
[hpoa_download]: http://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa