# PyXSec

## Table of contents

- [Introduction](#introduction)
- [Developer environment](#developer-environment)
- [How to use](#how-to-use)
- [Credits](#credits)
  - [Main developers](#main-developers)
  - [Other contributors](#other-contributors)
- [Stargazers over time](#stargazers-over-time)

## Introduction

`PyXSec` is a Python framework used to measure the differential cross-sections of particle physics processes using the unfolding technique. The peculiarity of this software is that you can perform this measurements using classical- and quantum-computing based techniques.

This software is currently based [`ROOT`](https://root.cern/), but plans are work in progress to substitute it with [`NumPy`](https://numpy.org/) and [`uproot`](https://uproot.readthedocs.io/en/latest/basic.html).

For the moment the cross-sections can be measured using the following unfolding modules:

- [`RooUnfold`](https://gitlab.cern.ch/RooUnfold): for classical unfolding backend
- [`QUnfold`](https://github.com/JustWhit3/QUnfold): for quantum-computing based backend

The idea at the base of this framework was inspired by the [`TTbarUnfold`](https://gitlab.cern.ch/ttbarDiffXs13TeV/ttbarunfold) framework, developed by [Marino Romano](https://gitlab.cern.ch/mromano), which is widely used in particle physics analyses to measure cross-sections using classical unfolding techniques.

:warning: The project is currently work-in-progress and it is still not ready for production. See the [contribution](https://github.com/JustWhit3/PyXSec/blob/main/CONTRIBUTING.md) file if interested.

:warning: This project is not currently available on [PyPI](https://pypi.org/), but it will be very soon. Our idea is to let it be easily installable in order to keep analyses as clean as possible and doesn't require to clone the entire repository everytime for a new study.

## Developer environment

To setup the environment for `PyXSec` development you need two dependencies:

- [`tox`](https://tox.wiki/en/latest/): at least v4
- [`conda`](https://docs.conda.io/en/latest/)

To setup the `conda` conda environment to work with the repository (only the first time):

```shell
conda create --name pyxsec-dev python==3.10
conda activate pyxsec-dev
pip install -r requirements.txt
pip cache purge && pip check
```

and every time you open a new shell:

```shell
conda activate pyxsec-dev
```

## How to use

The usage is very simple. You need an input XML configuration file with all the paths and the files needed for the measurement. An example is the following:

```XML
<configuration>
    <data       file="PWGH7.AFII.root"	hpath="reco/2j2b_emu/DR_b1b2" />                      <!-- Data -->
    <sig        file="AFII.root"	    hpath="reco/2j2b_emu/DR_b1b2" />                      <!-- Signal -->
    <bkg        file=""                 hpath="" />                                           <!-- Background -->
    <res	    file="AFII.root"        hpath="reco/2j2b_emu/particle_DR_b1b2_vs_DR_b1b2" />  <!-- Response matrix -->
    <gen        file="AFII.root"        hpath="particle/2j2b_emu/particle_DR_b1b2" />         <!-- Theory distributions -->
    <lumi       value="138965.16" />                                                          <!-- Luminosity -->
    <br         value="1"/>                                                                   <!-- Branching ratio -->
    <do_total   value="0" />                                                                  <!-- Do total xsec -->
    <unfolding  method="SimNeal"        regularization="0" statErr="toys:Gauss" ntoys="0" />  <!-- Unfolding settings -->
    <spectrum   particle="2j2b_emu"     variable="DR_b1b2" />                                 <!-- Particle-level info -->
</configuration>
```

each `ROOT` file must have `reco` and `particle`/`parton` level tress well separated. Each tree must contain branches for each interested selection and each branch must contain variables distributions to be unfolded and response matrices.

A quick example about how to use the framework:

```shell
python PyXSec.py --config="config.xml" --output="output.root"
```

:warning: This usage is still not supported, but this should be the final form of the framework signature.

## Credits

### Main developers

<table>
  <tr>
    <td align="center"><a href="https://justwhit3.github.io/"><img src="https://avatars.githubusercontent.com/u/48323961?v=4" width="100px;" alt=""/><br /><sub><b>Gianluca Bianco</b></sub></a></td>
    <td align="center"><a href="https://github.com/SimoneGasperini"><img src="https://avatars2.githubusercontent.com/u/71086758?s=400&v=4" width="100px;" alt=""/><br /><sub><b>Simone Gasperini</b></sub></a></td>
  </tr>
</table>

### Other contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DrWatt"><img src="https://avatars.githubusercontent.com/u/33673848?v=4" width="100px;" alt=""/><br /><sub><b>DrWatt</b></sub></a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Stargazers over time

[![Stargazers over time](https://starchart.cc/JustWhit3/PyXSec.svg)](https://starchart.cc/JustWhit3/PyXSec)