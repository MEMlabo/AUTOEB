# For Developers

## Environment

- Text Editor: Visual Studio Code
- Python version: 3.11

## Initialize

Execute `srcipts/init.sh` or `scripts/init.ps1`.

## Test

Enter venv and type: 

```sh
python3 -m test
```

If no `AssertionError` are raised, the test is successful.

## Type Check

Before commit, do type check: 

```sh
mypy -p autoeb -p test
```
