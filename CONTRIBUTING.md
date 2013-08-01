# How to contribute

I like to encourage you to contribute to the repository.
This should be as easy as possible for you but there are a few things to consider when contributing.
The following guidelines for contribution should be followed if you want to submit a pull request.

## TL;DR

* Read [Github documentation](http://help.github.com/) and [Pull Request documentation](http://help.github.com/send-pull-requests/)
* Fork the repository
* Edit the files, add new files
* Check the files with [`pep8`](https://pypi.python.org/pypi/pep8), fix any reported errors
* Check that the files work as expected in CloudBot
* Create a new branch with a descriptive name for your feature (optional)
* Commit changes, push to your fork on GitHub
* Create a new pull request, provide a short summary of changes in the title line, with more information in the description field.
* After submitting the pull request, join the IRC channel (irc.esper.net #cloudbot) and paste a link to the pull request so people are aware of it
* After discussion, your pull request will be accepted or rejected.

## How to prepare

* You need a [GitHub account](https://github.com/signup/free)
* Submit an [issue ticket](https://github.com/ClouDev/CloudBot/issues) for your issue if the is no one yet.
  * Describe the issue and include steps to reproduce if it's a bug.
	* Ensure to mention the earliest version that you know is affected.
* If you are able and want to fix this, fork the repository on GitHub

## Make Changes

* In your forked repository, create a topic branch for your upcoming patch. (e.g. `feature--autoplay` or `bugfix--ios-crash`)
	* Usually this is based on the develop branch.
	* Create a branch based on master; `git branch
	fix/develop/my_contribution develop` then checkout the new branch with `git
	checkout fix/develop/my_contribution`.  Please avoid working directly on the `develop` branch.
* Make sure you stick to the coding style that is used already.
* Make use of the [`.editorconfig`](http://editorconfig.org/) file.
* Make commits of logical units and describe them properly.
* Check for unnecessary whitespace with `git diff --check` before committing.
* Check your changes with [`pep8`](https://pypi.python.org/pypi/pep8). Ignore messages about line length.

## Submit Changes

* Push your changes to a topic branch in your fork of the repository.
* Open a pull request to the original repository and choose the right original branch you want to patch.
	_Advanced users may use [`hub`](https://github.com/defunkt/hub#git-pull-request) gem for that._
* If not done in commit messages (which you really should do) please reference and update your issue with the code changes. But _please do not close the issue yourself_.
_Notice: You can [turn your previously filed issues into a pull-request here](http://issue2pr.herokuapp.com/)._
* Even if you have write access to the repository, do not directly push or merge pull-requests. Let another team member review your pull request and approve.

# Additional Resources

* [General GitHub documentation](http://help.github.com/)
* [GitHub pull request documentation](http://help.github.com/send-pull-requests/)
* [Read the Issue Guidelines by @necolas](https://github.com/necolas/issue-guidelines/blob/master/CONTRIBUTING.md) for more details
* [This CONTRIBUTING.md from here](https://github.com/anselmh/CONTRIBUTING.md)
