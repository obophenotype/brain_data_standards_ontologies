# File updating workflow

The editors workflow is one of the formal [workflows](index.md) to ensure that the ontology is developed correctly according to ontology engineering principles. T


### Local editing workflow

Workflow requirements:
- git
- github

#### 1. _Create issue_
This would allow us to understand what the changes are (can skip if it is just an update of a file)

#### 2. _Update main branch_ 
In your local environment (e.g. your laptop), make sure you are on the `main` (prev. `master`) branch and ensure that you have all the upstream changes, for example:

```
git checkout master
git pull
```

#### 3. _Create feature branch_
Create a new branch. Per convention, we try to use meaningful branch names such as:
- issue23removeprocess (where issue 23 is the related issue on GitHub)
- issue26addcontributor
- release20210101 (for releases)

On your command line, this looks like this:

```
git checkout -b issue23removeprocess
```

#### 4. _Perform edit_
Using your editor of choice, perform the intended edit/change of file

#### 5. _Check the Git diff_
This step is very important. Rather than simply trusting your change had the intended effect, we should always use a git diff as a first pass for sanity checking.

In our experience, having a visual git client like [GitHub Desktop](https://desktop.github.com/) or [sourcetree](https://www.sourcetreeapp.com/) is really helpful for this part. In case you prefer the command line:

```
git status
git diff
```
#### 6. Quality control
Now its time to run your quality control checks through our continuous integration system (more details to come).


#### 7. Pull request

When you are happy with the changes, you commit your changes to your feature branch, push them upstream (to GitHub) and create a pull request. For example:

```
git add NAMEOFCHANGEDFILES
git commit -m "Added biological process term #12"
git push -u origin issue23removeprocess
```

Then you go to your project on GitHub, and create a new pull request from the branch, for example: https://github.com/INCATools/ontology-development-kit/pulls

There is a lot of great advise on how to write pull requests, but at the very least you should:
- mention the tickets affected: `see #23` to link to a related ticket, or `fixes #23` if, by merging this pull request, the ticket is fixed. Tickets in the latter case will be closed automatically by Github when the pull request is merged.
- summarise the changes in a few sentences. Consider the reviewer: what would they want to know right away.
- If the diff is large, provide instructions on how to review the pull request best (sometimes, there are many changed files, but only one important change).

#### 8. Review
Once all the automatic tests have passed (might not for now), assign @hkir-dev & @shawntanzk as reviewers (this pings us and let us know there's an update). Also do assign yourself as the assignee so we can easily keep track on who made which PR.

#### 9. Merge and cleanup
When the QC is green and the reviews are in (approvals), it is time to merge the pull request. @hkir-dev or @shawntanzk will be the one merging for now as changes need to be pushed to various branches.
After the pull request is merged, remember to delete the branch as well (this option will show up as a big button right after you have merged the pull request). If you have not done so, close all the associated tickets fixed by the pull request.
