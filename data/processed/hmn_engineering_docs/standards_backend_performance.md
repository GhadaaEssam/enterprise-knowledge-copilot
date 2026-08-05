# Performance
Performance is very important with the scale of the sites we work on. If it's not performant, it cannot ship. However, it's important to be pragmatic; performance is a rabbit hole that you can spend infinite time on. Shipping mostly-performant code is better than not shipping, and you can always incrementally improve it later.
Determining what is or isn't performant is tough, and this role mostly falls on the code author. However, performance should also be checked during review, especially for external plugins that may not have been created with performance in mind.
## Cache Queries and Requests
Data should almost always be cached when it's being loaded from an external source, whether that's the database or an external HTTP request. Use either the existing caches in WordPress, or add your own caching code. This has two main effects: it is almost always faster to load data from the cache, and it also reduces variability.
Reducing variability is useful as it ensures the site has predictable performance. For example, hitting an external API on every page load could cause performance problems on the external API's side to also impact our site (it would probably be very slow anyway). Instead, we can cache this data and periodically update the cache (e.g. in a cron job).
At the scale of the sites we're working on, it's often useful to cache *every* post query, particularly those used in utility functions. WordPress doesn't cache these out of the box as the cache hit rate would be very low, but when we can predict that a query will happen repeatedly, we can cache it at a higher level. (Plugins are available that will handle this for you automatically, including the [Advanced Post Cache](https://href.li/?https://github.com/Automattic/advanced-post-cache) plugin which is included on VIP sites.)
Where possible, use cached functions in WordPress, as these have already handled the caching for you. This includes most high-level functions around data, including `get_post()`, `get_post_meta()`, `get_option()`, and many more. If in doubt, check the WordPress source for `wp_cache_get()` calls, or ask a friendly colleague.
## Unbounded Queries
It's super easy to kill a large site by forgetting to put a limit on your query. Queries should always have an upper bound to ensure you don't try and load 400,000 posts into memory. This can be tough to spot locally with only a few test posts, so it's important to be careful about checking every query.
When writing database queries or post queries, always include an upper limit. If you need to get every item, reconsider the need to do so first, and whether you can change the process altogether. Unbounded queries are fine when you're only working with a few items in the database, but present problems as the site scales. (They can be difficult to debug as well, as the site may just go down for no reason in the middle of the night; just ask Ryan about downtime during the retreat.)
If you can do so, rethink the way you're storing or presenting data in the first place. You may be able to present pagination to the user instead, or use an infinite scroll technique to load items in batches instead.
The typical unbounded query in WordPress is using `WP_Query` with `'posts_per_page' => -1`. **Do not do this.** Likewise, raw database queries without a `LIMIT` clause should not be used.
If you really do need to touch every post in the database, consider whether you can move your code into an offline solution; that is, into a wp-cli command or a cron task. This ensures that end users are shielded from potential scaling issues, and makes the operation fail-safe.
Here is an example of querying all posts with bounded queries:
```
 'post',
    'post_status' => 'publish',
    'posts_per_page' => 100,
    'paged' => 1,
    'orderby' => 'ID', 
];

do {
    $query = new WP_Query( $args );
    foreach ( $query->posts as $post ) {
        the_ID();
    }
    $args['paged']++;
} while ( $args['paged'] max_num_pages );
```
While this will still retrieve every item from the database, paginating through results reduces load on MySQL as well as data passed over the wire. This should still generally be avoided or offloaded where possible.
## Avoid Writes on Page Views
You should avoid writing to the database on page views. Writing anything simply when a page is loaded is a surefire way to kill the database. This applies on any page view, including regular frontend pages and dashboard pages. You should only write to the database after a form submission (or Ajax `PUT` or `POST` request). (Note that this also applies to the filesystem, but you shouldn't write to the filesystem anyway.)
Writes to the database can cause row or table locking, in addition to invalidating the various caches throughout WordPress and the database. Additionally, it means that pages cannot be cached properly.
If you need to track page views or similar, consider a dedicated service, including external services like Google Analytics. You're often better off using these and pulling data back to the site via their API. (This is how [hm-top-posts](https://href.li/?https://github.com/humanmade/hm-top-posts) works, for example.) WordPress is built for a read-heavy workload, whereas analytics are a write-heavy workload, so a dedicated service built for analytics is usually a better option.
In some places, you may not be able to avoid writing to the database. In these very rare cases, you should ensure you're writing as little as possible; for example, only updating the user's status if it really needs to be updated.
## Unperformant Functions
The following functions are uncached and should mostly be avoided in favour of alternatives, unless you write your own caching code around them:
* `get_posts()` (VIP only) - This disables all filters which are used for query caching, use `WP_Query` instead or set `'suppress_filters' => false` manually.
* `get_children()` - This is uncached like `get_posts()`, but with an unbounded query, so should always be avoided.