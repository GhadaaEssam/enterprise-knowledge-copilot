# Source: https://engineering.hmn.md/guides/tooling/github/

# GitHub

## Using different SSH keys and Email per GitHub Organisation [#](#using-different-ssh-keys-and-email-per-github-organisation)

This guide shows how to make to make `git` automatically use an SSH key and email, *but only for a specific client*. This works *anywhere* on your machine, without environment variables, `direnv`, or using alias.

You’ll need this for clients that require developers to use a project-specific Github account, for instance when they have their own GitHub Enterprise account, or require the use of their own accounts and SSO. We’ll use this client, and the corresponding `example-org` Github organization as an example.

**First**, open your global git config file (`.gitconfig` at the root of your Home directory on MacOS) and add the following:

```
[includeIf "hasconfig:remote.*.url:git@github.com:example-org/**"]
    path = /Users/<your-username>/dev/example-org/.gitconfig
```

Now when interacting with the `example-org` Github organisation it will use the `example-org/.gitconfig` file. You can place this custom Git config file anywhere you want.

**Second**, open that file and specify 2 parameters:

```
[user]
    email = example@example.com
[core]
    sshCommand = "ssh -i /path/to/ssh/key -o IdentitiesOnly=yes"
```

`core.sshCommand` will override the `ssh` command used by `git` with one that specifies a client specific SSH key. Be sure to swap out both the email and the path to the SSH key you want to use. The email is optional, and you can add other git config parameters here too.

*Note*: Check your `.ssh/config` file. There might be an override in `IdentityFile` under `Host *`. Comment this out, or make it more specific.

Accessed Thu, 09 Jul 2026 14:25:22 +0000 from `https://engineering.hmn.md/guides/tooling/github/`

[Made by Humans](https://hmn.md)