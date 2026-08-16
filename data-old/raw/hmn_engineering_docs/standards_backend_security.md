# Source: https://engineering.hmn.md/standards/backend/security/

# Security

Security is one of the biggest factors involved in any review. All code that we push into a production or staging environment must be completely secure.

There are a huge number of factors that must be considered with security, but they mostly boil down into a few key things:

* **Never trust user input**

  User input can never be trusted, regardless of the source. “User input” actually means anything that’s not written into the code itself, and includes things like external HTTP request data and translations.
* **Sanitise on input, escape on output**

  Your database should always store a safe value, so all data coming into the database needs to be sanitised before saving. This could mean ensuring a value is a number, or that it only contains valid HTML. Sites also tend to be write-once, read-many, so moving the expensive sanitise step to when you write it can have better performance.

  This data also needs to be escaped for the relevant context on output. If you’re echoing into a HTML attribute, the code needs to be escaped for the attribute context; the same applies for text output into a HTML context. Escaping is always context-specific, so must be done at the last possible step, ideally immediately before output.
* **Check user authorisation and intent**

  The capabilities required to perform a task should always be well-defined, and should be checked as early as possible. In addition, always check the user’s intent: did the user themselves trigger this action?

  The key tools in WordPress to achieve this are the roles and capabilities system, and the nonce system.

## Sanitisation [#](#sanitisation)

Validation and sanitisation are two separate but related concepts.

When validating data, you are looking for certain criteria in the data. Or simply put, you’re saying “I want the data to have this, this, and this”. Sanitisation on the other hand is about removing all the harmful elements from the data. In essence you’re saying “I don’t want the data to have this, this, and this”.

But the difference is more than just conceptual. With validation, we store the data once we have verified it’s valid. If not, we discard it.

With sanitisation, we take the data, and remove everything we don’t want. This means that we might change the data during the sanitisation process. So in the case of user input, it is not guaranteed that all the input is kept. So it’s important that you choose the right sanitisation functions, to keep the data intact.

Refer to the [Sanitisation section of the Security Functions guide](/guides/wordpress/security-functions/#sanitisation) for specific sanitisation functions.

## Validation [#](#validation)

Validation is a technique to ensure that input is secure before using it in your code.

When validating data, you are verifying that it corresponds to what the program needs. This only works if you have a list of criteria that you can check to determine that the data is valid.

### Safelisting [#](#safelisting)

The simplest validation method is safelisting. This only works when there is a precise set of possible values that the data can have. These are also sometimes called [enumerated types or enums](https://href.li/?https://en.wikipedia.org/wiki/Enumerated_type).

Let’s look at how safelisting can be used for validating a theme option controlling the position of the sidebar.

Here is the code that we used to create the setting and the control:

```
$wp_customize->add_setting( 'sidebar-position', [
    'default'           => 'left',
    'sanitize_callback' => 'hm_validate_sidebar_position',
] );

$wp_customize->add_control( 'sidebar-position-control', [
    'label'    => esc_html__( 'Sidebar Position', 'hm' ),
    'section'  => 'theme',
    'settings' => 'sidebar-position',
    'type'     => 'radio',
    'choices'  => [
        'left' => esc_html__( 'Left', 'hm' ),
        'right' => esc_html__( 'Right', 'hm' ),
    ],
] );
```

The user only has two choices: left or right. This means that in the `hm_validate_sidebar_position()` function, we can determine whether the submitted option is one of the two possible values.

```
function hm_validate_sidebar_position( $sidebar_position ) {
    if ( in_array( $sidebar_position, [ 'left', 'right' ], true ) ) {
        return $sidebar_position;
    }
}
```

To do this, we use the `in_array()` PHP function. This function returns `true` when the needle, the submitted value for the position of the sidebar, is in the haystack, the list of possible positions.

So safelisting simply means that we compare the submitted data against a list of acceptable values. This works well for controls such as checkboxes, radio buttons, selects, and dropdowns.

### Qualifying data [#](#qualifying-data)

When qualifying data, we try to find out whether it meets a precise set of criteria. Let’s look at an example of validating data.

Imagine that you have a meta box that allows users to pick a colour for the website’s background. The colour will be stored as a hexadecimal colour code. A value needs to fulfill a precise set of criteria in order to be a valid hexadecimal colour code. These criteria can be expressed as a regular expression, as can be seen in the following test function:

```
preg_match( '|^#([A-Fa-f0-9]{3}){1,2}$|', $color )
```

Another example is a meta field which allows users to enter a value for the width (in pixels) of the content area of a particular post. In this case, there might be sensible minimum and maximum dimension values allowed, and a default defined for unspecified values. While not being a super useful feature in a theme, this example allows us to demonstrate the use of `filter_input()`.

The `filter_input()` PHP function gets a variable and validates it. The function accepts four arguments: the type of input, the name of the variable to get, the filter (validation) to apply, and an optional array of options.

```
$content_area_width = filter_input(
    INPUT_POST,
    'content_area_width',
    FILTER_VALIDATE_INT,
    [
        'options' => [
            'default' => 500,
            'min_range' => 100,
            'max_range' => 1000,
        ],
    ]
);
```

Although the code for this function might seem verbose, it’s much shorter and clearer than writing it all out:

```
// Warning: This code does not work correctly.
if ( isset( $_GET['content_area_width'] ) && is_int( $_GET['content_area_width'] ) && $_GET['content_area_width'] >= 100 && $_GET['content_area_width'] <= 1000 ) {
    $content_area_width = $_GET['content_area_width'];
} else {
    $content_area_width = 500;
}
```

You might wonder why there is a warning about this code not working. Seems to look good, right? The problem is that `is_int( $_GET['content_area_width'] )` will always return false, so this code will always return 500.

This is because data retrieved from the `$_GET` and `$_POST` super globals is always of the type string. Using the `filter_input()` function allows us to get around this limitation of the PHP language.

### Choosing the right qualifications [#](#choosing-the-right-qualifications)

When validating data, it’s crucial that you choose the right set of qualifications, and express this correctly in the code.

Imagine that you have a Customizer setting in your theme for entering a link to a Twitter profile. You want to have a valid URL for this setting, so you use the `filter_var()` PHP function with the `FILTER_VALIDATE_URL` filter.

```
// Warning: Insecure code!
function hm_validate_twitter_profile_url( $url ) {
    return filter_var( $url, FILTER_VALIDATE_URL ) );
}
```

The next thing you do is output the validated URL in your theme:

```
// Warning: Insecure code!
echo '<a href="' . $twitter_url . '">' . esc_html__( 'Twitter', 'hm' ) . '</a>';
```

In the four lines of code that we have seen so far, we have made two crucial mistakes:

1. We trusted the filter\_var() function to validate the URL to the Twitter profile.
2. We didn’t escape the URL on output.

We are going to look at escaping in a later part of this series. For now let’s look at why the validation was too weak to be secure.

The problem is that if you enter `javascript://test%0Aalert(321)`, this is a valid URL. As soon as a user would click on the Twitter link on the front end of the site, a Javascript dialog would appear.

We need to add additional checks to our function:

```
function hm_validate_twitter_profile_url( $url ) {
    if ( 0 !== strpos( $url, 'https://twitter.com/' ) ) {
        return;
    }

    return filter_var( $url, FILTER_VALIDATE_URL, FILTER_FLAG_PATH_REQUIRED ) );
}
```

This function now verifies that the data meets three qualifications:

1. The URL starts with `https://twitter.com/`
2. The URL is valid according to the [RFC 2396 standard](https://href.li/?http://www.faqs.org/rfcs/rfc2396.html)
3. The URL has a path component (as in `http://example.org/path`)

Refer to the [Validation section of the Security Functions guide](/guides/wordpress/security-functions/#validation) for specific validation functions.

## Escaping [#](#escaping)

Escaping is used to ensure that data is safe to be output to the browser. WordPress offers a number of escaping functions. The type of escaping function to use depends on the context in which the data is output.

This is because data might be safe or unsafe depending on where it is output. Data that is perfectly safe to output between two HTML tags might not be safe to output inside of a piece of inline JavaScript.

When writing code, always escape immediately before output. This is referred to as **late escaping**. This makes it clear when and how data is escaped, making the code easy to review and to understand.

It also avoids introducing security issues by accident. If the contents of a variable are escaped first, and then later in the code output, then this code is secure. However if at a later time, then escaping is removed from the variable, then all the instances in which the variable is output are now vulnerable.

### Escaping Translations [#](#escaping-translations)

Translations are to be treated as insecure data, and therefore need to be escaped before output.

WordPress offers a number of helper functions for this:

* `esc_html__()`: Wrapper for `esc_html( __() )`
* `esc_html_e()`: Wrapper for `echo esc_html( __() )`
* `esc_html_x()`: Wrapper for `echo esc_html( _x() )`
* `esc_attr__()`: Wrapper for `esc_attr( __() )`
* `esc_attr_e()`: Wrapper for `echo esc_attr( __() )`
* `esc_attr_x()`: Wrapper for `echo esc_attr( _x() )`

A common scenario is dealing with translations that do contain HTML. Escaping is trickier, because WordPress does not include an easy to use helper function for this.

If possible, extract all HTML from translated strings:

```
printf(
    esc_html__( 'Fixed in version %s', 'hm' ),
   '<strong>' . esc_html( $version ) . '</strong>'
);
```

In this snippet, the translated string can be HTML-escaped. `sprintf()` then inserts an escaped variable wrapped in HTML tags.

If this approach is not possible, `wp_kses()` can be used:

```
echo wp_kses(
   esc_html__( 'Fixed in version <strong>4.5</strong>', 'hm' ),
   [ 'strong' => [] ]
);
```

When dealing with multiple HTML tags, or HTML tags that accept attributes, the code needed to make wp\_kses() work can become quite verbose. We therefore recommend the use of [Clean HTML](https://href.li/?https://github.com/humanmade/clean-html) library.

#### Translations containing URLs [#](#translations-containing-urls)

When it comes to URL in translations, we can be dealing with two different cases:

1. The URL does not need to be adapted per language. In this case remove the URL from the translated string, and replace it with a placeholder.
2. The URL needs to be translatable: Remove the URL from the translated string, and make it translatable separately. Make sure to wrap the translation function used for the URL in an `esc_url()` call.

Accessed Mon, 26 Feb 2018 10:02:33 +0000 from `https://engineering.hmn.md/standards/backend/security/`

[Made by Humans](https://hmn.md)