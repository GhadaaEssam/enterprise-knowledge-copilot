# Source: https://engineering.hmn.md/how-we-work/process/reviews/

# Code Reviews

Code reviews ensure the quality of what we’re building remains high, and that code we’re vouching for remains up to the same standard. Reviews are primarily about assessing the code *quality*, not necessarily the behaviour. The code author is the one responsible for writing the code and making sure it works, while the reviewer is there to review the code.

Every piece of code we push into production must undergo review by at least one other engineer. Code may be pushed to staging without review if it is not touching real client data, but should typically be reviewed anyway.

## Types of Reviews [#](#types-of-reviews)

There are three main styles of review that we undertake:

* **External Reviews** – Third-party plugins we’re seeking to use.
* **Internal Reviews** – Standard reviewing process before code is deployed live into production.
* **In-Depth Reviews** – Internal reviews, but for tricky features.

Each of these styles of review has different factors to check for, but generally speaking, internal reviews are stricter on code quality checks, while external reviews are stricter on security and performance checks. Generally speaking, internal reviews have a higher level of trust, so reviews can focus more on ensuring quality is high. With that said, security and performance must always be a factor regardless of source, as they are critical to the end product.

If an external review reveals a plugin is technically OK, but has low code quality, checking for alternatives is typically a good idea. These plugins are generally harder to maintain, and are a [code smell](https://href.li/?https://blog.codinghorror.com/code-smells/). If a plugin has a large development team that is active, this can outweigh the code quality factor, but it’s always worth checking.

Internal reviews should generally be performed piecemeal on the project; in other words, they should be done on pull requests before merge. This provides a much smaller set of code to be reviewed, and allows more in-depth reviews. Larger blocks of code are harder to review fully. The flip-side of this is that it can be harder to see the larger picture of the whole project, so the reviewer should be conscious of how code fits into the context of the project. In-depth reviews can be done by-request when someone works on something and wants a closer look to verify what they’re doing is right.

Never be afraid to ask for clarification. If you spot something in a review that seems a bit weird, mention it. It’s easier to have a quick conversation in the PR comments to double-check, than to assume something is correct only to find the issue in production. Spending time writing an emergency fix and deploying it is much more expensive (in time, and potentially in revenue) than taking the time initially.

When working with code submitted by clients, differing levels of review may be applied. Generally speaking, we want to help our clients to think and work like us, so these reviews can be treated as internal reviews. Some client projects may necessitate different levels of reviewing, but should never be less strict than external reviews, as we need to vouch for this code. Style issues can be overlooked in these cases, but security can never be. Be pragmatic.

## Factors to Review [#](#factors-to-review)

### Security [#](#security)

Security is one of the biggest factors involved in any review. All code that we push into a production or staging environment must be completely secure.

For specific guidelines, consult the [frontend security](/standards/frontend/security/) and [backend security](/standards/backend/security/) standards.

### Performance [#](#performance)

Performance is very important with the scale of the sites we work on. Determining what is or isn’t performant is tough, and this role mostly falls on the code author. However, performance should also be checked by the reviewer, especially for external plugins that may not have been created with performance in mind.

For specific guidelines, consult the [frontend performance](/standards/frontend/performance/) and [backend performance](/standards/backend/performance/) standards.

### Accessibility [#](#accessibility)

Our work should be usable and accessible for as many users as possible. Reviewers should check for obviously inaccessible patterns.

For specific guidelines, consult the [accessibility best practices](/standards/frontend/best-practices/).

### Style [#](#style)

Code reviews should usually check that coding style matches [our coding style guidelines](/style/). If someone is intentionally ignoring a guideline, that’s fine too.

Internal reviews are typically the only ones that need style checking, as we’re not responsible for external plugins. The exception to this is if we’re specifically asked for it.

Style checks should mostly be automated, as it’s easy to miss when writing or during a review. This can be performed by the [coding standards checker](https://href.li/?https://github.com/humanmade/coding-standards), and can be enabled on a repo using the [linter bot](https://href.li/?https://github.com/humanmade/linter-bot).

### Behaviour and Logic [#](#behaviour-and-logic)

The actual behaviour of code typically does **not** need reviewing. Reviews are a process of checking work by others, not to duplicate that work again. Sometimes however, you may want your code double-checked, especially if you have some tricky logic.

Feel free to ask on any pull request for a more in-depth review; it’s always better to ask and not need it than to ship with something potentially broken. The best people to ask for these reviews are other people on the same project, as they can verify that the behaviour matches what they expect much more easily.

If your pull request involves changes to the frontend user interface of a site, you should consider including a screenshot of the relevant part of the page in your pull request description. Including screenshots assists reviewers in validating your stylesheet changes, and helps build awareness of new features and interactions across your team. For interactive elements you can use a screen recording tool like [LICEcap](https://href.li/?https://www.cockos.com/licecap/) (macOS & Windows) or [Peek](https://href.li/?https://github.com/phw/peek#readme) (Linux) to record a .gif file of the interaction.

## Automated code reviews. [#](#automated-code-reviews)

* All Altis projects should have the Altis Code Review checks configured. This runs the HM-Minimum ruleset, and is focused primarily on performance, security and best practices.
* The HM Linter Bot can be configured to check automatically for code style and more opinionated rules.
* Some projects use TravisCI, CircleCI, Github Actions (or other similar tools) to run coding standards checks.
* All automated checks should pass before requesting a code review from a human.

## Requesting a Review from a Human [#](#requesting-a-review-from-a-human)

When your code is ready for review, it’s up to you to request the review. The way to do this changes per-project so refer to project guidelines. Generally is handled via a “Needs Review” label as well as via a kanban column in your project management tool (Jira, ZenHub, GitHub’s etc)

Ideally reviews are handled by someone else working on the same project. But if that isn’t possible, anyone at Human Made can do code reviews. Ask in the [#dev-code-reviews](https://href.li/?https://hmn.slack.com/messages/C4B9GM1D5/) channel.

Reviewers are expected to approve, reject, or comment on the pull request, but should leave merging the pull request to the PR author unless asked specifically to merge.

### One comment

1. **Matthew Haines-Young** says:

   [June 8, 2026 at 4:45 pm](https://engineering.hmn.md/how-we-work/process/reviews/#comment-24)

   Shared by @matt in #eng-managers on Slack

Comments are closed.

Accessed Wed, 15 Nov 2017 07:57:41 +0000 from `https://engineering.hmn.md/how-we-work/process/reviews/`

[Made by Humans](https://hmn.md)