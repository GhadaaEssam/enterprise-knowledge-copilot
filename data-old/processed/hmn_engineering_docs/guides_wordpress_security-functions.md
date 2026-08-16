# Security Functions
This guide documents the functions available in WordPress and PHP for sanitisation, validation, and escaping, along with best practices for other functions.
## WordPress Sanitisation Functions
WordPress provides a number of functions that can be used to sanitise data before further processing, and to make data safe to be inserted into the database.
### sanitize\_text\_field()
The main usage of [`sanitize_text_field()`](https://href.li/?https://developer.wordpress.org/reference/functions/sanitize_text_field/) function is to sanitise the data provided by text input fields in forms. But it's useful for sanitising any kind of data that you want to be plain text.
`sanitize_text_field()` applies the following modifications to the data:
* Removes all HTML tags.
* Removes whitespace from the start and end of the string.
* Removes extra whitespace (more than a single space) between words.
* Removes tabs and line breaks.
* Converts stand-alone `` tags. It has no security implications on the JavaScript side, meaning that the data still needs to be escaped on output (when added to the DOM) in JavaScript.
## Correct Function Usage
### in\_array()
Always set the [`in_array()`](https://href.li/?https://www.php.net/manual/en/function.in-array.php) $strict argument to `true`, to enable strict comparison. Loose type comparison can lead to unexpected results.