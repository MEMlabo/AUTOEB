# Operation Flow

- [Operation Flow](#operation-flow)
  - [Calculation of site-log likelihood (slnL) value](#calculation-of-site-log-likelihood-slnl-value)
  - [Performing AU test](#performing-au-test)
    - [Generating RELL-bootstrap replicates](#generating-rell-bootstrap-replicates)
    - [Performing AU test](#performing-au-test-1)
    - [Summarizing AU test](#summarizing-au-test)
  - [Mapping AU test result into trees](#mapping-au-test-result-into-trees)
  - [Multi-threading](#multi-threading)

There are 3 steps in operation.
1. Calculation of site likelihood value (IQ-TREE)
1. Performing AU test (CONSEL)
1. Mapping AU test result into trees

## Calculation of site-log likelihood (slnL) value

At first, NNI trees are generated.
`all.treeset` is generated in this step.
The first tree in this file is the ML tree.
The other trees in this file are NNI trees.
The NNI trees corresponding to `n`th bipartition of ML-tree are `2n + 2` and `2n + 3`th trees (`n` starts from 0).

Second, slnL values of ML-tree are calculated.
IQ-TREE is required in this step.

The command executing IQ-TREE is described below.
```bash
iqtree2 -s <sequence> -m <model> -te <ML-Tree> -z <Trees> -wsl
```

If file `trees.sitelh` exists, those steps are skipped.

## Performing AU test

This process are composed by 3 steps.

1. Generating replicates by RELL-bootstrap (makermt)
1. Performing AU test (consel)
1. Summarizing AU test (catpv)

These steps depends on the CONSEL package.

### Generating RELL-bootstrap replicates

Replicates are generated on each treeset of bipartition.
Treeset are composed by ML-tree, 1st NNI-tree and 2nd NNI-tree.
If `--seed` option is specified, the specified value is used as seed in makermt.
When seed is `0`, seed is generated from system time in makermt.
Seeds are generated on each makermt invokation.
When seed is `-1`, random value is used as seed.
Each bipartition has the same seed value in this case.
Otherwise, the specified value works as seed.
If `-b`, `--bootstrap` is specified, the number of replicates by RELL-bootstrap is changed.
The value must be larger or equal to 1,000.
100,000 (default value) is recommended for it.
"makermt" is required in this step.
The command executing makermt is described below.
```bash
makermt --puzzle X.sitelh -s <seed> -b <the number of replicates / 10000> > X-makermt.log
```
If file `X.rmt` exists, thie step of `X`th bipartition is skipped.

### Performing AU test

AU test is performed for each treeset of bipartition.
"consel" is required in this step.
The command executing consel is described below.
```bash
consel X > X-consel.log
```
If file `X.pv` exists, this step of `X`th bipartition is skipped.

### Summarizing AU test

The result of AU test is summarized for each treeset.
"catpv` is required in this step.
The command executing catpv is described below.
```bash
catpv X > X.catpv
```
If file `X.catpv` exists, this step of `X`th bipartition is skipped.

## Mapping AU test result into trees

The results of AU test are mapped in ML-tree.
`result.tree` represents the mapped file.
`X.catpv` files are used for mapping `X`th bipartition.
If **any** NNI-tree corresponding to `X`th bipartition is/are not rejected by AU test, `X`th bipartition is **not supported** by AU test.
If **all** NNI-trees corresponding to `X`th bipartition are rejected, `X`th bipartition is **supported** by AU test.

After the mapping, temporary files are deleted.
If `--output-tmp-files` option is specified, temporary files are archived at `tmp-output.tar.gz` file.

## Multi-threading

`-T`, `--thread` option is useful for multi-threading operation.

In site likelihood value calculation, the specified value is used as `-T` option of IQ-TREE.
In execution of CONSEL, CONSEL processes (makermt, consel, catpv) runs parallely (CONSEL doesn't supports multi-threading operation).
