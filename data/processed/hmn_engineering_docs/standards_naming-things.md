# Naming and Terminology
At Human Made we put people first. Our culture is inclusive, kind & respectful. This is stated in our [company values](https://handbook.hmn.md/the-company/our-values/) & [aligns with the behaviour we expect everyone to ascribe to](https://handbook.hmn.md/the-company/behaviour-framework/).
It follows that the language that we use at work should support these values, and that extends to the code we write, our documentation, and the way we name things such as products or features. The language that we use needs to be inclusive, kind and respectful.
* Do not use racist language.
* Avoid sexist or unnecessarily gendered language.
* Avoid [ableist](https://href.li/?https://dictionary.cambridge.org/dictionary/english/ableist) language.
* Avoid language that could be harmful/hurtful to individuals.
* Avoid unnecessarily violent language.
Naming things is really hard, but here are some guidelines to follow when doing so.
* Be careful and deliberate about the words you use. Think about what they mean.
* Be mindful of associated meanings or connotations of terms as well as problems related to the context in which you're using them.
* Be aware of how language may be understood by others, from different cultural backgrounds or those who do not speak English as a first language.
* Just because something is the norm within the industry, doesn't mean we can't challenge that and improve on the naming.
* Relying on metaphors or jargon can be confusing and it is often better to use words that describe the technical behaviour more clearly.
* Be open to discussion. Suggestions on how we can be better should always be welcomed. We should always question, learn and improve, especially by listening to the viewpoints and experiences of others.
## Examples
The intention of these guidelines are to focus on the principles that you should follow, rather than providing a definitive list of terms you should avoid, however here are some real-life examples in which language used was improved to be more inclusive.
* The terms "Master/Slave" were fairly established industry terms used to describe technical operations and relationships. However there are clear issues here and in recent years, many within the industry have moved away from the use of these terms in this context in favour of more descriptive language such as "Primary/Replica". [See for example this changeset in Python](https://href.li/?https://bugs.python.org/issue34605).
* The 2011 Scrum Guide included the term "Backlog grooming" to describe a meeting in which items in the backlog are prepared for inclusion in the next sprint. Due to problematic connotations with the term ‘grooming', it was replaced with "Backlog Refinement" in the 2013 guide.
* Whitelist and blacklist are commonly used terms, but despite not being directly derived from racist language, using the metaphor that white is good and black is bad is problematic. Additionally, it contributes to the perpetuation of historical social issues and may make people uncomfortable. In this case, it may be better to avoid jargon/metaphor like this and use more direct and descriptive wording that is also more inclusive. e.g. `safeList` or `blockList`. For example, our `whitelist_html` library was renamed to [`clean_html`](https://href.li/?https://github.com/humanmade/clean-html/pull/7), which had the side-effect of making the functionality clearer.
* When we're trying to use language that is natural, friendly and conversational, it's really easy for problematic ableist language to slip in. Terms like crazy, dumb, cripple and sanity-check are all examples of this. There are plenty of alternatives to use here. For example ‘sanity check' could be swapped for ‘check for completeness and clarity'. Instead of ‘crazy', how about ‘baffling'?
* Similarly, violent language is often used in a very casual way. For example describing something as "killer", or saying something like "any developer who does this will be shot". In a professional context, when writing code or documentation, these metaphors are unnecessary and should be avoided.
* When describing user stories, avoid language that assumes gender e.g. "*He* navigates to the homepage on a mobile". English [has the gender neutral pronouns "they" and "them"](https://href.li/?https://www.merriam-webster.com/words-at-play/singular-nonbinary-they) which can be used instead, or alternatively reword to avoid the use of a pronoun completely e.g. "*The user* navigates to the homepage on a mobile"
* We say you should "challenge" industry norms, we're saying you have the freedom and permission to deviate even if it causes higher friction, as there's a broader goal to work towards. For example, a 3rd party API may include an endpoint `/api/whitelist`. However a function that calls this could be named `get_allowed_hosts` to avoid bringing this terminology into your codebase.
## Where can I learn more?
Here are some links on talks or further reading on the topic.
* [Talk at JSConf EU: The Etymology of Programming - Brittany Storoz](https://href.li/?https://www.youtube.com/watch?v=2KTK2qD4-gs&feature=emb_title)
* [Buffer article on inclusive language in tech](https://href.li/?https://open.buffer.com/inclusive-language-tech/)
* [Google developer style guidelines on writing inclusive documentation](https://href.li/?https://developers.google.com/style/inclusive-documentation)
* [Human Made branding guidelines, see section 5 on "Our voice" including tone and language.](https://handbook.hmn.md/the-company/branding/human-made/)