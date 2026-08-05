# Architecture
The capabilities of the infrastructure on which the project will be hosted on. These capabilities have a direct impact on the possible solutions to architectural challenges.
### Page Caching
Page caching solutions vary from application layer implementations like Batcache to infrastructure layer solutions like Varnish.
It is important to know what requests get cached, for how long, what the cache clearing logic is, and if and how the cache clearing can be customised.
### Job Scheduling System
An asynchronous job handler is a requirement for every application. The least reliable solution is WP Cron, so often Linux crons can be used. Certain hosts offer a separate job infrastructure that is independent of web requests, which is the ideal scenario.
The critical point here is the reliability of the job scheduling system. The better the system, the more the architecture can rely on it.
### Logging
Logs are required to have an insight into the workings of the application. In an ideal scenario, the hosting platform offers insight into the PHP logs, and offers an API to log custom events.
If custom logs aren't supported, your architecture will need to account for this by implementing this on the application layer.
### Platform Code
Certain hosts require the use of specific WordPress plugins, and have an assortment of recommended plugins.
This should be considered when designing features, as hosts are required to provide support for their code.
## Sites and Networks
WordPress can be can be deployed as a single site install, or as a multisite network. In addition, a network of multisite networks can be created using a third-party plugin.
Compared to a collection of single sites, a multisite network has a number of advantages.
The first is code sharing. MU plugins get loaded for all sites on a network, whereas plugins can be activated on a per site basis, as can themes.
Multisites add a new access level for super admins, that can manage all sites in the network from a centralised place. In larger organisations like for a example a publishing company with multiple brands, this allows maintainers of individual sites lots of freedom, while keeping centralised control over what plugins and themes these sites can run.
The user and user meta tables are also shared between all sites of the network. This allows admins to easily manage access to different sites for users, without needing to create accounts for them for each single site. Users can then login once, and from there access the admin areas of all the sites to which they belong.
A multisite network can also be configured to allow users to create their own sites on the network. An example use case might be an intranet for a school, in which teachers and students can create their own sites on the network.
From a code perspective, WordPress allows to switch the context from one site to another. This gives access to the global database object, which makes it easy to transfer data between sites on the network.
## External Services
The next step is to look at the external services with which the website will interact.
We can distinguish between two types of integrations, client side integrations and server side integrations.
### Client Side Integrations
The first type are integrations are client side only. This means that they impact the front end, without any impact on the infrastructure. A common example would be Google Analytics, or integrating a third party commenting system.
As the application does not have direct access to these external services, there are limitations on how the PHP layer and often also the front end can interact with them. As an example if related articles are being pulled in from an external service using a JavaScript snippet injecting content directly into the DOM, then there's no way to implement a fallback on the PHP layer if the external service does not respond.
Integrations that are client side only do not impact the PHP-generated page delivery performance of the application. However if the rendering of the front end is impacted, then this needs to be taken into account. A placeholder or a loading indicator could be displayed while the interaction with the external services is being done.
### Server Side Integrations
On the server side, we can distinguish between event driven integrations, and time driven integrations.
**Time driven integrations** consist of the application interacting with an external service in fixed intervals. To be reliable, this type integration needs to be powered by a reliable time-based job scheduler. In addition if the interaction is resource intensive, then it needs to be decoupled from the page generation process.
An example of such an integration would be importing content from an RSS feed. The feed might be retrieved every 15 minutes via a cron job, and new content would be inserted into the database.
**Event driven integrations** depend on a certain event, like a WordPress hook being fired, or a user action. Like any back end functionality, these integrations have an impact on performance. Therefore these integrations are often limited to the admin area.
If the integration only consists of notifying an external service, then the interaction could be done synchronously. An example would be notifying an external service that an article has been published.
However if data needs to be retrieved from an external service and processed, then this integration should preferably be done asynchronously, unless it depends on a user action.
An example would be importing a single video from an external service. If this is done after the user has clicked a button to do the import, then the interaction with the external service could be done synchronously, with the UI giving an indication of the progress.
If that same video import were done after the user has clicked on the Publish button, then this would slow down the post saving process too much. A failure of the external service might even break the post saving functionality.
In that scenario it would be best to schedule a cron job during the action, that handles the interaction with the external service asynchronously. Any dependencies could then be handled by scheduling other cron jobs, creating a chain of events.
As an example you could have a cron job that retrieves a shortlink from an external service when a post is published. The publicise to Twitter functionality that depends on the presence of the shortlink could then be scheduled once the shortlink has been retrieved and saved successfully.
### Third Party Data Handling
When dealing with third party APIs, the question becomes how much of the API data needs to be stored in the database of the consumer site.
If the database contents do not need to be kept in synchronisation with the API, then this is not as much of a concern.
An example would be a shortlink API: these links stay the same as long as the link of the content stays the same. Another example would be media
## Content
### Types of Content
Out of the box, WordPress only contains three types of content.
The first content type are **posts**. Posts are always items of a collection, which typically is displayed on the front end as an archive. The most common form is the date based blog home archive. Posts support tags and categories, which allows to divide the larger collection into smaller ones.
The second content type are **pages**. Pages by default exist as individual entities. They do not have archives, and they do not support any kind of taxonomies. The only way to tie pages together is by hierarchy.
The third content type are **attachments**. Attachments represent a media file in the database, and they are not meant to have a stand alone presence.
Even though WordPress supports these three different content types, under the hood all of them are stored in the same table. The differences between them are based on the features that they support, and the possible ways to retrieve them.
When architecting a site, have the arguments for `register_post_type()` in front of you, as well as the list of post type features. Consciously decide which capabilities that the different types of content need to support, and which not.
Keep in mind that once you decide to give a capability to a content type, it will apply to all entities of this type. Imagine that you have a post type and you registered archive support. It will be difficult to exclude individual posts from this archive (there are possible approaches, but they all have important drawbacks).
This is because every post type argument and feature comes with a fixed set of expectations. As an example if a post type supports authors, it will show up in author archives. While it is possible to remove individual post types from individual archives, this can be ineffective, or even impossible.
The decision on whether to use a built-in WordPress feature and customise it, or whether to write something from scratch is not always clear from the start. In such a case, it can be useful to build a quick MVP to validate or refute a possible architecture.
### Classifying Content with Taxonomies
As we have seen, posts always appear in collections. There's often the need to create sub-collections out of this main collection. This is where taxonomies come in.
### Flat vs. Hierarchical Taxonomies
Taxonomies can be divided into main types: **hierarchical** taxonomies and **flat** taxonomies. Which one to use depends a lot on the individual scenario.
Imagine that you have articles that you want to assign to national leagues and football teams. A team can only ever play in one national league. Therefore a straightforward approach might be to have a single taxonomy with parent terms representing the leagues, and child terms for the individual teams. With this approach, it would be easy to list all the teams in a particular league.
At first sight, this is a good solution. However teams do change leagues when they perform well or poorly. So each season you would have to move teams from one league to another, and in the process invalidating a bunch of URLs. So having to flat taxonomies, one for the leagues and one for the teams, would be better. Especially if you add other leagues, like international ones.
The downside is that in this scenario you cannot retrieve the teams in a league easily, because there are no object to object relationships in WordPress.
### Open, Restricted, Locked, and Hidden Taxonomies
By default, WordPress allows any user with Editors role or a higher role to create and rename terms in the default taxonomies. This is what we refer to as an **open** taxonomy.
While open taxonomies work fine for something like tags and categories, it is often a requirement to restrict the capability to create and modify terms to a specific role. The previous example of the football leagues and teams would be a good case for this.
While WordPress has built-in `manage_terms` and `edit_terms` capabilities, it does not make a distinction between the two. In this case, custom code is needed to implement this feature. We designate these taxonomies as **restricted**.
Locked taxonomies do not allow users to create or modify terms via the UI. The only available option is to assign terms to content. An example for this might be the main categories on a news website, featuring in the navigation.
You would not want to be such an essential part of the infrastructure to be editable by users. Terms in locked taxonomies should therefore be created in code, preferably during an upgrade routine that only runs once. By doing it this way, the website does not need to implement fallback code for missing terms.
**Hidden** taxonomies go one step further, by not being publicly available. The terms in these taxonomies are only used for retrieving posts. An example for this might be a taxonomy to manage the posts shown in different featured areas on a website.
### UI Considerations
By default, WordPress contains only two different meta boxes for taxonomies. The categories meta box is used for all hierarchical taxonomies, and the tags meta box for all flat taxonomies.
In most cases, these meta boxes are not optimal from a user perspective. Consider using CMB2, which offers a variety of meta boxes for managing taxonomy terms.
## Object to Object Relationships
WordPress does not support relationships between objects of the same type. An example would be linking a post to another post, or a term to another term. There are different ways to architect this, all with their own drawbacks.
### Post to Post Relationships for Non-Hierarchical Post Types
When dealing with non-hierarchical posts, the post parent field in the database can be reused for linking entities together. In this scenario, it doesn't matter whether it's a one to one or a one to many relationship.
The limitation here is that there's only one post parent field, so a post can't support multiple relationships this way. In addition the queries on the front end will need to account for this hierarchical relationship.
The *New Post* and *Edit Post* screens in the admin will handle assigning posts to a parent post automatically in the database, as long as a `parent_id` field is sent along in the `$_POST` data when the post is saved. This can be achieved by naming a specific field in your custom UI accordingly.
To retrieve posts, there's the cached `get_children()` function, as well as the `wp_get_post_parent_id()` function. Since hierarchical posts are a built-in WordPress feature, there's support for them in `WP_Query`, and retrieving posts is fast.
### One to One Relationships for Terms and Posts
Another approach is to use object meta to create relationships. This is done by storing the id of the linked entity into a meta field on the entity.
An example might be linking an related post to a video post type. In this scenario, you want the related post to pulled on single video views. You would therefore store the post id in the post meta of the video post type.
It is possible to retrieve the video post type to which a post is linked by doing a meta query. However meta queries are slow, so you would need to implement extra caching if this were used on the front end.
### One to Many Relationships for Posts
When a post needs to be able to be linked to multiple other posts, a possible approach is to use a taxonomy that shadows the post type.
This means that whenever a new post is created, a term in the shadow taxonomy is created. The term name and slug should correspond to the post title and slug, so that display elements and queries can be handled easily.
In practice this means implementing custom create, read, update, and delete functions for the terms in the shadow taxonomy that mimic these operations on posts.
This approach has the advantage that term queries are very fast, and you do not need to worry about any main queries to be impacted.
However the downside here is that posts do support features that taxonomies do not support. Posts can be hidden from the public, but be visible to logged-in users, terms cannot. In addition deleted posts are placed in the trash, whereas terms are deleted immediately.
Whatever your implementation is, it needs to account for this differences in content handling.
## Customising Built-In Archives
WordPress offers different types of built-in archives, like date and author archives, as well as two built-in taxonomies, tags and categories.
These archives are fast, because the queries behind them are all fast. Whenever these queries are customised, they become more complex, and therefore slower.
## Meta Data Handling
Posts and terms have a fixed database schema, that comes with expectations for the data stored in individual cells. As such there's quite a number of data that cannot be stored in the post and term tables.
This is where the post and term meta data APIs come in handy. These APIs give access to the meta tables, which is essentially a key/value storage. The value field is of the SQL type `LONGTEXT`, so it can store up to 4Gb of data.
The meta tables are meant to store bits of data that does not fit into any of the fields of the entity table. The functions for storing and retrieving data are easy to use, and complex queries can be run against this table.
Unfortunately the meta data APIs have a number of gotchas, which can lead to buggy, slow, and fragile implementations.
### Key Query Limitations
An object can have multiple meta entries with the same key associated to it. This can lead to difficult to detect bugs, if the meta API functions are used wrong:
* `add_*_meta()` accepts a `$unique` argument. If set to `false` (the default), a new entry with the same key will be added. If set to `true`, nothing will be saved.
* `update_*_meta()` will update all entries with the same key.
* Using `get_*_meta()` with `$single` set to `true` will retrieve the first entry under the specified key, even if more entries exist.
* If the `$key` passed to `get_*_meta()` evaluates to `false`, which can happen when an error happens during dynamic key generation, all meta data attached to the passed object id will be returned.
Features that apply heavily on post meta therefore need to be tested extensively, to avoid running into these edge cases.
### Value Query Limitations
The `meta_value` field of the meta tables is not indexed, so queries against post meta values can quickly become really slow, even on small tables.
Therefore queries against meta values should be avoided on the front end. If they cannot be avoided, then the query should be cached rather aggressively.
The reliance on post meta queries is often a result of bad architectural choices. Imagine that you have an Event post type that has a start and an end date for each event. As long as this data is only used for display purposes, storing the dates in post meta is fine.
However when you need to be able to selectively display events for specific date ranges, then post meta is no longer adequate. If there are only two zones on a site that require to run this expensive query, then aggressive caching would be a solution.
However using a different storage mechanism, like the `post_date` and `post_modified` fields of the post type would be a better solution.
### Handling of Different Data Types
Meta values are expected to be scalar values, or serialisable values. This leads to edge cases in how data is handled compared to how developers expect data to be handled.
* The only non scalar values that should be stored in post meta are arrays.
* Never stored objects in post meta. Careful when dealing with classes that implement the `ArrayAccess` interface. You are still dealing with an object, not an array.
* Depending on the value of the `$single` argument passed to `get_*_meta()`, either an empty string or an array of returned when no value exists for a specific meta key. This means that empty strings or arrays cannot reliably be stored in meta.