# vibe_versions
## General
The `benchmark_data.tsv` input file is expected to have the following format:
```
id  gene_id    hpo_ids
01  1    HP:0001234,HP:0004321
02  29974    HP:0000888
```

IMPORTANT: The `id` field must be unique!

## Run benchmarks
### VIBE v5.0

1. Download/unpack VIBE + resources:
    - [vibe-with-dependencies-5.0.3.jar](https://github.com/molgenis/vibe/releases/download/vibe-5.0.3/vibe-with-dependencies-5.0.3.jar)
    - [vibe-5.0.0-hdt.tar.gz](https://downloads.molgeniscloud.org/downloads/vibe/vibe-5.0.0-hdt.tar.gz)
    - [hp.owl](http://purl.obolibrary.org/obo/hp/releases/2018-03-08/hp.owl)

2. Run VIBE:
   ```bash
   biobesu vibe_versions 5.0 --jar vibe-with-dependencies-5.0.3.jar --hdt vibe-5.0.0-hdt/vibe-5.0.0.hdt --hpo hp.owl \
   --input benchmark_data.tsv --output vibe_5_0_output_dir
   ```

### VIBE v5.1

1. Download/unpack VIBE + resources:
    - [vibe-with-dependencies-5.1.5.jar](https://github.com/molgenis/vibe/releases/download/vibe-5.1.5/vibe-with-dependencies-5.1.5.jar)
    - [vibe-5.1.0-hdt.tar.gz](https://downloads.molgeniscloud.org/downloads/vibe/vibe-5.1.0-hdt.tar.gz)
    - [hp.owl](http://purl.obolibrary.org/obo/hp/releases/2018-03-08/hp.owl) (same as VIBE v5.0 benchmark)

2. Run VIBE:
   ```bash
   biobesu vibe_versions 5.1 --jar vibe-with-dependencies-5.1.4.jar --hdt vibe-5.1.0-hdt/vibe-5.1.0.hdt --hpo hp.owl \
   --input benchmark_data.tsv --output vibe_5_1_output_dir
   ```

## Generate plots
First, additional required data needs to be downloaded to generate the plots:
- [CGD.txt](https://research.nhgri.nih.gov/CGD/download/) ([2021-06-08 release](https://downloads.molgeniscloud.org/downloads/biobesu/CGD_2021-06-08.txt))

There are several ways to generate the plots:
- Opening the R script in RStudio. 
  Requires adjusting the `default` paths found in the `Config` section or moving the data to the paths as described.  
- Running the script through the command line.  
  Requires using the command line arguments to define the paths to the data or moving the data to the paths as described.

Example flow of running this script:
1. Copy all output files of each ran benchmark to a single (new) directory.
2. Run the R script:
    ```bash
    Rscript generate_plots.R -b benchmark_data.tsv -r benchmark_results/ -c CGD_2021-06-08.txt -o ./plots/
    ```