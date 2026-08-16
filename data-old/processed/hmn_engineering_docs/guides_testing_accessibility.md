# Accessibility Testing
Web accessibility aims to create an online space that is available to everyone, and a key part of that is designing websites and software that are flexible for all user needs. It not only helps to deliver content to more people, but small improvements such as the correct semantic use of HTML, CSS and JavaScript will make websites more robust and better prepared for future technologies.
Testing for accessibility involves a combination of automated testing and manual QA testing. Many of the automated tests are run against the generated content on the site, so depending on the project's set up, may need to be manually run in a browser (e.g. [HTML\_CodeSniffer](https://href.li/?http://squizlabs.github.io/HTML_CodeSniffer/)).
The authoritative source for accessibility testing is the [WordPress.org Accessibility Handbook](https://href.li/?https://make.wordpress.org/accessibility/handbook/best-practices/test-for-web-accessibility/), which is maintained by the WordPress Accessibility team. This guide contains a lot more information about accessibility best practices and testing.
## Guidelines
We aim to meet the [WCAG accessibility guidelines](https://href.li/?https://webaim.org/standards/wcag/checklist) at level AA as described in our [frontend best practices](/standards/frontend/best-practices/). Depending on whether a site is being used as a governmental or public service, a different set of legal requirements may apply and this may be a strict requirement.
The Make WordPress Accessible Handbook contains a dedicated section about [Testing for web accessibility](https://href.li/?https://make.wordpress.org/accessibility/handbook/best-practices/test-for-web-accessibility/) with steps and resources.
## Workflow and Design
Everyone needs to play their part in making the web accessible; from developers to editors, to designers, theme builders, and content creators.
Accessibility consideration for a project should start during the design process (or earlier if possible), with the branding colours and font styles of the client. Ensuring design is accessible at this stage is key to avoid surprises and redundant work later in the project. By testing and adjusting early in the process, you can prevent extra work and refactoring afterwards.
The following design guidelines should be considered:
* Fonts should be made as thick as the design allows, and [not be too thin](https://href.li/?https://uxdict.io/lights-fonts-good-or-bad-for-the-user-931088d2be86)
* Use more than just colour to highlight information
* Make links stand out in sentences by underlining them
* Provide one clear and unique title per page (h1)
* Use borders for input fields and provide them with visual labels
* Provide three ways to find and navigate content, such as:
+ a consistent menu
+ a search field
+ a sitemap
* Avoid using capitalised text
* Avoid using animation that can't be controlled or stopped by the user
For text in designs:
* Use real text rather than text within graphics
* Select basic, simple, easily-readable fonts
* Use a limited number of fonts
* Avoid small font sizes: use 16px or larger, depending on the font
* Don't rely only on the appearance of the font (colour, shape, font variation, placement, etc.) to convey meaning
* Review your branding colours for adequate colour contrast with the background colour, before you use them in a web design. All text must have a high colour contrast, including headings and text placed on images
* Recommended fonts:
+ Use standard fonts, natively available in the browser for content text
+ For online reading, sans-serif fonts (e.g. Arial, Verdana) are generally considered more legible than serif fonts (Times New Roman), narrow fonts or decorative fonts. Decorative and narrow fonts, in particular, should be reserved for headlines and decorative texts only
### Colour contrast
Designs should always ensure there is sufficient contrast between text and background colours. Colour contrast ratio between text and background must be:
* 4.5 or more for normal text
* 3.1 or more for larger text of at least 24 pixels or 19 pixels bold
Colour contrast can be tested using various tools:
* WebaXe - [Broad overview of tools](https://href.li/?http://www.webaxe.org/color-contrast-tools/)
* Snook - [Colour contrast checker](https://href.li/?https://snook.ca/technical/colour_contrast/colour.html)
* ColorA11y - [Colour contrast browser extension for Google Chrome](https://href.li/?https://chrome.google.com/webstore/detail/colora11y/icfneoldcbdmgaiocnnobpbbjncdfbfb?hl=en)
* Sim Daltonism - [Colour blindness simulator](https://href.li/?https://michelf.ca/projects/sim-daltonism/)
## Frontend (DOM) validation
An overview of how to test the DOM for accessibility is given [in the Make WordPress Accessible Handbook](https://href.li/?https://make.wordpress.org/accessibility/handbook/test-for-web-accessibility/test-for-web-accessibility-frontend-code/).
This guide includes checks, tools and resources for:
* Keyboard navigation
* W3C and WCAG 2 AA validation
* Setting up automated testing in the browser and the command line
* Testing dynamic content with a screen reader
As frontend accessibility testing needs to run against the final generated DOM, tests must be run in a full browser. While automated DOM testing does exist, this often requires painful setup. Additionally, current state-of-the-art automated testing does not capture all errors; testing keyboard accessibility and announcing of dynamic changes by a screen reader cannot currently be automated.
Some minor errors can be detected by static analysis, such as the [JSX accessibility plugin](https://href.li/?https://github.com/evcohen/eslint-plugin-jsx-a11y). This only tests for small, specific issues that would cause your code to be inaccessible, and does not guarantee that the generated pages are accessible.
The JSX accessibility are included as part of the [React coding standards](/standards/style/react/).
## Content checks
After the site is built, it still needs to be filled with content. It's important that this content is tested and reviewed as well.
An overview of how to test the content for accessibility is given in [the Make WordPress Accessible Handbook](https://href.li/?https://make.wordpress.org/accessibility/handbook/best-practices/test-for-web-accessibility/test-for-web-accessibility-content/).
This guide includes checks, tools and resources for:
* Reading levels
* Heading structure
* Link texts
* Alternative text for images
* Audio and video
If the site includes dynamic interactive elements (for example, dynamic forms) or custom HTML, you should also apply the DOM validation steps as well, including keyboard navigation testing.
## Further Resources
* [Accessible Design: A Process](https://href.li/?https://humanmade.com/2017/11/09/accessible-design-a-process/) (Human Made blog)
* [Accessibility testing](https://href.li/?https://humanmade.com/2017/12/01/accessibility-testing/) (Human Made blog)
* [Make WordPress Accessible Handbook](https://href.li/?https://make.wordpress.org/accessibility/handbook/)