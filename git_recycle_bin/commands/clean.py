import datetime
from dateutil.tz import tzlocal

from git_recycle_bin.utils.date import (
    parse_expire_date,
    date_parse_formatted,
    format_timespan,
    DATE_FMT_EXPIRE,
)
from git_recycle_bin.printer import printer

def clean(rbgit, remote_bin_name):
    remote_delete_expired_branches(rbgit, remote_bin_name)
    remote_flush_meta_for_commit(rbgit, remote_bin_name)


def remote_delete_expired_branches(rbgit, remote_bin_name):
    """
        Delete refs of expired branches on remote. Artifacts may still be kept alive by other refs, e.g. by latest-tag.
        Reclaiming disk-space on remote, requires running `git gc` or its equivalent -- _Housekeeping_ on GitLab.
        See https://docs.gitlab.com/ee/administration/housekeeping.html
    """
    branch_prefix = "artifact/expire/"
    lines = rbgit.cmd("ls-remote", "--heads", remote_bin_name, f"refs/heads/{branch_prefix}*").splitlines()

    now = datetime.datetime.now(tzlocal())

    for line in lines:
        _, branch = line.split(maxsplit=1)

        # Timezone may be absent, but we insist on date and time
        date_time_tz = parse_expire_date(branch)
        if date_time_tz['date'] == None: continue
        if date_time_tz['time'] == None: continue
        if date_time_tz['tzoffset'] == None:
            date_time_tz['tzoffset'] = datetime.datetime.strftime(now, "%z")

        compliant_expire_string = f"{date_time_tz['date']}/{date_time_tz['time']}{date_time_tz['tzoffset']}"
        expiry = date_parse_formatted(date_string=compliant_expire_string, date_format=DATE_FMT_EXPIRE)
        delta_formatted = format_timespan(dt_from=now, dt_to=expiry)

        if expiry.timestamp() > now.timestamp():
            printer.detail("Active", delta_formatted, branch)
            continue

        printer.high_level("Expired", delta_formatted, branch)
        rbgit.cmd("push", remote_bin_name, "--delete", branch)


def remote_flush_meta_for_commit(rbgit, remote_bin_name):
    """
        Every artifact has traceability metadata in the commit message. However we can not fetch the commit
        message without fetching the whole artifact too. Hence we have meta-for-commit refs, which point to
        blobs of only metadata. This way we can obtain metadata without downloading potentially big artifacts.

        The artifacts are kept clean either by their built-in expiry-dates or by whoever creating the artifact
        maintaining it, but there is no hook to clean the corresponding meta-for-commit ref.

        This subroutine will scan all existing meta-for-commit references and determine if an artifact is still
        available. If not, the metadata commit will be removed.
    """
    meta_set = rbgit.meta_for_commit_refs(remote_bin_name)
    heads    = rbgit.cmd("ls-remote", "--heads", remote_bin_name, "refs/heads/*").splitlines()
    tags     = rbgit.cmd("ls-remote", "--tags", remote_bin_name, "refs/tags/*").splitlines()

    sha_len = 40
    commits = { l[-sha_len:]: l[sha_len+1:] for l in meta_set }
    heads = { l[:sha_len] for l in heads }
    tags  = { l[:sha_len] for l in tags }
    branches = [ refspec for commit_sha, refspec in commits.items()
                 if commit_sha not in heads and commit_sha not in tags
                ]
    if branches:
        rbgit.cmd("push", remote_bin_name, "--delete", *branches)
