# Optimal Policy Selection Under Bilateral Preferences

> **Project Type** This is an independent "passion" project. The repository is not a polished Python package. It contains exploratory ideas, many of which are rough or unfinished. The code reflects the development process and is not intended for reuse.

> **AI Statement:** I originally started this project in 2025, in 2026 I came back and used an AI coding assistent to clean up the code. This made the work feel like it wasn't mine anymore, so I reverted to a "pre AI" version, and did some clean up "by hand". If you want to see the AI edited version, it is tagged on GitHub. That being said, "chat" style AI was used as a sounding board etc.

## Project Overview
Many situations involve a selection of policies that affect two subgroups or agents differently. Examples range from economic policies impacting different parties to household decisions affecting members of a couple or roommates. These decisions are typically binary, for instance, an economic policy may be passed or rejected, or a household decision may favor one member’s preference over another’s. This problem (in the roommate instance) was the insperation for this project. Writing this a year after I started this project, I'm not entierly sure what my goal was. But there is working code that searches for the optimal solution under different welfare functions, and different optimisation strategies. Performance differes between them, but it appears that for most practical purposes, greedy search under nash welfare seems to be a good solution.

---

## Background and Motivation
The initial inspiration for this project came from the common experience of moving in with someone. In such a scenario, numerous minor preferences and issues often differ between individuals, for example, the placement of pots and pans, the bed, or the couch. Frequently, one person may hold stronger opinions on these matters, leading them to make most of the decisions. However, this can make the other person feel less at home, simply because they have less intense preferences. This project looks to solve it by optimising some more "fair" welfare.

As I setup the problem, it became clear that this scenario is analogous to many other two-party systems. In these systems, a "naive optimal solution", simply choosing the option that is most significantly preferred, can lead to all decisions consistently favoring the one "larger" side. For instance, in politics, bills are passed based on a majority vote. While this ensures that the passed bills benefit the majority, it can neglect the interests of smaller groups.

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
├── src/
│   └── optimal_bilateral_preferences/
│       ├── __init__.py
│       └── ...
│
├── pyproject.toml
└── README.md
```

---

## License

MIT License. See `LICENSE` for details.
