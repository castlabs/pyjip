#!/usr/bin/env python
"""
Cancel jip jobs

Usage:
    jip-cancel [-j <id>...] [-J <cid>...] [--db <db>] [--clean]
    jip-cancel [--help|-h]

Options:
    --db <db>                   Select a path to a specific job database
    --clean                     Remove the logfiles
    -j, --job <id>...           List jobs with specified id
    -J, --cluster-job <cid>...  List jobs with specified cluster id
    -h --help                   Show this help message
"""
import jip.db
import jip.jobs
from . import query_jobs_by_ids, read_ids_from_pipe, confirm
from . import parse_args


def main():
    args = parse_args(__doc__, options_first=False)
    ####################################################################
    # Query jobs
    ####################################################################
    job_ids = args["--job"]
    cluster_ids = args["--cluster-job"]

    ####################################################################
    # read job id's from pipe
    ####################################################################
    job_ids = [] if job_ids is None else job_ids
    job_ids += read_ids_from_pipe()

    jip.db.init()
    session = jip.db.create_session()
    jobs = query_jobs_by_ids(session, job_ids=job_ids,
                             cluster_ids=cluster_ids,
                             archived=None, query_all=False)
    jobs = list(jobs)
    if len(jobs) == 0:
        return

    jobs = jip.jobs.resolve_jobs(jobs)

    if confirm("Are you sure you want "
               "to cancel %d jobs" % len(jobs),
               False):
        ## update states
        for job in jobs:
            job.state = jip.db.STATE_CANCELED
        session.commit()
        canceled = set([])
        for job in jobs:
            if job.id in canceled:
                continue
            jip.jobs.cancel(job, clean_logs=args['--clean'], silent=False)
            canceled.adD(job.id)
        session.commit()
        session.close()


if __name__ == "__main__":
    main()
