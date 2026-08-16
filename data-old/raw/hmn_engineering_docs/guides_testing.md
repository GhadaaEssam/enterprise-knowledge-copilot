# Source: https://engineering.hmn.md/guides/testing/

# Testing

* [Accessibility Testing](/guides/testing/accessibility/) Testing for accessibility.
* [Continuous Integration](/guides/testing/adding-ci/) How to set up Continuous Integration
* [PHPUnit](/guides/testing/phpunit/) Getting started with PHPUnit for WordPress project

## Types of Tests [#](#types-of-tests)

It’s important to know that there’s many different types of tests you can write. There are some common types we employ though in practice we mostly write integration tests:

* **Integration** tests run a piece of code in the context of the larger application, with services such as databases, cache servers etc…
* **Unit** tests test a single”unit” of your code such as a function. The dependencies of that code would be mocked out (replaced by fake versions) so that it’s fully isolated
* **Behavioural or Acceptance** tests simulate user interactions with your application, helpful for preventing regressions in key features
* **Performance** benchmarking is a means of setting a baseline and comparing how well an application or function performs before and after some changes
* **Accessibility** testing consists of frontend (DOM) validation, keyboard testing and screen reader testing. DOM validation can be partially automated, while keyboard and screen reader testing still needs to be done manually.

There are many other types of tests, including visual regression testing. Feel free to explore the other options available to see if anything better suits your project.

There are many other types of tests, including visual regression testing, as well as tonnes of alternative tools, but we don’t tend to use those. Feel free to explore the other options available to see if anything better suits your project.

### What tests should I write? [#](#what-tests-should-i-write)

It’s entirely subjective as to what sort of tests you should write, and how many tests you should write. This section is my opinion. – RM

Depending on what sort of project you want to test, the mix of tests may be different:

* For pure libraries, unit tests are typically the best way to ensure that your library behaves as expected. Libraries are expected to be self-contained units, although integration tests should be used to ensure your library interfaces with other libraries or external services correctly.
* For plugins, integration tests are mostly what you want to write. The entire purpose of most plugins is to interface with WordPress. Although writing unit tests may help here too, the effort required to mock out parts of WordPress is mostly not worth it, and you’ll likely need lots of integration tests *anyway*. A lot of the benefit of testing here comes from integration tests.
* For themes or entire sites, behavioural tests will give the best value. These test that your site/theme behaves the way you expect, with links, elements, etc existing where they should on the rendered site. Unit or integration tests are not usually as important here.

Each project will have its own requirements for the numer and type of tests you need. Large site builds may have unit and integration tests for underlying plugins and libraries, and behavioural tests for the theme as a whole.

Typically, libraries and plugins should aim for 100% test coverage, whether unit or integration tests. The specific nature of these tests depends on the plugin at hand. On the other hand, themes and sites warrant much less testing, as they’re immediately user-facing, and are less likely to break in subtle ways.

It’s important to always be mindful of how much time and effort testing takes, and to be pragmatic. It’d be great to have the entire codebase of every site 100% unit tested, but that’s often not realistic. Instead, test the underlying custom behaviour (plugins), and use behavioural tests to test edge-case functionality. Redistributable projects (open source plugins and libraries, e.g.) should be generally held to a higher standard, as they’re much more likely to hit edge cases.

Accessed Mon, 26 Feb 2018 10:02:26 +0000 from `https://engineering.hmn.md/guides/testing/`

[Made by Humans](https://hmn.md)