# Third Party Plugin Reviews
Human Made regularly makes use of existing third party plugins for WordPress during project delivery, subject to our company-wide standards for performance, security, and accessibility.
In the past the company has maintained a list of pre-approved third-party plugins for use on Altis and WordPress VIP, but due to differing and changing requirements between clients this is no longer the case. Delivery teams are responsible for ensuring that third-party plugins are fit for purpose for each project, and that they meet our engineering standards.
Within the WordPress ecosystem there are a number of long-established and trusted vendors who publish high quality plugins that we frequently use and recommend between projects. By default the delivery team should prefer using solutions from Altis Cloud Partners and WordPress VIP Agency Partners as they typically operate at the highest engineering standards.
## **Reviewing third party code**
As with any code we deploy to our platform, the minimum requirement is for third party plugins to pass an [Automated Code Review](https://href.li/?https://docs.altis-dxp.com/guides/code-review/).
ACR is cheap and fast. It should be used to assess the quality of a third party plugin during its initial consideration and code review, and to ensure its quality is maintained over time.
* This review can be run locally by any web engineer.
* Any code deployed to a development, staging, or production environment will automatically be run through ACR.
* The review is objective: it either passes or it fails.
* For clients that run scheduled penetration testing, the delivery team are responsible for triaging any issues that may arise and routing them to the third party supplier if necessary.
Delivery teams are discouraged from soliciting the Altis Cloud Team to perform code reviews on third party plugins. Some exceptions are:
* Legacy contracts that have specific stipulations for working with our Cloud Team.
* Where we are considering adopting the plugin as a part of our product.
## **Security requirements**
By default the [Human Made engineering standards for security](https://engineering.hmn.md/standards/backend/security/) are non-negotiable. Any code, whether third-party or first-party, must meet the key requirements of our security standards, including user input trust, input sanitisation, output escaping, authorisation, and intent.
A third-party plugin that does not meet these security standards is not only not a good fit for the engineering standards that our clients demand of us, but more importantly it risks impacting the confidentiality, integrity, and availability of the data and systems that our clients use.
[Human Made is SOC 2 certified](https://href.li/?https://humanmade.com/human-made-is-soc-2-certified/) and so are most of the platforms we deploy to, including Altis Cloud and WordPress VIP. This requires us to adhere to the highest standards of security and compliance at every level. Creating an exception to these standards in favour of hitting a delivery deadline is not acceptable.
Any exception to these security standards must be very carefully considered by the delivery team, must be fully justified, and must be explicitly tracked in the project's risk log. The delivery lead is responsible for escalating the risk awareness where necessary to the wider delivery team, Altis Cloud, or WordPress VIP.
## **When code fails review**
When code doesn't pass ACR, web engineers should take a subjective look at the specific errors flagged and make an assessment on how to proceed.
Some possibilities:
* Approach plugin authors about fixing the issues
* Work on fixes to push upstream
* Fork and fix issues
* Determine the validity and severity of errors, for example if they are relevant on production or otherwise aren't a risk given the context
* We might learn things that could help improve our Automated Code Review
* Seek out an alternative plugin
* Decide to build the feature ourselves
Depending on the types of issues, you'll need to discuss with and advise the client on the effort required for each alternative you decide to explore, the risks, and the value delivered.
When looking to resolve issues to move forward with a plugin (versus eliminating it as a candidate), it will be necessary to review each error individually. This can be labor intensive, and should be part of the cost-benefit discussion.
## **Consequences of working with code that doesn't meet our requirements**
If, after your assessment and with a full understanding of the issues the plugin has, the client wants to proceed with code that doesn't pass our review, they have this option. They need to then be made aware that they are responsible for any work involved if it has a negative impact on their site. It may also void their SLAs.
Make sure and discuss such decisions with the customer Account Manager before making any such decisions. All parties involved need to have a shared understanding of the risks and consequences.
## **Being good technical partners to our customers**
Being a good technical partner to our customers means helping them make informed decisions. Informed decisions cannot be rushed. As the Delivery Team working to provide Professional Services, you own these technical decisions. Ceding to time pressure or imposed solutions only does a disservice to our customers, no matter how uncomfortable those conversations may be.
Making informed decisions can only be the result of research and conversations across disciplines, where all parties are able to weigh the costs and benefits. If you are feeling pressured to make decisions that go against your better judgment, don't hesitate to discuss this with the customer Account Manager, or to reach out to the Director of Delivery for support.
### One comment
1. **Megan Rose** says:
[June 8, 2026 at 4:24 pm](https://engineering.hmn.md/how-we-work/process/reviews/third-party-plugin-reviews/#comment-23)
Shared by @megan-rose in #general on Slack
Comments are closed.