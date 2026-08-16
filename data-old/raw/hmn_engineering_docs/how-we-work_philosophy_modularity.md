# Source: https://engineering.hmn.md/how-we-work/philosophy/modularity/

# Modularity

Our products are designed modularly. This gives us the flexibility to add, remove and change parts of our products without needing to rewrite the core or other modules. It also gives us the ability to spin parts of our products off as open-source plugins or as internally reusable code.

Where possible, modules should interact with each other through the use of actions and filters. Actions and filters are actually an implementation of the [Mediator pattern](https://href.li/?https://en.wikipedia.org/wiki/Mediator_pattern), and mediating between different parts of code is where hooks truly shine. It’s important to also note that this is mediation between two modules; that is, your module should have functionality independent of the hooks. Although building functionality directly into your callbacks may get it working, it’s prone to breaking.

Note however that we do not enforce barriers between modules. Sometimes, it makes more sense to have modules depend on one another than to force everything to communicate via a mediator. Forcing a system often leads to making it overly generic, which can reduce both readability and performance. In a lot of cases, code will need to be rewritten when changing other modules for other reasons anyway (sending extra data, for example), so be pragmatic.

Ensuring your code is as modular as possible means we can later pull it out to reuse it. Cavalcade, HM Rewrite, and Static Mirror are all examples of where we’ve taken a plugin built specifically for one project and turned it into a plugin.

Open sourcing plugins for outside development means extra eyes on the code, which can aid in improving the code quality further and reducing bugs. Giving back to the community means not just contributing to existing projects, but ensuring the future of the community by releasing new ones.

The typical [project structure](/standards/structure/) uses modular plugins to separate out the various pieces of functionality in projects.

Accessed Mon, 26 Feb 2018 10:02:29 +0000 from `https://engineering.hmn.md/how-we-work/philosophy/modularity/`

[Made by Humans](https://hmn.md)