# Source: https://engineering.hmn.md/development-tools/

# Tools we use

This page aims to document some of the tools you need to do your job as an engineer at Human Made.

Some things are required, but generally we try to be flexible about what you use. If you’re already happy with your development setup, you probably won’t need to change much. That said, documenting some commonly used tools and configurations is still important.

## Essential Tools [#](#essential-tools)

These are the key tools you’ll *need* for day-to-day development, so make sure you have access to these. You should be given access to these as part of your induction, but if not, ask your Engineering Manager! Make sure to enable two-factor authentication where possible.

* *Laptop*. Most people use Apple laptops, and much of the guidance here reflects this. You are free to choose an alternative, and we have some engineers who use Windows or Linux, but there may not be so much support available from the rest of the team. Join the slack channels [#interests-linux](https://href.li/?https://slack.com/app_redirect?channel=C8347R134) or [#interests-windows-os](https://href.li/?https://slack.com/app_redirect?channel=CHBG43ML4) if you decide to use one of these platforms.
* *Git & [GitHub](https://href.li/?https://github.com/humanmade)* We use Github extensively, so you will need a github account. You’ll also need git installed on your computer.
* *[Slack](https://href.li/?https://hmn.slack.com/)*. Probably the main way we communicate. Download the app on your laptop. Make sure to join [#dev](https://href.li/?https://hmn.slack.com/messages/C03K3J34A/)! Installing the app on your phone can be useful too, but be careful that you’re able to switch off at the end of the day!
* [1Password](https://href.li/?https://1password.com/) Password managers are good for security to ensure we use strong and unique passwords. We also use 1Password to share access to sensitive information across the company. You will need to be added to the ‘engineer’ group. Projects will often have their own group or vault that you will be given access to when you join.
* [Zoom](https://href.li/?https://zoom.us). Most of our meetings are on zoom.
* Running sites locally.
  + *[Docker](https://href.li/?https://www.docker.com)* You will need this to run [Altis local server](https://href.li/?https://docs.altis-dxp.com/local-server/) and other modern WordPress local environments.
  + *Vagrant & Virtualbox*. Some projects may recommend or require using a Vagrant based local development environment (e.g. those using [Altis Local Chassis](https://href.li/?https://docs.altis-dxp.com/local-chassis/)), for which you will need to use both [Vagrant](https://href.li/?https://www.vagrantup.com/) and [Virtualbox](https://href.li/?https://www.virtualbox.org/).
* *[Node.js](https://href.li/?https://nodejs.org/en/).* You will need this to run most local build processes. We recommend installing Node using [nvm](https://href.li/?https://github.com/nvm-sh/nvm) so that it is easier to switch between different versions depending on your project.
* *Code Editor.* You’re free to use whatever you want to write code, but you’ll need something. Here are the most commonly used code editors at Human Made. See below for some tips.
  + [VS Code](https://href.li/?https://code.visualstudio.com/)
  + [PHP Storm](https://href.li/?https://www.jetbrains.com/phpstorm/)
* Terminal app.
  + MacOS
    - Terminal.app
    - Other app e.g. [iTerm](https://href.li/?https://iterm2.com/) or [Hyper](https://href.li/?https://hyper.is/).
    - One built into your code editor.
* Web browser!

Also refer to the [company handbook tools page for a reference on other tools used across the company](https://handbook.hmn.md/working-here/tools/).

There are other tools that may be essential for the project you’re working on (e.g. project management tools such as Jira), but you probably don’t need access to it until you actually need it. Individual projects will have their own onboarding process to ensure you have access to everything required when you join. However if you feel that you don’t have access to something that you should, don’t be afraid to ask.

## Optional tools [#](#optional-tools)

None of these tools are essential, but are things that engineers at Human Made use as part of their setup. You won’t need to install all of them right away, but take a look and you can install things as and when you need them.

* Database management application.
  + MacOS
    - [SequelPro](https://href.li/?https://www.sequelpro.com/)
    - [SequelAce](https://href.li/?https://github.com/Sequel-Ace/Sequel-Ace)
  + Linux or Cross-Platform
    - [TablePlus](https://href.li/?https://tableplus.com/)
    - [DBeaver](https://href.li/?https://dbeaver.io/)
* Git GUI. Whilst we encourage you to become comfortable using git on the command line, sometimes having a nice interface is a huge help.
  + MacOS
    - [Sourcetree](https://href.li/?https://www.sourcetreeapp.com/).
* Git merge tool
  + MacOS
    - [Araxis merge](https://href.li/?https://www.araxis.com/merge/index.en)
* API tool. Not essential, but can be really useful if you’re doing a lot of work with APIs.
  + MacOS
    - [Postman](https://href.li/?https://www.postman.com/)
    - [Paw](https://href.li/?https://paw.cloud/)

## Setting up your code editor [#](#setting-up-your-code-editor)

### VS Code [#](#vs-code)

Some useful settings and extensions.

* [PHP Intelephense.](https://href.li/?https://marketplace.visualstudio.com/items?itemName=bmewburn.vscode-intelephense-client)
* [PHP Debug](https://href.li/?https://marketplace.visualstudio.com/items?itemName=felixfbecker.php-debug)
* [PHP Sniffer & Beautifier](https://href.li/?https://marketplace.visualstudio.com/items?itemName=ValeryanM.vscode-phpsab). Also add `"phpcs.showSources": true` to your settings.json so that you can see the specific PHPCS rule that’s failing in the `Problems` tab message.
* [PHP Docblocker](https://href.li/?https://marketplace.visualstudio.com/items?itemName=neilbrayfield.php-docblocker) and [Document This](https://href.li/?https://marketplace.visualstudio.com/items?itemName=oouo-diogo-perdigao.docthis)
* [ESLint](https://href.li/?https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint)
* [Stylelint](https://href.li/?https://marketplace.visualstudio.com/items?itemName=stylelint.vscode-stylelint)
* [WordPress snippets](https://href.li/?https://marketplace.visualstudio.com/items?itemName=wordpresstoolbox.wordpress-toolbox)
* [WordPress Gutenberg Snippets](https://href.li/?https://marketplace.visualstudio.com/items?itemName=BenjaminZekavica.wordpress-gutenberg-snippets)
* [Gitlens](https://href.li/?https://marketplace.visualstudio.com/items?itemName=eamodio.gitlens)
* Colorize bracket pairs for easier identification by adding `"editor.bracketPairColorization.enabled": true` to your settings.json.
* [Import cost](https://href.li/?https://marketplace.visualstudio.com/items?itemName=wix.vscode-import-cost) or you can use [Bundlephobia](https://href.li/?https://bundlephobia.com/)

### PHP Storm [#](#php-storm)

To do.

## How We Work [#](#how-we-work)

This whole section of the handbook is about how Human Made works, and you should probably read all of it for a good overview. If you’re short of time, the key documents to read are the [development process](/how-we-work/process/development/) and [review process](/how-we-work/process/reviews/) pages.

## We’re Here to Help [#](#were-here-to-help)

Your manager and project team will help you get up to speed quickly, but everybody at Human Made is here to support you as well. If you see anything in these onboarding documents that doesn’t make sense or does not work for you — a broken link, an unfamiliar concept, something that looks outdated — don’t be afraid to ask questions!

You can ask questions in `#general` or `#dev` in Slack, message anybody directly, or join somebody’s office hours zoom. Please do not hesitate if you need assistance in any way.

We’re glad to have you on the team — welcome to Human Made!

Accessed Mon, 04 Oct 2021 08:46:18 +0000 from `https://engineering.hmn.md/how-we-work/development-tools/`

[Made by Humans](https://hmn.md)