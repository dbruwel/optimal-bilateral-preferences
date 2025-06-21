# Optimal Policy Selection Under Bilateral Preferences
#### Abstract
Many situations involve a selection of policies that affect two subgroups or agents differently.
Examples range from economic policies impacting different parties to household decisions affect-
ing members of a couple or roommates. These decisions are typically binary—for instance, an
economic policy may be passed or rejected, or a household decision may favor one member’s
preference over another’s. In this note, we analyze the problem of finding the optimal subset of
policies to select. We propose a simple objective function and examine greedy algorithms, brute
force, continuous approximations, and other methods. We show that the greedy algorithm is
optimal for a broad class of problems, making brute force approaches unnecessary.

#### Disclamer
This repository contains research-style code and is not intended as a Python package. It utilizes several freely licensed packages for analysis. This project is a side endeavor, completed over a few weeks, aiming to address a specific question the authors pondered. It does not claim to present novel ideas, nor does it extensively research existing solutions to similar problems. No claim is made regarding the work's importance, interest, or novelty. It was not written with the intention of being made publicly available.

#### Background and Motivation
The initial inspiration for this work stemmed from the common experience of couples moving in together. In such scenarios, numerous minor preferences and issues often differ between individuals — for example, the placement of pots and pans, the bed, or the couch. Frequently, one partner may hold stronger opinions on these matters, leading them to make most of the decisions. However, this can inadvertently make the other partner feel less at home, simply because they expressed less intense preferences. This project aimed to formulate a method to ensure both members of a couple feel heard and satisfied.

As the problem was formulated, it became clear that this scenario is analogous to many other two-party systems. In these systems, a "naive optimal solution" — simply choosing the option that is most significantly preferred — can lead to all decisions consistently favoring one side. For instance, in politics, bills are passed based on a majority vote. While this ensures that most passed bills benefit the majority, it can inadvertently neglect the interests of smaller groups.

#### Repository Structure
The repository is organized into three directories:
- `paper`: Contains the LaTeX source and PDF of this work, presented as a pseudo-note style report (not peer-reviewed or intended for publication).
- `scripts`: Stores the Python and C++ scripts for various optimization methods.
- `notebooks`: Houses the main notebook used for simulating data and generating results.