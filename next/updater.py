from constants import ConfKeys, GitHub
from gh_api import GitHubAPI
import subprocess
import re
import os


class UpdateManager(object):
    def __init__(self, conf, messages):
        self.conf = conf
        self.messages = messages
        self.print_output = False

    def update(self):
        try:
            self.msg(u'Cleaning install directory...')
            rootdir = os.path.dirname(os.path.abspath(__file__))
            for root, _, files in os.walk(rootdir):
                for f in files:
                    if f.endswith('.pyc'):
                        os.remove(os.path.join(root, f))
            self.msg(u'Done!')
            self.msg(u'Updating...')
            branch = self.find_branch()
            output, err = self.run_git(['pull', 'origin', branch])
            if err == None:
                self.msg('Done!')
            else:
                self.err(u'Something went wrong:')
                self.err(err)
            self.msg(u'Updating remotes...')
            output, err = self.run_git(['remote', 'update'])
            if err == None:
                self.msg('Done!')
            else:
                self.err(u'Something went wrong:')
                self.err(err)
        except Exception, e:
            self.err(u'Something went wrong:')
            self.err(str(e))

    def check_for_new_version(self):
        branch = self.find_branch()
        default_remote = self.find_remote()

        output, error = self.run_git(['merge-base', 'HEAD',
            default_remote])
        if error or not output:
            raise UpdateError

        last_common_hash = output.strip()

        if not re.match(r'[a-z0-9]*', last_common_hash):
            self.err(u'Faulty local git output, ignoring')
            raise UpdateError
            return

        num_behind = 0
        gh = GitHubAPI()
        try:
            gh_commits = gh.commits(GitHub.GITHUB_USER, GitHub.GITHUB_REPO,
                    branch)
        except IOError:
            self.err(u'Could not connect to Github, are you connected to the '
            'internet?')
            raise UpdateError
        for commit in gh_commits:
            try:
                if not re.match(r'[a-z0-9]*', commit['sha']):
                    break
                if commit['sha'] == last_common_hash:
                    break

                num_behind += 1
            except:
                break

        if num_behind:
            self.msg((u'There is a newer version of next available, you are '
            '{0} commit(s) behind!').format(num_behind))
            return True
        else:
            self.msg(u'No update for next available!')
            return False

    def find_remote(self):
        '''
        A method to find the default remote that would be addressed when
        running "git pull"
        '''
        result = u'origin'
        try:
            output, err = self.run_git(['rev-parse', '--symbolic-full-name',
                '@{u}'])
            result = output.strip().replace('refs/remotes/', '', 1)
        except:
            pass
        return result

    def find_branch(self):
        '''
        A method to find the branch that the user checked out for next (master
        or develop)
        '''
        result = u'master'
        try:
            output, err = self.run_git(['symbolic-ref', '-q', 'HEAD'])
            result = output.strip().replace('refs/heads/', '', 1)
        except:
            pass
        return result

    def run_git(self, args):
        '''
        Helper method to run git with a given set of arguments
        Heavily based on the _run_git method of SickBeard
        '''
        if self.conf.get(ConfKeys.GIT_PATH, None):
            cmd = [self.conf[ConfKeys.GIT_PATH]] + args
        else:
            cmd = ['git'] + args

        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, cwd=self.conf[ConfKeys.BASE_DIR])
            output, err = p.communicate()
        except OSError:
            self.msg(u'Something went wrong while running git!')

        if ((p and p.returncode != 0) or 'not found' in output or
        'not recognized as an internal or external command' in output):
            self.err(u'Git could not be found on your system or something '
            'went horribly wrong!')
            output = None
        elif 'fatal:' in output or err:
            self.err(u'Git returned bad info, have you installed next using '
            'git?')
            output = None
        return (output, err)

    def msg(self, m):
        if self.print_output:
            print m
        else:
            self.messages.push(m)

    def err(self, m):
        self.messages.clear()
        if self.print_output:
            print m
        else:
            self.messages.push(m)


class UpdateError(Exception):
    pass
