# unroll-repo CLI

## Objective

Combine all the files in a remote repository into a single structured text file without having to download its contents locally

## Purpose

Passing the contents of the repository into an LLM to allow for easy understanding of the purpose and mechanisms of a repository

## Behaviour

`python3 unroll_repo.py [-h] [-b BRANCH] owner name`<br>

Has two required arguments: owner and name, which correspond to the owner of the repository and the name of the repository

If no branch flag is specified, the default branch is obtained and used

If the branch flag is specified, the specified branch is used.

If the repository owner, repository name or branch name is wrongly specified OR the repository is private, the CLI will stop and return an error message.

The CLI requests for the Git Tree using the GitHub API, parses the tree, then fills the tree in with the contents of the files obtained using the URL: `https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{branch}/{file_path}`

It outputs text that can be redirected to a file as such: `python3 unroll_repo.py owner_name repo_name > output.txt`

## Future Plans

Allow for access to private repositories:
- This CLI only handles public repositories and not private ones
- Decision was made because:
    - Many well known repositories are public
    - Private repositories would need to be accessed using the GitHub API, requiring a GitHub token which some users might not have

Handle images (both embedded and standalone):
- Could try to handle basic image formats such as PNG and JPG
- Images displayed in Jupyter Notebooks are PNG images in base64
    - Would require decoding
- Potentially run the images through a VLM in advance to get a description, but the LM might provide better answers if the TXT file and images are put in together. Latency of VLM is also a consideration.
- Could also follow the hyperlinks for images in markdown and obtain them

Option to unroll a local repository:
- Add a single argument e.g. just `python3 unroll_repo folder_name`, which would unroll the `folder_name` folder/repository

Option to ignore files/filetypes:
- Could add file names or extensions to ignore (e.g. .json, .lock, or LIICENSE and CREDITS) like .gitignore does for git.
- Possible behaviour: `python3 unroll_repo owner_name repo_name -i to_ignore.txt`. `to_ignore.txt` would contain the file/filetypes to ignore. 
