tweebot
=======

[![Build Status](https://travis-ci.org/kcsaff/tweebot.svg?branch=master)](https://travis-ci.org/kcsaff/tweebot)

A twitter bot client, written in Python.  This can be used as either a command-line tool, or as a library
imported into your Python applications.

Requirements
============

1. Python 3.3+
2. A twitter account

Installation
============

To install:

```
make install
```

Development
===========

To build the dev environment:

```
make venv
. venv/bin/activate
python main.py
```

Configuration
=============

The application will only try to tweet if you provide a key file,
which is formatted like:

```
CONSUMER_KEY: dsafsafafsd
CONSUMER_SECRET: iuhbfusdfiu44
ACCESS_KEY: vjhbv99889
ACCESS_SECRET: ivfjslfiguhg98
```

*OR* the equivalent JSON.

The filename must be provided using the ``--keys`` command-line argument.

Command-line usage
==================

Tweeting
--------

To tweet a simple status update:

```
tweebot --keys {twitter-key-file} tweet "Hello world, this is my Tweebot status update!" -vv
```

You can control verbosity with the number of ``v``s.

More command-line options are possible, try ``--help`` to see them all.

If you use ``-`` for the tweet text, the application will use standard input,
which can be handy for piping info from
your bots -- ie, use an arbitrary application to pipe to tweebot which can tweet it out.

Following
---------

To automatically follow new followers, and unfollow unfollowers:

```
tweebot --keys {twitter-key-file} follow --auto
```

Library usage
=============

There are two basic ways you can use this in a library:
you can either import the ``TwitterClient`` class and control
that from your application, or you can import
tweebot's ``main`` function and provide it with a callback
that will generate your status updates.

tweebot.main
------------

If you provide a callable to ``tweebot.main``,
then tweebot will use it as a callback when the main function is
called.  The main method implements all the command-line tweebot arguments,
the difference is that if the program
is asked to tweet an empty status, it will instead tweet the results of your method, called with no
arguments.  If you tweet a non-empty status, that string will be handed to your method, and the result will
be tweeted:

```
mytweebot --keys {twitter-key-file} tweet -vv
```

Thus, this provides a simple way to define new twitter-bots: define a method of the form:

```
def my_tweet_builder(status, directives):
    new_status = do_something()
    return new_status
    # or
    return new_status, new_directives
```

This can either ignore the status it's given, or use it in any way you wish.  If you have multiple bots that
modify the status when given, then you could run them independently, or pipe them together in novel ways without
recompiling -- your choice.

Direct client use
-----------------

If you want your application to be in control, you can simply import
``tweebot.TwitterClient`` and use its methods
directly.  This includes direct API access (via tweepy) to twitter, and few custom, convenience methods.
