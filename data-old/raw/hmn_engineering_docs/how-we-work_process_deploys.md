# Source: https://engineering.hmn.md/how-we-work/process/deploys/

# Deploys

After you’ve created a site, you’ll need to deploy it somehow. The process for this differs between projects hosted on HM Cloud, and projects hosted on WordPress.com VIP.

## Hosted on Altis [#](#hosted-on-altis)

For projects hosted on Altis, all deployment is handled internally, and developers have the ability to self-deploy when necessary.

Deployments are created from [Altis Dashboard](https://href.li/?https://www.altis-dxp.com/resources/docs/cloud/dashboard/). This allows build tools to be integrated into the `.build-script`, so generated files (minified JS, etc) should not be committed into the repository.

While code does not have to pass through multiple levels of review like the VIP deployment process, all code must be [reviewed before merge](https://href.li/?https://www.altis-dxp.com/resources/docs/guides/code-review/) to ensure code quality in any case.

## Hosted on WordPress.com VIP [#](#hosted-on-wordpress-com-vip)

VIP projects follow an entirely different deployment process. This is slightly different between VIP Classic and VIP Go, but mostly follows the same process.

Code pushed into `master` is pushed into a “deploy queue” internally, and the VIP team [reviews this](https://href.li/?https://vip.wordpress.com/documentation/vip/code-and-theme-review-process/#deploy-review) typically within a day (potentially faster depending on the SLA for the project). After review, VIP will then deploy this code at their discretion.

Deploys can [be scheduled](https://href.li/?https://vip.wordpress.com/documentation/vip/scheduled-deploys/) if necessary, but should typically be avoided.

Deploying is a multi-step process, as code needs to be submitted from our Git repository to the VIP SVN (for VIP Classic) or Git (for VIP Go) repository for the site. ZenDesk should also be monitored for post-deploy messages from the VIP team, which may note [warnings that should be fixed](https://href.li/?https://vip.wordpress.com/documentation/vip-go/code-review-blockers-warnings-notices/), but which aren’t blockers.

### VIP Go [#](#vip-go)

During development, [other environments](https://href.li/?https://vip.wordpress.com/documentation/vip-go/vip-go-environments/) can be used to set up development or staging sites. With these secondary environments, code is automatically deployed upon pushing code.

Keep an eye out for changes on the Go repository from the WordPress.com VIP team that may need to be applied to the canonical internal repository. This may appear unexpectedly in the diff when synchronising code across, and will require porting across to the main repository before deploy.

If you need the ability to deploy built code (such as JS/CSS bundles), it’s best to use the [VIP Go Builder](https://href.li/?https://github.com/humanmade/vip-go-builder) tool. This avoids needing to commit the built code, and ensures these files don’t constantly cause merge conflicts.

Accessed Wed, 15 Nov 2017 07:57:41 +0000 from `https://engineering.hmn.md/how-we-work/process/deploys/`

[Made by Humans](https://hmn.md)