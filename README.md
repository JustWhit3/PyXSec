# PyXSec
Python framework to measure cross-sections of particle physics processes using different unfolding techniques (RooUnfold, QUnfold, etc...)

Work in progress...

Reimplementation of [`TTbarUnfold`](https://gitlab.cern.ch/ttbarDiffXs13TeV/ttbarunfold).

```shell
conda create --name pyxsec-dev python==3.8
conda activate pyxsec-dev
pip install -r requirements.txt
pip cache purge && pip check
```