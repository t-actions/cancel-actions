#!/usr/bin/env python3
import os
import re
import sys
import logging
import requests
from typing import List


def fetch_all_page(
    url: str,
    next_link_key = 'next',
    ignore_error = True,
    sess = requests.Session()) -> List[requests.Response]:
    results = []
    while url:
        r = sess.get(url)
        url = ''

        if r.ok:
            results.append(r)
        elif ignore_error:
            logging.error('{0} Error: {1} for url: {2}'.format(
                r.status_code, r.reason, r.url))
            logging.error(r.content)
        else:
            r.raise_for_status()

        if next_link_key in r.links:
            url = r.links[next_link_key].get('url')

    return results


def cancel_actions(
        repo: str,
        ref: str,
        event: str,
        statuses = ['queued', 'in_progress'],
        sess = requests.Session(),
):
    for status in statuses:
        url = 'https://api.github.com/repos/{0}/actions/runs?branch={1}&event={2}&status={3}&per_page=100'.format(
            repo,
            ref,
            event,
            status,
        )

        if os.environ.get('IGNORE_ERROR'):
            responses = fetch_all_page(url, sess = sess)
        else:
            responses = fetch_all_page(url, sess = sess, ignore_error = False)

        for response in responses:
            for workflow in response.json()['workflow_runs']:
                if str(workflow['id']) != os.environ.get('GITHUB_RUN_ID'):
                    r = sess.post(workflow['cancel_url'])
                    if not os.environ.get('IGNORE_ERROR'):
                        r.raise_for_status()
                    elif not r.ok:
                        logging.error('{0} Error: {1} for url: {2}'.format(
                            r.status_code, r.reason, r.url))
                        logging.error(r.content)
                    else:
                        logging.info(
                            'Canceled workflow with run id: {0}'.format(
                                workflow['id']))


def main():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        logging.error('Cannot find env "GITHUB_TOKEN"')
        sys.exit(1)

    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        logging.error('Cannot find env "GITHUB_REPOSITORY"')
        sys.exit(1)

    event = os.environ.get('EVENT_NAME')
    if not event:
        logging.error('Cannot find env "EVENT_NAME"')
        sys.exit(1)

    ref = os.environ.get('REF')
    if not ref:
        logging.error('Cannot find env "REF"')
        sys.exit(1)
    ref = re.sub('^refs/(heads|tags)/', '', ref)

    with requests.Session() as sess:
        sess.headers['Authorization'] = 'token {0}'.format(token)
        sess.mount('http://', requests.adapters.HTTPAdapter(max_retries = 5))
        sess.mount('https://', requests.adapters.HTTPAdapter(max_retries = 5))
        cancel_actions(repo, ref, event, sess = sess)


if __name__ == "__main__":
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(asctime)s %(levelname)s %(message)s',
        datefmt = '%Y-%m-%d %X',
    )
    main()