# Security
## XSS (Cross-Site Scripting)
XSS is a type of attack where an attacker is allowed to insert malicious JavaScript into a page and run that script for the end user. XSS attacks most often come from un-escaped user input or bad-actors that have been allowed more access than they should or have found a hole where data is being passed through without being sanitized or escaped.
XSS is relatively simple to address and fix, yet it is still 2nd in the OWASP Top Ten risks due to its prevalence.
**Simple steps to avoid XSS:**
* Escape all output, no matter how benign
* Sanitize all user input, especially from all frontend forms and REQUEST variables
* Use a Content Security Policy to prevent any extraneous script tags from running
## CORS (Cross-Origin Requests)
A Cross-Origin Request allows a user on one site to request a resource from another. In many instances these may be harmless, for example an image. These become security problem when the request takes advantage of or manipulates HTTP headers to request a protected resource.
Setting [Access-Control headers](https://href.li/?https://fetch.spec.whatwg.org/#http-cors-protocol) can be used to allow and disallow cross-origin requests.
Nonces can be used to indicate the request is coming from the expected origin but must not be used for authentication. WordPress nonces are valid for multiple users over 24 hours, for true nonces (a number used once) a plugin is required to augment the WordPress system.
## CSP (Content Security Policy)
Content Security Policies allow us to write instructions to the browser, telling it how we want it to behave in certain situations. They are generally sent as a header.
Almost every site that we build has use for a Content Security Policy. This use could range from a very simple `upgrade-insecure-requests` all the way to controlling where every script tag and form input on each page are allowed to originate from.
What form and how strict the policies should be will vary by client and application, but every site we build should have some form of CSP. CSPs should be tested thoroughly against the application as they can also break significant portions of a site if not carefully implemented.
**The generally most useful directives are:**
* `form-action`
* `upgrade-insecure-requests`
* `script-src`, `style-src` (note, use these with caution! This will typically break all inlined scripts that you have not created or passed a nonce to. This is intentional, but could easily break significant portions of your site)
* `frame-src` (can be used with Protected Embeds to prevent unwanted iframes.)
To prevent a site breaking completely when adding CSPs for the first time, you can send the header as `Content-Security-Policy-Report-Only` instead of `Content-Security-Policy`. This will allow you to see all violations in the console as you browse the site and fix them before completely blocking resources.
To set CSPs (either live or Report-Only), you can leverage [Altis' browser-security module](https://href.li/?https://github.com/humanmade/altis-browser-security) and the [`CSP setting`](https://href.li/?https://github.com/humanmade/altis-browser-security#content-security-policy).
You can learn more about the various types of headers at https://content-security-policy.com/ and https://scotthelme.co.uk/content-security-policy-an-introduction/. You can test a site's security headers by visiting: https://securityheaders.io/
## SRI (Sub-Resource Integrity)
When including external stylesheets or JS libraries, there is a risk of that original file being modified with malicious code. Often, we can locally host that file in the project instead, eliminating this possibility, but that is not always an option.
When you must load scripts and styles from an external location, Sub-Resource Integrity (SRI) should be used. SRI creates a hash that the browser can use to validate that the resource received is the exact resource requested. If the resource received has been modified from what the requested resource should be, the browser will simply reject it by comparing SHA hashes, preventing a XSS vector.
For example, a normal request to include jQuery could look like this:
```

```
Whereas a request with SRI looks like this:
```

```
Certain CDN providers will provide you with an SRI-included link tag, but if there is no pre-built hash for the resource, you can use https://report-uri.com/home/sri\_hash to generate one for you. It's important to note that this will only work with properly versioned assets. If an asset's content changes, but its hash is not updated, the asset will not get loaded and could break functionality.
WordPress does not currently have in-built support to easily add SRI attributes to scripts to styles (coming in [Trac #33948](https://href.li/?https://core.trac.wordpress.org/ticket/33948)). Until this is added in core, you can leverage [Altis' browser-security module](https://href.li/?https://github.com/humanmade/altis-browser-security), even if using a third-party hosting provider. This module will automatically generate hashes for all locally-hosted files and you can manually add hashes for externally-hosted asset using the below code.
```
// Setting hashes for scripts.
use Altis\Security\Browser;
wp_enqueue_script( 'my-handle', 'https://...' );
Browser\set_hash_for_script( 'my-handle', 'sha384-...' );

// Setting hashes for styles.
use Altis\Security\Browser;
wp_enqueue_style( 'my-handle', 'https://...' );
Browser\set_hash_for_style( 'my-handle', 'sha384-...' );
```
## HTTPS (HTTP Strict Transport Security)
HTTP Strict Transport Security instructs the browser to only ever load your site with a valid TLS certificate, and to re-route any requests over HTTP to HTTPS instead. This directive can enforce the usage of HTTPS as default and prevent a (albeit small) vector of attack via MiTM.
**The HTTP header looks like this:**
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```
`max-age` is the maximum amount of time that a user's browser is allowed to respect this directive, and `includeSubDomains` tells the browser to use this for sub-domains as well as the main domain. `includeSubDomains` is optional.