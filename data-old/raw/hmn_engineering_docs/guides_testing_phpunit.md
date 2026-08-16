# Source: https://engineering.hmn.md/guides/testing/phpunit/

# PHPUnit

Writing tests can be tough, especially once WordPress gets involved. Let’s do it together.

Most tests you’ll work on are written using PHPUnit, so let’s work through getting started using PHPUnit. To start with, we’re going to work with a very basic PHPUnit test which doesn’t load WordPress, and work up to testing a plugin.

You can follow along with the steps here, or clone the repository which includes the parts we’re writing here.

If you’re using Chassis for local development, you’ll want to install the [Tester extension](https://href.li/?https://github.com/Chassis/Tester). This will make PHPUnit available inside your VM, and automatically configure environment variables for WordPress testing.

If you’re **not** using Chassis, you need to make sure you have [PHPUnit](https://href.li/?https://phpunit.de/) installed and available on your path.

The first step to getting started is to write a test class. PHPUnit uses class-based tests, which load the class up, then run every method named `test_...()`. If this method runs successfully, the test passes.

Let’s start out with a completely empty test class. Create a new directory at the top-level of your plugin called `tests/`, and save the following as `tests/class-example-test.php`:

```
<?php

namespace HM\ExamplePlugin\Tests;

use HM\ExamplePlugin;
use PHPUnit_Framework_TestCase;

class Example_Test extends PHPUnit_Framework_TestCase {
    // Nothing here yet!
}
```

You can now run this test file by telling PHPUnit to run it. (If you’re using a VM, you should run this inside the VM via `vagrant ssh`.)

```
phpunit tests/class-example-test.php
```

You should see output similar to the following:

```
PHPUnit 5.7.3 by Sebastian Bergmann and contributors.

W                                                                   1 / 1 (100%)

Time: 89 ms, Memory: 8.00MB

There was 1 warning:

1) Warning
No tests found in class "HM\ExamplePlugin\Tests\Example_Test".

WARNINGS!
Tests: 1, Assertions: 0, Warnings: 1.
```

This means PHPUnit found your class, but couldn’t find any tests in it. This makes sense since we haven’t written any yet! Let’s go ahead and write one.

Tests in PHPUnit are based on assertions. With assertions, you run a piece of code, then assert the value matches what you expected. If it doesn’t match, the test fails and stops running. Tests can have multiple assertions if you have multiple values to check, but tests should remain focussed on testing one piece of functionality.

For our first test, let’s do a super simple test to check it’s working. Add the following method to your class:

```
public function test_cast_int_to_bool() {
    $should_be_true = (bool) 1;
    $this->assertTrue( $should_be_true );
}
```

Run PHPUnit against the file again, and you should see this:

```
PHPUnit 5.7.3 by Sebastian Bergmann and contributors.

.                                                                   1 / 1 (100%)

Time: 82 ms, Memory: 8.00MB

OK (1 test, 1 assertion)
```

At the bottom, “OK (1 test, 1 assertion)” tells us that all our tests passed, and that we have one test (class method) and one assertion (`$this->assert...` call). The dot is part of the progress meter, and indicates a passing test; when you have multiple tests, you’ll see them complete live here with an indicator of their status (`.` = pass, `F` = fail, `E` = error, `W` = warning).

The assertion we wrote could be written a different way:

```
$this->assertSame( true, $should_be_true );
```

`assertSame` checks the value and type of the two variables matches, and is equivalent to `assertTrue( true === $should_be_true )`. While we could use either here, it’s best to use the most specific assertion possible. This generates precise error messages.

Most assertions take two parameters: `$expected` and `$actual`. You should always pass the expected value first to ensure the error messages match what you’d expect.

Most assertions also take an optional last parameter `$message` which lets you specify a custom error message to be displayed next to the assertion message. You should only use this parameter when it’s unclear why this assertion didn’t match based on the built-in error message.

Rather than writing custom messages, name your methods descriptively. If your `test_plugin_loaded` test fails, that’s enough information to debug without needing a custom message.

Congratulations, you just wrote your first PHPUnit test class! Almost every test you’ll ever write follows the same pattern: run code, and check the result matches what you expect using assertions.

## Configuring PHPUnit [#](#configuring-phpunit)

When we ran PHPUnit before, we had to pass the specific test class file in. This is OK for a single file, but we can simplify this by adding a configuration file for PHPUnit.

PHPUnit uses XML-based configuration, and loads from `phpunit.xml.dist` and `phpunit.xml`. You should commit the `.dist` file to your repository, and allow the other file to be used for local development overrides.

Let’s go ahead and create our configuration file. Save the following to `phpunit.xml.dist`:

```
<phpunit>
    <testsuites>
        <testsuite>
            <directory prefix="class-" suffix=".php">./tests/</directory>
        </testsuite>
    </testsuites>
</phpunit>
```

This tells PHPUnit that it should run every file in the `tests` directory that matches `class-*.php`. Right now, this is every file there, but we’ll add some additional special files later.

There are [a lot more configuration options](https://href.li/?https://phpunit.de/manual/current/en/appendixes.configuration.html), but we’ll start here for now. Don’t close the file, as we’ll edit it again in just a moment!

## Testing in the WordPress Context [#](#testing-in-the-wordpress-context)

Right now, we have a standalone PHPUnit test that doesn’t call out to any external code. To actually write tests for the real world, we need to load in our actual code and start testing it.

PHPUnit includes the ability to “bootstrap” your tests. The bootstrap file allows you to include any code you want to test against and is run automatically every time you run `phpunit`.

To enable bootstrapping, edit the `phpunit.xml.dist` file. Replace the existing `<phpunit>` open tag with this:

```
<phpunit
    bootstrap="tests/bootstrap.php"
>
```

(Since the file doesn’t start with `class-`, PHPUnit won’t try and run it as a test.)

We can then create our bootstrap file. We want to load in WordPress’ testing framework, which will automatically set up the WordPress internals to get ready for testing. To do this, we need a copy of WordPress’ development tools. The standard way to load this is through a `WP_TESTS_DIR` environment variable which points to the tests directory.

Chassis with the Tester extension will set up the required environment variables and copy of WordPress for you. For other environments, you need to set these yourself.

Save the following to `tests/bootstrap.php`:

```
<?php

namespace HM\ExamplePlugin\Tests;

// Get tests directory from environment.
$_tests_dir = getenv( 'WP_TESTS_DIR' );

// Give access to tests_add_filter() function.
require_once $_tests_dir . '/includes/functions.php';

/**
 * Manually load the plugin being tested.
 */
function manually_load_plugin() {
    require dirname( __DIR__ ) . '/plugin.php';
}
tests_add_filter( 'muplugins_loaded', __NAMESPACE__ . '\\manually_load_plugin' );

// Start up the WP testing environment.
require $_tests_dir . '/includes/bootstrap.php';
```

In this file, we get the WordPress test tools directory, load the required pieces, load our plugin manually, and then load up WordPress.

Core’s bootstrapping automatically wipes the database and creates it from scratch when testing, so our plugin needs to be loaded manually via a hook. This does **not** activate the plugin, so activation hooks will not be run, and the plugin will not be included in the active plugins option. Ensure you account for this in your code.

In our tests, we can now check against our plugin. Just to show that it works, we can declare a version constant in our plugin (`plugin.php`):

```
<?php
/**
 * Plugin Name: Example Plugin
 */

namespace HM\ExamplePlugin;

const VERSION = '1.0.0';
```

We can then write a new test for this. Add the following method to your `class-example-test.php` file:

```
public function test_plugin_loaded() {
    $this->assertTrue( defined( 'HM\\ExamplePlugin\\VERSION' ) );
}
```

With our new PHPUnit configuration file, you can now just run `phpunit` with no parameters. You should see the following:

```
Installing...
Running as single site... To run multisite, use -c tests/phpunit/multisite.xml
Not running ajax tests. To execute these, use --group ajax.
Not running ms-files tests. To execute these, use --group ms-files.
Not running external-http tests. To execute these, use --group external-http.
PHPUnit 5.7.3 by Sebastian Bergmann and contributors.

..                                                                  2 / 2 (100%)

Time: 2.71 seconds, Memory: 28.00MB

OK (2 tests, 2 assertions)
```

This new output is from WordPress’ bootstrap file, and indicates WordPress was successfully installed in test mode.

Congratulations, you can now write basic PHPUnit tests in WordPress! However, we can go further with this. Continue on to see how!

## Using WordPress’ Test Framework [#](#using-wordpress-test-framework)

Up until now, we’re been writing standard PHPUnit tests. These get you a lot of the way, and are all you need in a lot of cases, however we can now use WordPress’ test framework. This framework provides additional, WordPress-specific functionality.

Let’s do so in a new class. Save the following as `tests/class-plugin-test.php`:

```
<?php

namespace HM\ExamplePlugin\Tests;

use HM\ExamplePlugin;
use WP_UnitTestCase;

class Plugin_Test extends WP_UnitTestCase {
    // No tests yet!
}
```

This is almost exactly the same, except we now subclass `WP_UnitTestCase` instead of `PHPUnit_Framework_TestCase`. This gives us access to a bunch of additional functionality.

### Factories [#](#factories)

The WordPress framework has a concept called “factories”. These are classes that create objects for you following a standard pattern, without needing to handle all the fiddly bits (like default parameters, multiple function calls, etc) yourself. Out of the box, the framework provides factories for .

These factories are available via `$this->factory->{$type}`, where type is one of `post`, `attachment`, `comment`, `user`, `term`, `category`, `tag`, `blog` (sites) or `network`.

To use the factory, call the `create` method on the object. This takes an array of override arguments (like a specific post title), but you these are always optional. (To see the defaults, check the `default_generation_definitions` property.)

For example, if you need a post for a test:

```
$post_id = $this->factory->post->create();
```

If you need a user with a specific role:

```
$editor_id = $this->factory->user->create([
    'role' => 'editor',
]);
```

### `setUp` and `tearDown` [#](#setup-and-teardown)

Before every test (method) is run, PHPUnit runs a special method called `setUp`. Likewise, after every test, it runs a method called `tearDown`. These methods can be used to set up and restore global variables, or create common objects (like users).

The WordPress testing framework includes a default `setUp` and `tearDown`. In `setUp`, the framework makes a backup copy of certain global variables (including `$wp_filter`), and starts a database transaction. This switches MySQL to using temporary tables. In `tearDown`, hooks and other globals are reset to before the test ran, the current user is reset (logged out), and the transaction is rolled back. This causes any database changes to be discarded.

These hooks mean you can do things inside your tests (like adding filters) without worrying about it affecting other tests.

You can write your own custom `setUp` and `tearDown` methods to set up state you might need to use. This could include custom globals, clearing caches, or anything we want to do on every test.

**Important:** Always be sure to call `parent::setUp()` or `parent::tearDown()` when overriding, or your tests will leak and cause hard-to-debug errors.

Note the order as well; always call `parent::setUp()` before running your own setup, and call `parent::tearDown()` before tearing down your own variables.

For example, we can create an author user, and set the current user to it:

```
public function setUp() {
    parent::setUp();

    $this->author_id = $this->factory->user->create([
        'role' => 'author',
    ]);
    wp_set_current_user( $this->author_id );
}
```

By setting this to a property, we can use this ID directly in our tests. For example, we could create a post, then check that the user is correct:

```
public function test_author_defaults_to_current_user() {
    $post_id = $this->factory->post->create();
    $post = get_post( $post_id );

    $this->assertEquals( $this->author_id, $post->post_author );
}
```

In addition to these regular methods, PHPUnit includes static methods, called `setUpBeforeClass` and `tearDownAfterClass`. When using the WordPress framework, you should **not** use these; instead use `wpSetUpBeforeClass` and `wpTearDownAfterClass`. This runs in the correct sequence for database transactions. Inside these methods, you do not have to call `parent::...`.

Accessed Mon, 26 Feb 2018 10:02:28 +0000 from `https://engineering.hmn.md/guides/testing/phpunit/`

[Made by Humans](https://hmn.md)