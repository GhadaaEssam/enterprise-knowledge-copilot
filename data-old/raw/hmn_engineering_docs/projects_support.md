# Source: https://engineering.hmn.md/projects/support/

# Support for Projects

Human Made releases a lot of open-source projects to the community based on our internal work. We also have a limited amount of time to support these projects, so this support guide outlines what you can expect from our projects.

This support policy applies to our open-source plugins and libraries, unless otherwise noted. We are able to provide professional support as part of the [Altis platform](https://href.li/?https://www.altis-dxp.com/).

Our projects are released into the wild for the benefit of everyone, but it’s important to set expectations if you’d like to use these projects.

## Designed for Developers [#](#designed-for-developers)

We design our plugins for other developers. This means that running our plugins involves a certain level of technical proficiency. At the very least, you need to be able to configure the plugin via constants or filters, and attempt to debug issues before filing.

Please do not ask for support before trying to debug the issue yourself. We’re always happy to give pointers, but issues filed without enough detail to examine the bug will be closed. We cannot provide general user support for these plugins, so if you don’t have the ability to debug them yourself, you may be better running a user-focussed plugin with UI.

If you absolutely need functionality or support, we’re happy to [offer consultation](https://hmn.md/does/) on a paid contract basis.

## Our Promise [#](#our-promise)

As a flip-side to what we expect of users, you can expect things from us:

* **We promise to provide high-quality, production-ready code.**   
  Our projects are designed for high-traffic production sites. While we do release some unready/in-development code, we’ll try and label this to make it clear. Where possible, we’ll also try and label projects with which client projects they’re being used on to make it clear when they’re running in production.
* **We promise that our open-source code matches code in production.**   
  We don’t run a special version of our plugins internally with additional fixes. We own these plugins from beginning to end, so if an issue pops up in them, we’ll fix the plugin publicly.
* **We promise to keep our code lightweight.**   
  Bloat is the easiest way to make a project unmaintainable, and we’re actively trying to fight that. Our plugins typically don’t have settings UI, instead using constants or filters, allowing flexibility without bloating the UI. We also keep the core of our plugins lightweight following the [Complete Software](/how-we-work/philosophy/completion/) principles. New features will be handled in additional plugins rather than bundling into the core. This also means that we’ll try and make our code as extensible as possible. We need the extensibility for our internal use, and it enables an ecosystem around the code without needing us to be as involved.

Accessed Wed, 15 Nov 2017 07:57:41 +0000 from `https://engineering.hmn.md/projects/support/`

[Made by Humans](https://hmn.md)