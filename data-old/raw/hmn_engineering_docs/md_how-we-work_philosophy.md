# Source: https://engineering.hmn.md/md/how-we-work/philosophy/

# Philosophy

At Human Made we strive to provide our clients with **value** above all else. With that in mind, the following pages outline a framework for how to approach engineering work.

## Principles [#](#principles)

* [Built to Last](/how-we-work/philosophy/built-to-last/)
  + Projects need to be built to last so they can be maintained for years to come.
* [Modularity](/how-we-work/philosophy/modularity/)
  + We design software to be modular for flexibility, and the future ability to spin it off as open-source.
* [Completion](/how-we-work/philosophy/completion/)
  + Sometimes, software is *just done*.

## Assume every problem has already been solved [#](#assume-every-problem-has-already-been-solved)

* Don’t dive immediately into code, stop and think
* Search the web
* Search the [HM GitHub org](https://href.li/?https://github.com/humanmade)
* Search the [Dev H2](https://dev.hmn.md/)
* Ask in [Slack #dev](https://href.li/?https://hmn.slack.com/archives/C03K3J34A) or the Dev H2

## Prefer action over discussion [#](#prefer-action-over-discussion)

* This is the nature of open source: see a missing README? A typo? Out of date docs? If you have time to express your frustration, you have time to create a pull request or issue to improve the situation
* We should all hold each other accountable to this standard, regardless of job title or seniority
* If you’re working around a problem, attempt to fix it upstream as well, even if you can’t use the fix right away
  + When necessary a GitHub pull request can serve as the source for a composer patch even if the upstream project is slow to accept changes

## Avoid exceptionalism [#](#avoid-exceptionalism)

* Not everything needs to adhere to HM Coding Standards, consistency is more important
* Just because a plugin uses patterns or a code style you don’t like doesn’t mean it can’t provide value
* While it’s tempting to solve a problem from scratch the way you think is best, consider the long term. Contributing to existing work can have a much wider impact

## Over-communicate [#](#over-communicate)

* Talk about development work in client channels: it builds confidence, trust, and creates opportunities for better outcomes
* Keep your team (including clients) informed what you’re doing, especially if it may affect them (*e.g.* deploys)

## Check your notifications [#](#check-your-notifications)

* Open tickets, code reviews and work in progress in a sprint should be considered “active”, this is your highest priority so monitor your inbox
* If colleagues/clients are chasing you for code reviews or feedback that you need to address, consider whether you need to reset their expectations or whether you need to be more proactive following up or acknowledging them.

## Open Source is our default [#](#open-source-is-our-default)

* If a piece of functionality can be packaged as a self-contained plugin or unit, then do so. Factor this into your estimates
* Beware of monolithic build tools and other processes that make it difficult to share code. Favour reusable, community-maintained tools like `wp-scripts` and `npx @wordpress/create-block`
* You don’t need to have a full README or docs to publish code, as long as there’s at minimum a basic description that’s searchable and explains the purpose of the repository

## Solve the problem you have now, not ones you might have later [#](#solve-the-problem-you-have-now-not-ones-you-might-have-later)

* Don’t optimise prematurely or spend a long time accounting for theoretical problems that may never occur
* When we build in a modular way and share code, it’s easier to iterate when we need to solve additional problems later on

## Ownership is a shared responsibility [#](#ownership-is-a-shared-responsibility)

* The individual who created a repo or has the most commits against it is a good person to tag for code reviews or questions, but you can also rely on your squad’s Principal and EM to unblock contributions and updates to shared HM repos
* If you are the original author of some code, avoid being too protective or precious about minor issues if it means you are hindering a colleague’s progress. You can always make changes later

## Favour community tools [#](#favour-community-tools)

* Use WordPress core build tools whenever possible
* If you hit limitations, try to solve them for the wider community rather than going bespoke straight away

## Stay up to date with WordPress core [#](#stay-up-to-date-with-wordpress-core)

* Always read the [WordPress release field guides](https://href.li/?https://make.wordpress.org/core/tag/field-guide/)
* Pay attention to ongoing core projects
* Use what you learn to keep Human Made at the forefront of WP development
* Use what you learn to uncover new opportunities for our clients

## Learn to recognise and raise sales opportunities [#](#learn-to-recognise-and-raise-sales-opportunities)

Technical debt, performance issues, and bad architecture are all opportunities to increase value. Even if it’s code we wrote, we keep learning and improving and it benefits our clients to raise opportunities for improvement.

It can feel like some projects are stuck, horrible, and demotivating to work on etc. Reframe this: what can we do increase the value the client gets while also making our own lives easier?

Work with your squad’s Account Manager to propose new work for existing clients that will benefit both them and us.

Accessed Wed, 15 Nov 2017 07:57:41 +0000 from `https://engineering.hmn.md/how-we-work/philosophy/`

[Made by Humans](https://hmn.md)