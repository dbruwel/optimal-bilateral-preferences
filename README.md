# Optimal Policy Selection Under Bilateral Preferences
**This project is a work in progress.**

This is an independent research project, undertaken out of personal interest and curiosity. The repository is not a polished Python package, and the accompanying paper is incomplete and unreviewed. It contains exploratory ideas-many of which are rough or unfinished. The code reflects the development process and is not intended for reuse.

## Project Overview
Many situations involve a selection of policies that affect two subgroups or agents differently. Examples range from economic policies impacting different parties to household decisions affecting members of a couple or roommates. These decisions are typically binary—for instance, an economic policy may be passed or rejected, or a household decision may favor one member’s
preference over another’s. In this note, we analyze the problem of finding the optimal subset of policies to select. We propose a simple objective function and examine greedy algorithms, brute force, continuous approximations, and other methods. We show that the greedy algorithm is optimal for a broad class of problems, making brute force approaches unnecessary.

---

## Background and Motivation
The initial inspiration for this work stemmed from the common experience of couples moving in together. In such scenarios, numerous minor preferences and issues often differ between individuals — for example, the placement of pots and pans, the bed, or the couch. Frequently, one partner may hold stronger opinions on these matters, leading them to make most of the decisions. However, this can inadvertently make the other partner feel less at home, simply because they expressed less intense preferences. This project aimed to formulate a method to ensure both members of a couple feel heard and satisfied.

As the problem was formulated, it became clear that this scenario is analogous to many other two-party systems. In these systems, a "naive optimal solution" — simply choosing the option that is most significantly preferred — can lead to all decisions consistently favoring one side. For instance, in politics, bills are passed based on a majority vote. While this ensures that most passed bills benefit the majority, it can inadvertently neglect the interests of smaller groups.

---

## Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/dbruwel/optimal-bilateral-preferences.git
cd optimal-bilateral-preferences
pip install -e .
```

---

## Repository Structure

```
optimal-bilateral-preferences/
│
├── notebooks/                # Jupyter notebooks for exploration and results
│   └── *.ipynb
│
├── paper/                    # Draft paper, figures, and supplementary material
│   ├── main.pdf
│   └── ...
│
├── src/
│   └── optimal_bilateral_preferences/
│       ├── __init__.py
│       └── ...
│
├── setup.py
├── pyproject.toml
└── README.md
```

---

## Disclamer
This is research-grade code, not a production package. It was completed over a few weeks to explore a specific question of interest. The project does not aim to be novel or comprehensive and was not initially intended for public release. It uses various freely available Python packages under open licenses.

---

## License

MIT License. See `LICENSE` for details.
