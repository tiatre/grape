GRAPE: Graph Analysis and Phylogenetic Estimation
================================================

.. image:: grape_logo_small.png
   :alt: GRAPE Logo
   :align: center
   :width: 300px

GRAPE is a Python library for phylogenetic inference using community detection in graphs. It applies graph-based community detection algorithms to linguistic cognate data to reconstruct phylogenetic trees, offering a novel computational approach to historical linguistics.

Quick Start
-----------

.. code-block:: bash

   # Basic analysis
   python grape.py data/iecor_small.tsv --seed 42

   # With specific parameters
   python grape.py data/dravlex.tsv --graph adjusted --community louvain --strategy fixed --initial_value 0.5 --seed 42

Features
--------

* **Multiple Community Detection Algorithms**: Louvain and Greedy Modularity methods
* **Flexible Graph Construction**: Adjusted and unadjusted linguistic distance weighting  
* **Parameter Optimization**: Fixed, dynamic, and adaptive parameter search strategies
* **Comprehensive Testing**: Validated on 7 major language families with 200+ languages
* **Standard Output**: Newick format trees compatible with phylogenetic software
* **Scientific Validation**: Results align with established linguistic classifications
* **Reproducible Results**: Random seed support for consistent outputs

Documentation
=============

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   user_guide/quickstart
   user_guide/parameters

.. toctree::
   :maxdepth: 2
   :caption: Examples

   examples/dravidian_walkthrough

.. toctree::
   :maxdepth: 2
   :caption: Technical Documentation

   technical/mathematical_background
   technical/implementation

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/grape
   api/common

Supported Language Families
===========================

GRAPE has been tested and validated on:

================== ================================== =========== ===================================
Family             Dataset                            Languages   Key Groupings Validated
================== ================================== =========== ===================================
**Indo-European**  harald_ie.tsv, iecor_full.tsv     160         Germanic, Romance, Celtic, Slavic, Indo-Iranian
**Dravidian**      dravlex.tsv                        19          South, Central, North Dravidian
**Polynesian**     walworthpolynesian.tsv             30          Tongic, Nuclear Polynesian, Eastern Polynesian
**Tupian**         tuled.tsv                          30+         Guaranic group, early branching patterns
**Arawakan**       chaconarawakan.tsv                 8           Northern Arawakan geographic clustering
================== ================================== =========== ===================================

Installation
============

.. code-block:: bash

   git clone https://github.com/your-repo/grape.git
   cd grape
   pip install -r requirements.txt

Requirements
------------

* Python 3.7+
* NetworkX
* ETE3  
* NumPy
* Six (required by ETE3)

Optional Dependencies
---------------------

For distance-based phylogenetic methods:

.. code-block:: bash

   pip install biopython

Performance
===========

============== =========== ============= ==================
Dataset Size   Languages   Concepts      Typical Runtime
============== =========== ============= ==================
Small          < 20        < 200         < 5 seconds
Medium         20-50       200-500       5-30 seconds  
Large          50-200      500-1000      30-300 seconds
============== =========== ============= ==================

Memory usage scales linearly with dataset size, generally < 1GB for datasets up to 200 languages.

Citation
========

If you use GRAPE in your research, please cite:

.. code-block:: bibtex

   @software{grape2024,
     title={GRAPE: Graph Analysis and Phylogenetic Estimation},
     author={Tiago Tresoldi and Contributors},
     year={2024},
     url={https://github.com/your-repo/grape},
     note={Computational phylogenetics using community detection}
   }

License
=======

This project is licensed under the MIT License.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`