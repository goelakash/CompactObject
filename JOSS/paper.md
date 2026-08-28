---
title: 'CompactObject: An open-source Python package for full-scope neutron star equation of state inference'
tags:
  - Python
  - astrostatistics
  - neutron stars
authors:
  - name: Chun Huang
    orcid: 0000-0001-6406-1003
    affiliation: 1
  - name: Tuhin Malik
    orcid: 0000-0003-2633-5821
    affiliation: 2
  - name: João Cartaxo
    orcid: 0009-0001-7105-8272
    affiliation: 2
  - name: Shashwat Sourav
    orcid: 0000-0002-0169-4003
    affiliation: 1
  - name: Wenli Yuan
    orcid: 0000-0003-2771-759X
    affiliation: 3
  - name: Tianzhe Zhou
    orcid: 0009-0000-8504-9134
    affiliation: 4
  - name: Xuezhi Liu
    orcid: 0009-0008-3286-7254
    affiliation: 5
  - name: John Groger
    orcid: 0000-0002-7054-9053
    affiliation: 1
  - name: Nicole Osborn
    orcid: 
    affiliation: 1
  - name: Nathan Whitsett
    orcid: 
    affiliation: 1
  - name: Xieyuan Dong
    orcid: 
    affiliation: 6
  - name: Zhiheng Wang
    orcid: 0009-0000-5088-6207
    affiliation: 1
  - name: Constança Providência
    orcid: 0000-0001-6464-8023
    affiliation: 2
  - name: Micaela Oertel
    orcid: 0000-0002-1884-8654
    affiliation: 7
  - name: Alexander Y. Chen
    orcid: 0000-0002-4738-1168
    affiliation: 1
  - name: Laura Tolos
    orcid: 0000-0002-6449-106X
    affiliation: "8, 9, 10"
  - name: Anna Watts
    orcid: 0000-0002-1009-2354
    affiliation: 11

affiliations:
  - name: Physics Department and McDonnell Center for the Space Sciences, Washington University in St. Louis, MO 63130, USA
    index: 1
  - name: CFisUC, Department of Physics, University of Coimbra, 3004-516 Coimbra, Portugal
    index: 2
  - name: School of Physics and State Key Laboratory of Nuclear Physics and Technology, Peking University, Beijing 100871, China
    index: 3
  - name: Department of Physics, Tsinghua University, Beijing 100084, China
    index: 4
  - name: Physics Department, Central China Normal University, Luoyu Road, 430030, Wuhan, China
    index: 5
  - name: School of Physics, Nankai University, Tianjin 300071, China
    index: 6
  - name: Laboratoire Univers et Théories, CNRS, Observatoire de Paris, Université PSL, Université Paris Cité, 5 place Jules Janssen, 92195 Meudon, France
    index: 7
  - name: Institute of Space Sciences (ICE, CSIC), Campus UAB, Carrer de Can Magrans, 08193, Barcelona, Spain
    index: 8
  - name: Institut d'Estudis Espacials de Catalunya (IEEC), 08860 Castelldefels (Barcelona), Spain
    index: 9
  - name: Frankfurt Institute for Advanced Studies, Ruth-Moufang-Str. 1, 60438 Frankfurt am Main, Germany
    index: 10
  - name: Anton Pannekoek Institute for Astronomy, University of Amsterdam, Science Park 904, 1090 GE Amsterdam, the Netherlands
    index: 11

date: 28 August 2026
bibliography: cojoss.bib
---


# Summary

The equation of state (EOS) relates pressure, density, and composition in the
interiors of neutron stars and determines observable quantities such as their
masses, radii, and tidal deformabilities. **CompactObject** is an open-source
Python framework for constructing or importing EOSs, calculating neutron-star
structure, and constraining EOS parameters with Bayesian inference. Its modular
design separates EOS generation, Tolman--Oppenheimer--Volkoff (TOV) integration,
likelihood construction, sampling, and posterior visualization, so each layer can
also be used independently. The package connects astrophysical measurements from
radio timing, X-ray pulse-profile modelling, and gravitational waves with nuclear
physics information from saturation properties, chiral effective field theory
($\chi$EFT), and perturbative quantum chromodynamics (pQCD). It also reads cold
EOS tables from CompOSE [@CompOSE2022], allowing tabulated models to be analysed
through the same interfaces as built-in models.

# Statement of need

Inferring an EOS requires repeatedly translating model parameters into a
thermodynamically consistent EOS, solving the stellar-structure equations, and
evaluating heterogeneous observational and theoretical constraints. Comparing
model families is particularly difficult if each is implemented with different
unit conventions, crust matching, likelihoods, or sampling choices.

CompactObject supplies these operations in one reusable workflow. Its purpose is
not to privilege one description of dense matter, but to make controlled
comparisons between flexible parameterizations, nuclear empirical-parameter
expansions, phenomenological field theories, and exotic compact-star models. The
same likelihood and TOV machinery can therefore be applied across model classes,
while model-specific outputs such as particle fractions and nuclear saturation
properties remain accessible.

# State of the field

Flexible piecewise-polytropic and speed-of-sound parameterizations are widely
used to explore broad EOS spaces. We refer to these as *parameterized EOS
descriptions*, not metamodels. Here, *nuclear metamodel* is reserved for an
expansion of the energy per particle around nuclear saturation density in terms
of empirical isoscalar and isovector parameters [@Margueron2018], which is also
implemented in CompactObject.

NEoST provides an open-source nested-sampling framework with flexible core
parameterizations and low-density models informed by ab initio $\chi$EFT
calculations [@Raaijmakers2025]. CompactObject is complementary: its particular
emphasis is the use of a common inference interface for those flexible
descriptions alongside physics-motivated models whose couplings, composition,
and saturation properties can be inferred directly. This includes nonlinear and
density-dependent relativistic mean-field (RMF) models, strangeon matter, and
quark matter. Both approaches connect microscopic nuclear information and
multimessenger data; they differ mainly in the model libraries and interfaces
they expose.

# Software design and functionality

The `EOSgenerators` module implements piecewise-polytropic and speed-of-sound
parameterizations, a nuclear empirical-parameter expansion, nonlinear and
density-dependent RMF models [@Tolos2017; @Malik2022], a user-defined
density-dependent coupling interface, a strangeon EOS [@Xu2003], and the MIT bag
model [@Chodos1974]. It also imports CompOSE and LAL-format tables. The
`TOVsolver` module maps an EOS to mass--radius and mass--radius--tidal-
deformability sequences and provides sound-speed and maximum-central-density
diagnostics.

`InferenceWorkflow` provides priors and likelihoods for mass, mass--radius, and
tidal-deformability measurements; nuclear saturation properties; pure-neutron-
matter constraints from $\chi$EFT [@Hebeler2013; @Huth2022]; and high-density
pQCD consistency [@Gorda2023]. Its nested-sampling workflow uses UltraNest
[@Buchner2021], while documented notebooks show complete inference pipelines.
Posterior comparison plots are supplied by `postprocessing`. NumPy, SciPy,
Numba, Jupyter, and corner.py provide the principal numerical and interactive
infrastructure [@NumPy2011; @SciPy2020; @Numba2015; @Jupyter2016;
@Corner2016]. Installation and notebook smoke tests run in continuous
integration for both pip and Conda environments.

# Research impact

CompactObject has supported published Bayesian studies of nucleonic RMF models
[@Huang2024], hyperonic RMF models [@Huang2025], strangeon matter
[@Yuan2025], and first-order phase transitions [@HuangSourav2025]. A systematic
cross-comparison of covariant energy-density functionals has subsequently used
the package to apply identical astrophysical, $\chi$EFT, and pQCD constraints
across multiple model families [@Cartaxo2026]. These applications demonstrate
the intended use of the software for reproducible inference and model comparison
rather than only prospective functionality.

The source, examples, tests, and documentation are available from the project
repository [@CompactObjectRepo], and versioned releases are archived on Zenodo
[@COZenodo]. CompactObject is distributed under the GNU General Public License,
version 3 or later (GPL-3.0-or-later), consistently with the repository's
`LICENSE` file.

# AI usage disclosure

OpenAI Codex was used during the review revision to assist with language editing
and bibliography auditing. The authors checked the resulting text against the
source code and primary literature and take responsibility for the manuscript's
content.

## Acknowledgements

C.H., S.S., N.O., N.W., and J.G. acknowledge support from the Arts & Sciences
Fellowship of Washington University in St. Louis. C.H. also acknowledges support
from NASA grant 80NSSC24K1095. C.P. received support from Fundação para a
Ciência e a Tecnologia (FCT), I.P., Portugal, under projects UIDB/04564/2020
(doi:10.54499/UIDB/04564/2020), UIDP/04564/2020
(doi:10.54499/UIDP/04564/2020), and 2022.06460.PTDC
(doi:10.54499/2022.06460.PTDC). L.T. acknowledges support from
CEX2020-001058-M (Unidad de Excelencia "María de Maeztu") and
PID2022-139427NB-I00 financed by the Spanish
MCIN/AEI/10.13039/501100011033/FEDER, EU; Generalitat de Catalunya contract
2021 SGR 171; Generalitat Valenciana contract CIPROM/2023/59; and CRC-TR 211,
project 315477589 ("Strong-interaction matter under extreme conditions").
A.L.W. acknowledges support from ERC Consolidator Grant 865768 AEONS. A.C.
acknowledges support from NSF grants DMS-2235457 and AST-2308111.

# References
