# Bioinformatics Benchmark Suite

A suite for testing bioinformatics tools. Be sure to check a suite's individual README for any additional requirements. Their README's are stored in their individual folders located [here](./biobesu/suite)

## How-to
### Install
```bash
git clone git@github.com:molgenis/biobesu.git
cd biobesu
pip install .
```

### Use
```
# General format
biobesu <suite> <runner> --<runner_argument> [--<runner_optional_argument>]

# Get available suites
biobesu

# Get runners for selected suite
biobesu <suite>
```

Examples:
```
biobesu hpo_generank lirical --jar /path/to/LIRICAL.jar \
--hpo /path/to/hp.obo --input /path/to/benchmark_data.tsv \
--output /path/to/dir/output --lirical_data /path/to/dir/lirical/data \
--lirical_exomiser /path/to/dir/2102_hg19
```

## Developers (work-in-progress)
### Installation
#### Command line
```bash
git clone git@github.com:molgenis/biobesu.git
cd biobesu
pip install --editable .[test]
pytest test/
```

#### Intellij IDEA
1. `git clone git@github.com:molgenis/biobesu.git`
2. In Intellij IDEA, install the Python module if not yet installed (Preferences -> Plugins).
3. Open the project folder in Intellij IDEA.
4. Go to "File -> Project Structure -> SDKs" and select/create a Python virtual environment.
5. Open `setup.py` and install any missing packages.

### Structure

```
helper/ # General helper scripts
    |- <name>.py

suite/ # Benchmark suites
    |- <suitename>
        |- cli.py # Entry point for suite
        |- helper/ # Suite helper scripts
            |- <name>.py
        |- runner/ # Scripts runnable through suite entry point
            |- <name>.py
```