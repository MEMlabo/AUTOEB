# AUTOEB <!-- omit in toc -->
**AU** **t**est **o**n **e**ach **b**ipartition

Technical documents are [here](docs/Index.md).

## Index <!-- omit in toc -->

- [Citation](#citation)
- [Dependencies](#dependencies)
- [Installation](#installation)
  - [By Singularity](#by-singularity)
  - [Without Singularity](#without-singularity)
    - [Linux](#linux)
    - [Windows](#windows)
- [Usage](#usage)
  - [By Singularity](#by-singularity-1)
  - [Without Singularity](#without-singularity-1)
    - [Linux](#linux-1)
    - [Windows](#windows-1)
  - [Options](#options)
    - [General options](#general-options)
    - [IQ-TREE options](#iq-tree-options)
    - [CONSEL options](#consel-options)
    - [Output options](#output-options)
  - [Examples of usage](#examples-of-usage)
- [Output](#output)

## Citation

Under preparation

## Dependencies

- Python
  - version: 3.11
  - web site: https://www.python.org/
- IQ-TREE
  - version: 2.2.0
  - web site: http://www.iqtree.org/
  - GitHub: https://github.com/iqtree/iqtree2
  - citation: B.Q. Minh, H.A. Schmidt, O. Chernomor, D. Schrempf, M.D. Woodhams, A. von Haeseler, R. Lanfear (2020) IQ-TREE 2: New models and efficient methods for phylogenetic inference in the genomic era. *Mol. Biol. Evol*., 37:1530-1534. doi: 10.1093/molbev/msaa015
- CONSEL
  - version: commit at `1a532a4fe9e7d4e9101f2bbe64613f3b0cfc6274`
  - web site: http://stat.sys.i.kyoto-u.ac.jp/prog/consel/
  - GitHub: https://github.com/shimo-lab/consel
  - citation: Shimodaira H., Hasegawa M. (2001). CONSEL: for assessing the confidence of phylogenetic tree selection. *Bioinformatics*. Dec;17(12):1246-7. doi: 10.1093/bioinformatics/17.12.1246.

## Installation

Whichever installation type you select, you have to clone this repository in advance.
**DO NOT** use the `main` branch for installation.
You should checkout the tag associated with target version of this software (In `git clone` command, `-b TAG` option is usable).

```bash
git clone git@github.com:MEMlabo/AUTOEB.git -b v1.1.1
```

### By Singularity

To build singularity container, execute `scripts/build-singularity.sh`.
When the build successes, the container file `autoeb.sif` is created at `package/`.

```sh
chmod +x ./scripts/build-singularity.sh
bash ./scripts/build-singularity.sh
```

### Without Singularity

#### Linux

At first, execute `scripts/init.sh` to initialize the project.

```sh
chmod +x ./scripts/init.sh
bash ./scripts/init.sh
```

Next, add package path of `autoeb` to `.bashrc` by using the environment variant `PYTHONPATH`.

**Example of .bashrc**
```
export PYTHONPATH=$PYTHONPATH:<repo dir>/src/
```

Lastly, set the command to execute IQ-TREE and path of CONSEL by modifying `src/autoeb/config.json`.

**Example of config.json**
```json
{
    "iqtree_command": "iqtree2.2.0",
    "consel_dir": "/usr/local/bin/"
}
```

#### Windows

At first, execute `scripts/init.ps1` to initialize the project.

```ps
.\scripts\init.ps1
```

Next, add package path of `autoeb`  by using the variant `PYTHONPATH` (Using control panel is easy way).

Lastly, set the command to execute IQ-TREE and path of CONSEL by modifying `src/autoeb/config.json`.


**Example of config.json**
```json
{
    "iqtree_command": "iqtree2.exe",
    "consel_dir": "$PATH"
}
```

## Usage

### By Singularity

Use `singularity run` command to execute.

```
singularity run ./package/autoeb.sif <parameters>
```

### Without Singularity

#### Linux

Execute `scripts/exec_autoeb.sh`.

```
bash ./scripts/exec_autoeb.sh <parameters>
```

#### Windows

Execute `scripts/exec_autoeb.ps1`.

```
.\scripts\exec_autoeb.ps1 <parameters>
```

### Options

#### General options

| Name |   Full Name   |          Type / Default          | Required | Description                                                                                                                                                |
| ---: | :-----------: | :------------------------------: | :------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-h` |   `--help`    |               flag               |    -     | Show the help of this application                                                                                                                          |
| `-v` |  `--version`  |               flag               |    -     | Show the version of this application                                                                                                                       |
| `-s` |    `--seq`    |               file               |    +     | Path of sequences (file format should be applicable for IQ-TREE)                                                                                           |
| `-t` |   `--tree`    |               file               |    +     | Path of ML-tree file                                                                                                                                       |
|      |   `--range`   |          string / `ALL`          |    -     | Specifies which bipartition to analyze e.g.) `ALL` (all bipartitions), `-5` (0th to 5th) ,`3-11` (3rd to 11th), `4,13-` (4th and 13th to last bipartition) |
|      | `--sig-level` | float (0 \< value \< 1) / `0.05` |    -     | Significance level of rejecting NNI-tree                                                                                                                   |
| `-T` |  `--thread`   |         int (\>=1) / `1`         |    -     | Specifies the number of threads used in IQ-TREE and parallel execution of CONSEL                                                                           |
|      |   `--redo`    |               flag               |    -     | Ignore checkpoints and force to execute all operation                                                                                                      |

#### IQ-TREE options

| Name |     Full Name      |      Type / Default       | Required | Description                                                                         |
| ---: | :----------------: | :-----------------------: | :------: | :---------------------------------------------------------------------------------- |
| `-m` |     `--model`      |          string           |    +     | Substitution model supported by IQ-TREE e.g.) `LG+I+G`, `WAG+C20+F+R10`             |
|      |  `--iqtree-param`  |        file / null        |    -     | The text file with optional parameters used in executing IQ-TREE                    |
| `-b` |   `--bootstrap`    | int (\>= 1000) /`100,000` |    -     | Specifies the number of replicates by RELL-bootstrap in makermt (in CONSEL package) |
|      | `--iqtree-verbose` |           flag            |    -     | IQ-TREE log become redirected to stdout.                                            |

When specify `--iqtree-param` option, specify a text file which represents parameters to give in running IQ-TREE.
In loading the text file, new line (`\n`) is replaced by white space.

<details>
<summary>Example</summary>

AUTOEB Command:
```bash
autoeb -s seq.fasta -t ml.tree -m LG+F+G -o autoeb --iqtree-param iqtree-parameters.txt
```

`iqtree-parameters.txt`:
```text
--mem 100G
--safe
```

</details>

#### CONSEL options

| Name | Full Name |   Type / Default   | Required | Description                                                                                                                                                                                                      |
| ---: | :-------: | :----------------: | :------: | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|      | `--seed`  | int (\>= 0) / `-1` |    -     | Specifies the seed of RELL-bootstrap by the makermt. If `0`, system time is used for seed (each bipartition has different values). If `-1` (default), random value is used (each bipartition has the same value) |


#### Output options

| Name |      Full Name       |     Type / Default     | Required | Description                                                                                |
| ---: | :------------------: | :--------------------: | :------: | :----------------------------------------------------------------------------------------- |
| `-o` |       `--out`        |       directory        |    +     | Directory to output files. If specified directory doesn't exist, created automatically     |
| `-f` |    `--out-format`    | string / `{src}/{bin}` |    -     | Specifies the format of bipartitions. See also [here](./docs/output.md#bipartition-format) |
|      | `--output-tmp-files` |          flag          |    -     | All temporary files are retained and compressed into `tmp-output.tar.gz`.                  |

### Examples of usage

In the most common use case of AUTOEB, sequence file `seq.fasta` and tree file `ml.treefile` are specified files.
`LG+C60+F+G` is specified as substitution model.
Output files are contained at `output_autoeb` directory.
```bash
singularity run autoeb.sif -s seq.fasta -t ml.treefile -m LG+C60+F+G -o output_autoeb
```

`-T` option specifies the number of threads used.
See also [here](./docs/op_flow.md#multi-threading).
```bash
singularity run autoeb.sif -s seq.fasta -t ml.treefile -m LG+C60+F+G -T 16 -o output_autoeb
```

## Output

See [here](./docs/output.md).
