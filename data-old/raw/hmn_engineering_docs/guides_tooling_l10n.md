# Source: https://engineering.hmn.md/guides/tooling/l10n/

# Localisation

WordPress uses three different types of files for managing translations:

* `.pot` files contain a list of all translatable strings in the code.
* `.po` files contain a list of translations for a particular language. They are generated from the `.pot` files.
* `.mo` files are machine-readable versions of `.po` files. They are used by the software to output translations.

## Languages and Locales [#](#languages-and-locales)

WordPress distinguishes between languages, like Portuguese, and locales, like Portuguese for Brazil.

The distinction is done via the naming. Language files only contain the language code, in this case `pt.po`. Locale files contain the language and the locale code, so `pt_BR.po`.

Correct naming is required for WordPress to find the correct translations. WordPress will look for the language file first, and then for the locale second.

## Localisation Tools [#](#localisation-tools)

The first tool we’ll use is [node-wp-i18n](https://href.li/?https://github.com/cedaro/node-wp-i18n). This Node module includes a command line tool for extracting translatable strings from code.

The second tool we’ll use is [Poedit](https://href.li/?https://poedit.net/), a MacOS app to create translations.

## Creating Translations [#](#creating-translations)

### Creating the POT File [#](#creating-the-pot-file)

To generate the POT file, open a Terminal window, and navigate to the root folder of your plugin or theme. Then run `wpi18n makepot`.

Assuming that the code is translation-ready, you’ll see that a `.pot` files has been created in the root directory.

### Creating the PO File [#](#creating-the-po-file)

* Start Poedit, and select *Create New Translation* from the welcome menu.
* Navigate to the directory containing the previously generated POT file, and open it.
* The UI will prompt you for the language of the translation. Make sure to select the right language and locale. This will ensure that the PO files are named correctly.
* Translate the strings.
* Save the PO file into the `languages` directory of your theme or plugin.

### Creating the MO File [#](#creating-the-mo-file)

Open an existing PO file in Poedit, and select *File > Compile to MO*. Save the MO file along the PO file in the `languages` directory.

Without the MO file, WordPress will not be able to load the translations.

## Updating Existing Translations [#](#updating-existing-translations)

* Open an existing PO file using *File > Open*.
* Select *Catalogue > Update from POT*. This will refresh the strings in the PO file.

Accessed Tue, 28 Aug 2018 07:21:59 +0000 from `https://engineering.hmn.md/guides/tooling/l10n/`

[Made by Humans](https://hmn.md)