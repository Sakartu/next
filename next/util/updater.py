from constants import ConfKeys
from gh_api import GitHubAPI
import subprocess
from constants import GitHub
import re


class UpdateManager(object):
    def __init__(self, conf, messages):
        self.conf = conf
        self.messages = messages

    def update(self):
        self.run_git(u'pull origin autoupdate')

    def check_for_new_version(self):
        self.msg(u'Checking for new version...')
        output, _ = self.run_git('rev-parse HEAD')
        current_hash = output.strip()

        if not re.match(r'[a-z0-9]*', current_hash):
            self.msg(u'Faulty local git output, ignoring')
            return

        branch = self.find_branch(self.conf)

        num_behind = 0
        gh = GitHubAPI()
        for commit in gh.commits(GitHub.GITHUB_USER,
                GitHub.GITHUB_REPO, branch):
            if commit == current_hash:
                break

            num_behind += 1

        if num_behind:
            self.msg((u'There is a newer version of next available, you are '
            '{0} commits behind!').format(num_behind))
        else:
            self.msg(u'No update available!')

    def find_branch(self, conf):
        '''
        A method to find the branch that the user checked out for next (master
        or develop)
        '''
        result = u'master'
        try:
            output, err = self.run_git('symbolic-ref -q HEAD')
            result = output.strip().replace('refs/heads/', '', 1)
        except:
            pass
        return result

    def run_git(self, args):
        '''
        Helper method to run git with a given set of arguments
        Heavily based on the _run_git method of SickBeard
        '''
        cmd = [u'git ' + args]
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, shell=True,
                cwd=self.conf[ConfKeys.BASE_DIR])
            output, err = p.communicate()
        except OSError:
            self.msg(u'Something went wrong while running git!')
        if(p.returncode != 0 or 'not found' in output or
        'not recognized as an internal or external command' in output):
            self.msg(u'Git could not be found on your system!')
            output = None
        elif 'fatal:' in output or err:
            self.msg(u'Git returned bad info, have you installed next using '
            'git?')
            output = None
        return (output, err)

    def msg(self, m):
        self.messages.append(m)
