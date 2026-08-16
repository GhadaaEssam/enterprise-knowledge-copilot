# Source: https://engineering.hmn.md/standards/frontend/best-practices/

# Best Practices

## Perceived Performance [#](#perceived-performance)

Perceived performance is how performant the user perceives the site, as opposed to the technical measurements of performance. While technical performance is important, perceived performance can have a greater effect on the users willingness to stay on the site.

Perceived performance is typically measured as the time it takes for the content to be usable, this may occur before assets have finished rendering (images, fonts, JavaScript).

Perceived performance can be improved by

* Using system fonts
* If web fonts are used, initial render ought to use system fonts and switch to the web font once it completes loading (FOUT). In recent browsers this can be achieved in CSS using [`font-display: swap`](https://href.li/?https://developer.mozilla.org/en-US/docs/Web/CSS/@font-face/font-display) in older browsers the [Font Face Observer](https://href.li/?https://fontfaceobserver.com/) JavaScript library can be used.
* Avoid unnecessary jumps.
* As assets load, images, advertisements, video and other embeds, they can cause text content to jump around on the page. Avoid this by using CSS and/or width and height attributes to allow space for this content to fill.
* Lazy load images

## Eliminate Unnecessary Downloads [#](#eliminate-unnecessary-downloads)

Render blocking downloads will have the largest effect on the perceived performance of a web page. Having some blocking requests is unavoidable but they should be kept to a minimum. Google’s Lighthouse documentation [identifies render blocking resources](https://href.li/?https://developers.google.com/web/tools/lighthouse/audits/blocking-resources#more-info).

Assets used together should be combined into as few downloads as possible. Each file added to a web page introduces additional overhead – even on HTTP/2.

## Progressive Enhancement [#](#progressive-enhancement)

Progressive enhancement emphasizes core webpage content first. This strategy then progressively adds more nuanced and technically rigorous layers of presentation and features on top of the content as the end-user’s browser/internet connection allow.\*

The order of displaying content:  
First content (HTML), then presentation (CSS) and after that client-side scripting ([Chocolatey Layers of Progressive Enhancement](https://href.li/?https://alistapart.com/article/understandingprogressiveenhancement)).

The basic render should include content for the lowest end browsers and allow for JavaScript to fail. Additional content (carousel frames, items behind accordions, etc) can be loaded and rendered via JavaScript.

React projects should include server side rendering, this can take one of two approaches:

* JavaScript first: basic WordPress PHP templates can be used to render the initial response and be replaced/improved upon with React.
* JavaScript only: use the same code base to render code in both the client and the server. For internal projects, [humanmade/react-wp-ssr](https://href.li/?https://github.com/humanmade/react-wp-ssr) is included in HM Cloud, for external projects [airbnb/hypernova](https://href.li/?https://github.com/airbnb/hypernova) enables rendering using a node server.

## Accessibility [#](#accessibility)

We aim to meet the [WCAG accessibility guidelines](https://href.li/?https://webaim.org/standards/wcag/checklist) at level AA.

The most important topics for accessibility are:

* [Semantic, error free HTML5](https://href.li/?https://wpaccessibility.org/docs/topics/)
* All essential functionality can be executed by keyboard only
* All content is available for all users
* A logical order of content in a web page, [tell a story with your HTML](https://href.li/?https://rianrietveld.com/2014/11/14/storytelling-html-practical-accessibility/)
* Dynamic changes on a web page are announced
* Good colour contrast between text and background
* Colour alone isn’t used to convey meaning (for example with error messages)
* Animation is stoppable by the user

In the [Markup Style Guide](/standards/style/markup/) and the [WordPress Accessibility Handbook](https://href.li/?https://make.wordpress.org/accessibility/handbook/best-practices/) you’ll find information on how to apply this in your work.

Accessed Mon, 26 Feb 2018 10:02:33 +0000 from `https://engineering.hmn.md/standards/frontend/best-practices/`

[Made by Humans](https://hmn.md)