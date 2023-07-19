# Intro

This guide is meant for Windows users who have little to no experience with Git / Version Control, Markdown, and Python.



If you are using Linux, I believe you can follow along just fine, and many things will be simplified.

# Prerequisites

## Github

This project uses Git (a version control system) to keep track of previous edits to the wiki. In this model, everyone has a **local** copy of the wiki, and may send / receive changes to / from other people.

This is hosted by [Github](https://github.com/); so make an account there.

## Github Desktop

To enable collaboration, you need to be able to interact with Git. If you are already familiar with Git and using the Command Line Interface, I would recommend [Git Bash](https://git-scm.com/downloads). If you are not, a simple GUI equivalent is [Github Desktop](https://desktop.github.com/) **Recommended for beginners**.

## Python

Python is used as the means of showing the wiki locally; getting custom themes; and running various utility scripts within the wiki. Get it here: [Python](https://www.python.org/downloads/).

Open up your **command prompt** after installing Python (application called cmd). The pip module this library uses to show the wiki is called *mkdocs*.

There are going to be two ways to use Python from here: the easy way and the *right but not necessary* way. If you are a beginner, just stick with

### The Easy Way

In Command Prompt, simply type and press enter: `pip install mkdocs`

### The Right Way

Do this if you already were using Python for something else; or plan on using Python for something else in the future. This process will create a Virtual Environment for Python, which is separate from other projects you are doing / will do in Python. If you don't think this is relevant / don't care, see **The Easy Way**.

(Do all of this in Command Prompt)

- In the location of your choice, create a venv for Python: `python -m venv .venv`

- Activate the **V**irtual **ENV**ironment `.\venv\Scripts\activate`

- Now you can install mkdocs `pip install mkdocs`

- In the future, when you open and close the Command Prompt, you will need to activate your venv again `.\venv\Scripts\activate`

## Web Browser

You will need a web browser for viewing the wiki. Any of your choice should be sufficient for these purposes; the generated HTML / JS is pretty simple.

## Markdown Editor

The wiki uses  **Markdown**, which is what this readme is written in! The extension for a markdown file is `.md`.

To learn how to type in this format, try [Markdown Basic Syntax Guide](https://www.markdownguide.org/basic-syntax/)

You can also freely insert HTML into Markdown. If you know HTML (or want to do things like center images), feel free to use it when applicable.

Any editor that can edit text will work for working on these files, but you may want something specific for Markdown. My recommendation is something simple, like [MarkText](https://github.com/marktext/marktext#download-and-installation). Alternatively, a good list can be found here: [List of Markdown Editors](https://github.com/mundimark/awesome-markdown-editors)

If you want a generally decent, entry level text editor that is better than Notepad (wow, what a low bar), try [Notepad++](https://notepad-plus-plus.org/downloads/) 

If you are more of a Vim / emacs person, of course those work too.

# Creating a New Wiki

## An Entirely New Wiki

From the wiki page on Github, there should be a green button which reads **Use this template** > Create a new repository. Be sure to **Include all Branches** and select whether or not your repository will be **public** or **private**.

## From Nuclino (!Advanced!)

If you had a Nuclino site that you would like to switch to this format, there is a Python script to do just that! Export the Nuclino site, then provide it as an argument to `bin\py\nuclino2docs.py`. This will create a folder which can be used as the docs folder for mkdocs.

## Getting Your Own Copy To Work On

If you are using **Github Desktop**.

- Open Github Desktop. If this is the first time doing so, it'll ask you to sign in; etc.

- Click **<> Code** > Local > Open with GitHub Desktop.
  
  - Choose the appropriate path to put the files (Default should be fine)

# Interacting with the Wiki

## Editing the Wiki

To edit the wiki, find out where it was placed in your computer. I believe the default location is in `Documents\Github\...`

Within the correct folder, you should see a `docs\` folder.  Edit these files with your favorite markdown editor to change the wiki!

### Share Your Changes

If you have changes to make, go back to Github Desktop. You should see a list of all of your changes, (file by file; line by line). You may choose which changes to share (The default should be all of them). Then you have to commit:

- Make a title for your changes

- Describe your changes

- Press the Commit Button

- Push the changes to origin (Highlighted button)

### Get New Changes

To get new changes, go to Github Desktop. In the top bar, press "Fetch Origin". If there have been changes made, there should be a "Pull Origin" button. This will give you all changes that people have made since last doing this process.

### Make New Changes Appear Publicly (!Advanced!)

Currently, the branch you push and pull from is master (looking at the top bar of Github Desktop should confirm this). However, if you push to the **public** branch, then any changes you make will be visible to the publicly facing website that Github automatically generates (through some nice mkdocs functionality and Github Actions).

Typically, you would want to checkout files or entirely merge master into public, then commit and push.

If your repo is private and you don't have an expensive GitHub subscription, this will unfortunately not work.

## (Pre)Viewing the Wiki

## Showing the Live Wiki

To show the live wiki, which updates in real time as you save edits to pages, do the following:

- Open up your Command Prompt and **navigate to the wiki folder**. This may be hard to do for new Command Line users. Think of it as the text equivalent for navigating folders in your computer.
  
  - See a list of folders  + files where you currently are `dir`
  
  - Go to folder X `cd X` (cd means change dir)
  
  - Go back one `cd ..`

- Prepare your Python (Those who followed The Easy Way do not need to do anything)

- `mkdocs serve`
  
  - If following changing your flavor, below:  `bin\win\serve_custom.bat`

- To close later, press ctrl+C in the Window
  
  - If asked to terminate batch job, `N`

## Exporting the Wiki Offline

You can provide the wiki to someone entirely offline (with no setup required). The downside to this format is that it isn't editable /  doesn't update in real time; may be msising images; and has various features like search disabled.

As in **Showing the Live Wiki**, navigate to the wiki folder and prepare your Python. Then, simply:

- `bin\win\build_local.bat`

- Provide the created zip file to whomever
  
  - To clean up: `bin\win\clean_local.bat`

## Changing Your Flavor

An advantage of having a local copy is that you can choose however you like to view it.

To get a new theme, e.g. mkdocs-material (Browse around for others, if you want). Here is a great [video about mkdcos-material](https://youtu.be/Q-YA_dA8C20)

- Prepare your Python

- `pip install mkdocs-material`

- Edit the `custom.yml` file:
  
  - ```yml
    theme:
      name: material
      # Theme configuration below
      # See video / associated documentation
    ```

- See it live: `bin\win\serve_custom.bat`
