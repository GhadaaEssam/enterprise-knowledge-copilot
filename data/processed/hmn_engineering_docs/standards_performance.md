# Performance
Performance is something that needs to be considered early in the architecture and design of features, rather than corrected for at the end. When we talk about performance at this level, we're talking about the *performance characteristics* of the process or algorithm (this is also called the *characteristic performance*).
When discussing performance characteristics, it's common to talk about "algorithms". This doesn't mean a formal mathematical process, but rather discussing the abstract process rather than the specific steps. For example, the algorithm for calculating the number of posts for an author could be:
* Set the counter to zero
* Fetch all posts
* For every post:
+ If the post is not by the author, skip it
+ Add one to the counter
It might be helpful to think of an algorithm as a single function.
When thinking about a specific problem, you should carefully consider the performance characteristics of the problem. For example, a process that needs to load in every item from a database table is always going to scale with the number of items. Often, you may be able to rethink a problem to reduce this down to reading only a single item instead through careful design.
Typically, you can reduce an algorithm to one of a set of standard behaviours: constant, linear, quadratic, or exponential (with a few more complex ones). These describe how the algorithm responds to the size of an input array.
Specifically, these describe how the **complexity** of the algorithm increases, not the time (although they tend to be the same). An "expensive" quadratic loop (high complexity) might actually be really fast if you only have a few items. In general, aim for the lowest complexity that produces relatively clean code, and only worry about trying to reduce it in application bottlenecks.
These behaviours are often denoted using [Big-O notation](https://href.li/?https://justin.abrah.ms/computer-science/big-o-notation-explained.html), which is just a convenient shorthand. Don't worry too much about the specifics of the notation. However, note that when using this, you drop all but the dominating term: a function which has both linear behaviour and quadratic behaviour only denotes the quadratic behaviour, as it tends to be much more important as the size of the array increases.
## Constant-time Behaviour
This is an algorithm that always takes the same time, regardless of the input. For example, a function that always returns `42` would respond in constant-time.
Constant-time behaviour is denoted in Big-O as `O(1)`.
The following are examples of constant-time functions:
```
// This function doesn't take input and always returns the same things.
function get_url() {
    return 'http://example.com/';
}

// This function only takes one item, and reads the data directly.
function get_type( WP_Post $post ) {
    return $post->post_type;
}

// The following are also constant-time in PHP due to how PHP stores data.
count( $array );
strlen( $string );
isset( $array[ $key ] ); // Technically O(n), but ~O(1) for post_type;
    }, $posts );
}

// This function checks for duplicates in an array.
function has_duplicates( $items ) {
    foreach ( $items as $first ) {
        foreach ( $items as $second ) {
            if ( $first === $second ) {
                return true;
            }
        }
    }

    return false;
}

// The following are also linear-time in PHP.
in_array( $needle, $haystack );
array_shift( $array );
array_keys( $array );
array_values( $array );
array_filter( $array );
```
## Quadratic Behaviour
An algorithm that scales quadratically with the size of the input; that is, it doubles in complexity for each new element. For example, a function that loops over a list of items, and for each item, loops again over the items.
Quadratic behaviour is denoted in Big-O as `O(n^2)`.
Nested loops on the same list of items are a cause of quadratic behaviour. These can be easy to identify (a `foreach` inside a `foreach` on the same items) in some cases, but often are difficult to spot due to the application's complexity. These can easily manifest with loops over PHP globals, such as the WordPress query.
SQL queries with subqueries or joins can cause quadratic behaviour, which is why you should often avoid them, and be very careful when you are using them.
Generally, try and reduce quadratic behaviour to linear behaviour where you can. Quadratic behaviour tends to be slow unless your array is small (under 100 items).
The following are examples of quadratic-time functions:
```
// This function takes a list of items and loops it for each item.
function count_children( array $posts ) {
    $children = [];
    foreach ( $posts as $post ) {
        $children[ $post->ID ] = 0;

        foreach ( $posts as $children ) {
            if ( $post->ID === $children ) {
                $children[ $post->ID ]++;
            }
        }
    }
    return $children;
}
```
## Exponential Behaviour
An algorithm that dramatically increases with the size of the input. For example, a function that recurses over items, where the level of recursion is linked to the size of the list of items.
Exponential behaviour is denoted in Big-O as `O(2^n)`.
Typically, exponential behaviour is rare in the sort of code we write, but can occur when using recursion. Exponential behaviour should be reduced where possible, as it's almost always slow, even with small arrays.
The following are examples of exponential-time functions:
```
// This function calculates the Fibonacci number by calculating all
// previous numbers.
//
// For example, calculating `fibonacci( 7 )` requires calculating
// `fibonacci( 5 )` and `fibonacci( 6 )`, which itself requires calculating
// `fibonacci( 5 )`.
function fibonacci( $n ) {
    if ( n  $item ) {
        if ( $item === $value ) {
            $result = $index;
        }
    }
    return $result;
}

// This function does the same thing, but improves the best and average cases:
function search( array $items, $value ) {
    foreach ( $items as $index => $item ) {
        if ( $item === $value ) {
            return $index;
        }
    }
    return null;
}
```
### Cache Expensive Operations
If an operation is inherently complex or slow, you can cache the result. This reduces the operation in all but the worst-case to a cache lookup, which is a constant-time operation.
This is usually a sensible solution if the result doesn't change often (for example, child post counts only change if a post is updated). If the result changes often, you may need to come up with a different solution, as the cache hit rate may not be great.