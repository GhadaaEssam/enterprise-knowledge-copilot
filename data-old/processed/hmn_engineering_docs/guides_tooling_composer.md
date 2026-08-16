# Composer
[Composer](https://href.li/?https://getcomposer.org/) is the industry standard package manager for PHP. We use it in most projects now, and Altis is completely built around it.
Composer allows us to pull in plugins and other dependencies at build time, and allows us to avoid the inherent issues with git submodules getting out of sync.
You should familiarise yourself with the [basic concepts of Composer](https://href.li/?https://getcomposer.org/doc/01-basic-usage.md), and it will help you a lot to understand the [full schema of composer.json](https://href.li/?https://getcomposer.org/doc/04-schema.md), and what you can do with it.
## Best practices
* Avoid pinning versions to branches e.g. `dev-main` unless you really know what you are doing. A `composer update` could completely change the code you're running if you aren't careful.
* Do not run `composer update` unless you are intending to update the `composer.lock` file and the pinned versions within it. Use `composer install` to get an exact match to the codebase that will be deployed.
* Avoid setting `minimum-stability` to anything less than `stable` unless absolutely necessary. It is better to favour [inline aliases](https://href.li/?https://getcomposer.org/doc/articles/aliases.md#require-inline-alias) to keep workarounds scoped to a single package.
### Exceptions
We occasionally encounter issues where a feature in one project targets a specific branch in a dependency, causing problems if the feature is merged before the dependency is fully integrated into a release. Additionally, targeted branches can accidentally be altered, leading to unexpected failures.
#### Ensuring Completion of Tickets
A ticket should not be considered complete until:
* The third-party dependency has been updated with the necessary feature.
* The feature has been merged into the dependency's official release.
* The dependency version in our project has been updated accordingly.
To avoid issues, we should minimise targeting specific branches wherever possible. Instead, we should wait for an official release or at least a stable tag before integrating it into our project.
#### Temporary Branch Targeting
In cases where a hotfix is required and an immediate solution is needed, we can use Composer to allow a feature branch while keeping a stable version as a fallback. This is done using the following syntax:
```
"external/feature": "dev-feature-branch || 2.3.4"
```
This allows Composer to use `dev-feature-branch` if it exists but fall back to `2.3.4` (e.g. a stable branch) if the branch is unavailable. Once the feature is fully merged into a release, the branch reference should be removed.
#### Version Targeting with Patch Updates
You can also use the tilde version constraint (e.g. `~2.3.4`) to opt in to patch version updates. Coupled with the branch || tag syntax, e.g:
```
"external/feature": "dev-feature-branch || ~2.3.4"
```
This tells Composer to use the `dev-feature-branch` if available, but otherwise to use the latest patch version from the `2.3` release. This adds flexibility and keeps things stable without locking us to a single patch release.
---
By following these guidelines, we ensure a more stable and maintainable dependency management process while reducing the risk of broken integrations.
## Publishing to packagist
You should always aim to publish open source plugins to packagist.org.
***Note:** before you can publish a package under the `humanmade` namespace you need to be added as a maintainer of another package within the namespace. Message your EM, @rob, @rmccue or @joe to be added to a package if you haven't been already. If you are adding an engineer to a project for the first time use [https://packagist.org/packages/humanmade/s3-uploads](https://href.li/?https://packagist.org/packages/humanmade/s3-uploads)*.
The process is:
* Run `composer init` and follow the steps to generate your `composer.json`
* Choose `wordpress-plugin`, or one of the other `wordpress-*` package types as needed
* Require `composer/installers` with the version constraint set to `^1 || ^2`
* Login to packagist.org using your GitHub account
* Submit the package via the "Submit" link and entering the URL to the plugin's GitHub repo
It is recommended to invite more than one HM engineer to each package on packagist, so that it can still be managed in case of absence or leaving the company.
If you need to change or adds maintainers can email Jordi Boggiano the maintainer at [j.boggiano@seld.be](mailto:j.boggiano@seld.be) (lovely chap) using your humanmade.com email address and request it.
## Premium plugins / Closed source
Some code can never be published on packagist.org. In some cases it might be easiest to commit them to the repository in full, or you can add a private git repo as a source in `composer.json`, however you would also need to make sure all team members and build processes have access to that repository too.
An easier option is to use our private packagist repository:
## packagist.hmn.md
This is our private packagist repository hosted on instawp.app, and powered by [SatisPress](https://href.li/?https://github.com/cedaro/satispress), a WordPress plugin that makes the site into a Packagist repository. You can upload plugin zip files for any private or premium plugins for example that do not support direct installation via composer.
A shared login can be found in the engineering vault in 1Password, search for "Packagist" and use the `humanmade-pro` account.
### Uploading plugins
* Go to the Add New Plugin page at
* Click "Upload Plugin" next to the page heading
* Upload the plugin zip file
### Configure SatisPress
* With the plugin uploaded go to
* Click "Manage Packages" and you will see a list of all the plugins uploaded to the site, check the box or boxes for the plugins you need to have available
* Once a plugin is managed by SatisPress, uploading a new zip will add that version to the list of available versions for that plugin
### Configure Composer
To make use of packagist.hmn.md you need to do 2 things:
In `composer.json` add:
```
{
	"repositories": {
		"humanmade-pro": {
			"type": "composer",
			"url": "https://packagist.hmn.md/satispress/"
		}
	}
}
```
Create `auth.json`, or add to it:
```
{
	"http-basic": {
		"packagist.hmn.md": {
			"username": See 1Password,
			"password": See 1Password
		}
	}
}
```
Make sure to merge the JSON into any existing properties like `repositories` or `http-basic`.
### Installing from packagist.hmn.md
Now all you need to is require packages using `humanmade-pro` as the prefix:
`composer require humanmade-pro/multilingualpress`