# Bioinformatics Benchmark Suite

A suite for testing bioinformatics tools. Be sure to check a suite's individual README for any additional requirements. Their README's are stored in their individual folders located [here](./biobesu/suite).

## Requirements

- python 3.8 or higher
- pip

Furthermore, ensure that the python `/bin` folder is added to `$PATH` in `.bash_profile` so that the tool will be executable from the command line.

## How-to

### Install
```bash
git clone git@github.com:molgenis/biobesu.git
cd biobesu
pip install .
```

### Use

```bash
# General format
biobesu <suite> <runner> --<runner_argument> [--<runner_optional_argument>]

# Get available suites
biobesu

# Get runners for selected suite
biobesu <suite>
```

There are several scripts which can be executed directly. Do note that some of these require `entry_points` from the `setup.py` to function correctly, so installing BioBeSu with pip is still required.

**Example:**
```bash
# Prepare lirical.
java -jar LIRICAL.jar download

# Run lirical with benchmark data.
biobesu hpo_generank lirical --jar /path/to/lirical-1.3.0/LIRICAL.jar \
--hpo /path/to/hp.obo --input /path/to/benchmark_data.tsv \
--output /path/to/dir/output --lirical_data /path/to/dir/lirical/data \
--runner_data /path/to/tmp/dir/
```

## Developers (work-in-progress)
### Installation
#### Command line
```bash
git clone git@github.com:molgenis/biobesu.git
cd biobesu
python3 -m venv venv
source venv/bin/activate
pip install --editable '.[test]'
pytest test/
```

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

When updating the `setup.py` with a new suite, be sure to use the naming convention: `biobesu_<dirname_suite>`.
You can deviate within a suite in regards to the entrypoint names, though it is suggested to keep them identical (or at least similar).

**setup.py example**
```
'biobesu_suites': [
    'suit_name = biobesu.suite.suit_name.cli:main',
],
'biobesu_suit_name': [
    'runner_name = biobesu.suite.suit_name.runner.runner_name:main',
    'another = biobesu.suite.suit_name.runner.another_runner:main'
],
```

For test python scripts, please prepend `<suit_name>-` before the name if it's a suite-specific test file.
This so that no overlapping test script filenames can occur.
