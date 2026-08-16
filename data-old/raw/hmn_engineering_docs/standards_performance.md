# Source: https://engineering.hmn.md/standards/performance/

# Performance

Performance is something that needs to be considered early in the architecture and design of features, rather than corrected for at the end. When we talk about performance at this level, we’re talking about the *performance characteristics* of the process or algorithm (this is also called the *characteristic performance*).

When discussing performance characteristics, it’s common to talk about “algorithms”. This doesn’t mean a formal mathematical process, but rather discussing the abstract process rather than the specific steps. For example, the algorithm for calculating the number of posts for an author could be:

* Set the counter to zero
* Fetch all posts
* For every post:
  + If the post is not by the author, skip it
  + Add one to the counter

It might be helpful to think of an algorithm as a single function.

When thinking about a specific problem, you should carefully consider the performance characteristics of the problem. For example, a process that needs to load in every item from a database table is always going to scale with the number of items. Often, you may be able to rethink a problem to reduce this down to reading only a single item instead through careful design.

Typically, you can reduce an algorithm to one of a set of standard behaviours: constant, linear, quadratic, or exponential (with a few more complex ones). These describe how the algorithm responds to the size of an input array.

Specifically, these describe how the **complexity** of the algorithm increases, not the time (although they tend to be the same). An “expensive” quadratic loop (high complexity) might actually be really fast if you only have a few items. In general, aim for the lowest complexity that produces relatively clean code, and only worry about trying to reduce it in application bottlenecks.

These behaviours are often denoted using [Big-O notation](https://href.li/?https://justin.abrah.ms/computer-science/big-o-notation-explained.html), which is just a convenient shorthand. Don’t worry too much about the specifics of the notation. However, note that when using this, you drop all but the dominating term: a function which has both linear behaviour and quadratic behaviour only denotes the quadratic behaviour, as it tends to be much more important as the size of the array increases.

## Constant-time Behaviour [#](#constant-time-behaviour)

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
isset( $array[ $key ] ); // Technically O(n), but ~O(1) for <1 million items
array_pop( $array );
```

## Linear Behaviour [#](#linear-behaviour)

An algorithm that scales proportionally with the size of the input. If an algorithm takes one second for each item in the input, it responds linearly. For example, a function that adds `1` to every item of the input would respond in linear time.

Linear behaviour is denoted in Big-O as `O(n)`.

Typically, you can spot linear behaviour by `foreach` loops and related behaviour (such as `array_map`). In SQL queries, most simple `SELECT` queries are linear (e.g. `WHERE post_type = post`), but your table structure can help reduce these (for example, adding an index to a field you’re querying by can reduce it from linear to logarithmic behaviour).

The following are examples of linear-time functions:

```
// This function takes a list of items and applies a simple operation.
function add_one( array $items ) {
    foreach ( $items as &$item ) {
        $item = $item + 1;
    }
    return $items;
}

// This function maps a function onto an array.
function get_types( $posts ) {
    return array_map( function ( $post ) {
        return $post->post_type;
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

## Quadratic Behaviour [#](#quadratic-behaviour)

An algorithm that scales quadratically with the size of the input; that is, it doubles in complexity for each new element. For example, a function that loops over a list of items, and for each item, loops again over the items.

Quadratic behaviour is denoted in Big-O as `O(n^2)`.

Nested loops on the same list of items are a cause of quadratic behaviour. These can be easy to identify (a `foreach` inside a `foreach` on the same items) in some cases, but often are difficult to spot due to the application’s complexity. These can easily manifest with loops over PHP globals, such as the WordPress query.

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

## Exponential Behaviour [#](#exponential-behaviour)

An algorithm that dramatically increases with the size of the input. For example, a function that recurses over items, where the level of recursion is linked to the size of the list of items.

Exponential behaviour is denoted in Big-O as `O(2^n)`.

Typically, exponential behaviour is rare in the sort of code we write, but can occur when using recursion. Exponential behaviour should be reduced where possible, as it’s almost always slow, even with small arrays.

The following are examples of exponential-time functions:

```
// This function calculates the Fibonacci number by calculating all
// previous numbers.
//
// For example, calculating `fibonacci( 7 )` requires calculating
// `fibonacci( 5 )` and `fibonacci( 6 )`, which itself requires calculating
// `fibonacci( 5 )`.
function fibonacci( $n ) {
    if ( n <= 1 ) {
        return n;
    }

    return fibonacci( $n - 1 ) + fibonacci( $n - 2 );
}
```

## Other Behaviours [#](#other-behaviours)

There are [a lot of other named complexities](https://href.li/?https://en.wikipedia.org/wiki/Time_complexity#Table_of_common_time_complexities), but most of these aren’t useful to refer to in practice.

Logarithmic time (`O(log n)`) is likely the only other behaviour you’ll commonly hear. This is similar to linear time, but eliminates some complexity by reducing the number of things it needs to touch.

Sorting in PHP with `sort()` has `O(n log n)` behaviour (quasilinear), as it uses the [quicksort algorithm](https://href.li/?https://en.wikipedia.org/wiki/Quicksort).

## Reducing Complexity [#](#reducing-complexity)

Typically, don’t worry too much about reducing complexity unless you’re working with large arrays (more than 100 items). Try and write your code as efficiently as possible, but don’t spend time refactoring just for something theoretically better.

For example, `isset()` is constant-time, while `in_array()` is linear-time, but this difference is unlikely to matter for arrays smaller than 10,000 items. Micro-optimisations like this should be tested, and only implemented if they make a significant difference over a more readable variant.

### Time-Memory Trade-Off [#](#time-memory-trade-off)

Sometimes, you can improve the complexity by storing information; this is called a **time-memory trade-off**, since we’re gaining speed by storing more information. For example, we can improve the duplicate checking code from quadratic-time to linear-time by looping only once but storing what we see:

```
// This implementation has O(n^2) behaviour.
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

// By storing what we've seen and using isset (which is O(1)) we instead have
// an O(n) algorithm.
// (This is essentially a hash table.)
function has_duplicates( $items ) {
    $seen = [];
    foreach ( $items as $item ) {
        // isset() is a constant-time operation.
        if ( isset( $seen[ $item ] ) ) {
            return true;
        }

        $seen[ $item ] = true;
    }

    return false;
}
```

### Improving the Average Case [#](#improving-the-average-case)

Some parts of your code that get called often may need time spent reducing the complexity as part of performance optimisations. These bottlenecks can occur in pieces of code that are called thousands of times in a request, such as filters on `translate` or functions that run on `init`.

Usually, you can get the best performance benefits by improving the **average case** rather than the **worst case**. For example, when you have are searching for an item, you can often improve the average case by stopping as soon as you find it, rather than continuing across all items:

```
// This function searches for an item, but has linear behaviour as it does not
// stop immediately:
function search( array $items, $value ) {
    $result = null;
    foreach ( $items as $index => $item ) {
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

### Cache Expensive Operations [#](#cache-expensive-operations)

If an operation is inherently complex or slow, you can cache the result. This reduces the operation in all but the worst-case to a cache lookup, which is a constant-time operation.

This is usually a sensible solution if the result doesn’t change often (for example, child post counts only change if a post is updated). If the result changes often, you may need to come up with a different solution, as the cache hit rate may not be great.

Accessed Tue, 28 Aug 2018 07:22:01 +0000 from `https://engineering.hmn.md/standards/performance/`

[Made by Humans](https://hmn.md)