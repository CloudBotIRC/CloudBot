from git import Repo

from cloudbot import hook, web


@hook.command()
def update():
    repo = Repo()
    git = repo.git
    try:
        pull = git.pull()
    except Exception as e:
        return e
    if "\n" in pull:
        return web.paste(pull)
    else:
        return pull


@hook.command()
def version():
    repo = Repo()

    # get origin and fetch it
    origin = repo.remotes.origin
    info = origin.fetch()

    # get objects
    head = repo.head
    origin_head = info[0]
    current_commit = head.commit
    remote_commit = origin_head.commit

    if current_commit == remote_commit:
        in_sync = True
    else:
        in_sync = False

    # output
    return "Local \x02{}\x02 is at commit \x02{}\x02, remote \x02{}\x02 is at commit \x02{}\x02." \
           " You {} running the latest version.".format(head, current_commit.name_rev[:7],
                                                        origin_head, remote_commit.name_rev[:7],
                                                        "are" if in_sync else "are not")
