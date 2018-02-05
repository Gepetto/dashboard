import logging
import re
from subprocess import check_output

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.db import models
from django.urls import reverse

import requests
from autoslug import AutoSlugField
from ndh.models import Links, NamedModel, TimeStampedModel
from ndh.utils import enum_to_choices
import git

from .utils import SOURCES, TARGETS, slugify_with_dots

logger = logging.getLogger('rainboard.models')

MAIN_BRANCHES = ['master', 'devel']
RPKG_URL = 'http://robotpkg.openrobots.org'
RPKG_LICENSES = {'gnu-lgpl-v3': 'LGPL-3.0', 'gnu-lgpl-v2': 'LGPL-2.0', 'mit': 'MIT', 'gnu-gpl-v3': 'GPL-3.0',
                 '2-clause-bsd': 'BSD-2-Clause'}
RPKG_FIELDS = ['PKGBASE', 'PKGVERSION', 'MASTER_SITES', 'MASTER_REPOSITORY', 'MAINTAINER', 'COMMENT', 'HOMEPAGE']
CMAKE_FIELDS = {'NAME': 'name', 'DESCRIPTION': 'description', 'URL': 'homepage', 'VERSION': 'version'}


class Article(NamedModel):
    authors = models.ManyToManyField(settings.AUTH_USER_MODEL)
    year = models.PositiveSmallIntegerField()
    url = models.URLField(max_length=200)
    pdf = models.URLField(max_length=200)


class Namespace(NamedModel):
    group = models.BooleanField(default=False)


class License(models.Model):
    name = models.CharField(max_length=200)
    spdx_id = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.spdx_id or self.name


class Forge(Links, NamedModel):
    source = models.PositiveSmallIntegerField(choices=enum_to_choices(SOURCES))
    url = models.URLField(max_length=200)
    token = models.CharField(max_length=50, blank=True, null=True)
    verify = models.BooleanField(default=True)

    def get_absolute_url(self):
        return self.url

    def api_data(self, url=''):
        logger.info(f'requesting api {self}{url}')
        req = requests.get(self.api_url() + url, verify=self.verify, headers=self.headers())
        return req.json() if req.status_code == 200 else []

    def headers(self):
        return {
            SOURCES.github: {'Authorization': f'token {self.token}', 'Accept':
                             'application/vnd.github.drax-preview+json'},
            SOURCES.gitlab: {'Private-Token': self.token},
            SOURCES.redmine: {'X-Redmine-API-Key': self.token},
            SOURCES.travis: {'Authorization': f'token {self.token}',
                             'TRAVIS-API-Version': '3'},
        }[self.source]

    def api_url(self):
        return {
            SOURCES.github: 'https://api.github.com',
            SOURCES.gitlab: f'{self.url}/api/v4',
            SOURCES.redmine: self.url,
            SOURCES.travis: 'https://api.travis-ci.org',
        }[self.source]

    def get_projects(self):
        return getattr(self, f'get_projects_{self.get_source_display()}')()

    def get_namespaces_github(self):
        for namespace in Namespace.objects.filter(group=True):
            for data in self.api_data(f'/orgs/{namespace.slug}/members'):
                Namespace.objects.get_or_create(slug=data['login'],
                                                defaults={'name': data['login'], 'group': False})

    def get_projects_github(self):
        def update_github(namespace, data):
            project, _ = Project.objects.get_or_create(name=data['name'],
                                                       defaults={'homepage': data['homepage'],
                                                                 'main_namespace': namespace})
            repo, _ = Repo.objects.get_or_create(forge=self, namespace=namespace, project=project,
                                                 defaults={'repo_id': data['id'], 'name': data['name']})
            repo.homepage = data['homepage']
            repo.url = data['html_url']
            repo.repo_id = data['id']
            repo.default_branch = data['default_branch']
            repo.open_issues = data['open_issues']

            repo_data = repo.api_data()
            if repo_data and 'license' in repo_data and repo_data['license']:
                if 'spdx_id' in repo_data['license'] and repo_data['license']['spdx_id']:
                    license = License.objects.get(spdx_id=repo_data['license']['spdx_id'])
                    repo.license = license
                    if not project.license:
                        project.license = license
            repo.open_pr = len(repo.api_data('/pulls'))
            repo.save()
            project.save()

        self.get_namespaces_github()
        for org in Namespace.objects.filter(group=True):
            for data in self.api_data(f'/orgs/{org.slug}/repos'):
                update_github(org, data)
        for user in Namespace.objects.filter(group=False):
            for data in self.api_data(f'/users/{user.slug}/repos'):
                if not Project.objects.filter(name=data['name']).exists():
                    continue
                update_github(user, data)

    def get_namespaces_gitlab(self):
        for data in self.api_data('/namespaces'):
            Namespace.objects.get_or_create(slug=data['path'],
                                            defaults={'name': data['name'], 'group': data['kind'] == 'group'})

    def get_projects_gitlab(self):
        def update_gitlab(data):
            project, created = Project.objects.get_or_create(name=data['name'])
            namespace, _ = Namespace.objects.get_or_create(name=data['namespace']['name'])
            repo, _ = Repo.objects.get_or_create(forge=self, namespace=namespace, project=project,
                                                 defaults={'repo_id': data['id'], 'name': data['name'],
                                                           'url': data['web_url']})
            if 'forked_from_project' in data:
                repo.forked_from = data['forked_from_project']['id']
                repo.save()
            elif created or project.main_namespace is None:
                project.main_namespace = namespace
                project.save()

        self.get_namespaces_gitlab()

        for data in self.api_data('/projects'):
            update_gitlab(data)

        for orphan in Project.objects.filter(main_namespace=None):
            repo = orphan.repo_set.filter(forge__source=SOURCES.gitlab).first()
            update_gitlab(self.api_data(f'/projects/{repo.forked_from}'))

    def get_projects_redmine(self):
        pass  # TODO


class Project(Links, NamedModel, TimeStampedModel):
    private = models.BooleanField(default=False)
    main_namespace = models.ForeignKey(Namespace, on_delete=models.SET_NULL, null=True, blank=True)
    main_forge = models.ForeignKey(Forge, on_delete=models.SET_NULL, null=True, blank=True)
    license = models.ForeignKey(License, on_delete=models.SET_NULL, blank=True, null=True)
    homepage = models.URLField(max_length=200, blank=True, null=True)
    articles = models.ManyToManyField(Article)
    description = models.TextField()
    version = models.CharField(max_length=20, blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    # TODO: release github ↔ robotpkg

    def get_absolute_url(self):
        return reverse('rainboard:project', kwargs={'slug': self.slug})

    def git_path(self):
        return settings.RAINBOARD_GITS / self.main_namespace.slug / self.slug

    def git(self):
        path = self.git_path()
        if not path.exists():
            logger.info(f'Creating repo for {self.main_namespace.slug}/{self.slug}')
            return git.Repo.init(path)
        return git.Repo(str(path / '.git'))

    def main_repo(self):
        repo, created = Repo.objects.get_or_create(forge=self.main_forge, namespace=self.main_namespace, project=self,
                                                   defaults={'name': self.name, 'default_branch': 'master',
                                                             'repo_id': 0})
        if created:
            repo.api_update()
        return repo

    def update_branches(self, main=True):
        branches = [b[2:] for b in self.git().git.branch('-a', '--no-color').split('\n')]
        if main:
            branches = [b for b in branches if b.endswith('master') or b.endswith('devel')]
        for branch in branches:
            if branch in MAIN_BRANCHES:
                instance, created = Branch.objects.get_or_create(name=branch, project=self)
                if created:
                    instance.update()
            else:
                name = '/'.join(branch.split('/')[1:])
                forge, namespace = name.split('/')[:2]
                repo, created = Repo.objects.get_or_create(forge__slug=forge, namespace__slug=namespace, project=self,
                                                   defaults={'name': self.name, 'default_branch': 'master',
                                                             'repo_id': 0})
                if created:
                    repo.api_update()
                instance, created = Branch.objects.get_or_create(name=name, project=self)
                if created:
                    instance.update()

    def main_branch(self):
        return 'devel' if 'devel' in self.git().heads else 'master'

    def cmake(self):
        filename = self.git_path() / 'CMakeLists.txt'
        if not filename.exists():
            return
        with filename.open() as f:
            content = f.read()
        for key, value in CMAKE_FIELDS.items():
            search = re.search(f'set\s*\(\s*project_{key}\s+([^)]+)*\)', content, re.I)
            if search:
                self.__dict__[value] = search.groups()[0].strip(''' \r\n\t'"''')
                self.save()

    def repos(self):
        return self.repo_set.count()

    def rpkgs(self):
        return self.robotpkg_set.count()

    def update(self):
        robotpkg = self.robotpkg_set.order_by('-updated').first()
        branch = self.branch_set.order_by('-updated').first().updated
        self.updated = max(branch, robotpkg.updated) if robotpkg else branch
        self.save()


class Repo(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', slugify=slugify_with_dots)
    forge = models.ForeignKey(Forge, on_delete=models.CASCADE)
    namespace = models.ForeignKey(Namespace, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    license = models.ForeignKey(License, on_delete=models.SET_NULL, blank=True, null=True)
    homepage = models.URLField(max_length=200, blank=True, null=True)
    url = models.URLField(max_length=200, blank=True, null=True)
    default_branch = models.CharField(max_length=50)
    open_issues = models.PositiveSmallIntegerField(blank=True, null=True)
    open_pr = models.PositiveSmallIntegerField(blank=True, null=True)
    repo_id = models.PositiveIntegerField()
    forked_from = models.PositiveIntegerField(blank=True, null=True)
    clone_url = models.URLField(max_length=200, blank=True, null=True)
    travis_id = models.PositiveIntegerField(blank=True, null=True)
    # TODO gitlab:
    # description = models.TextField()
    # created_at = models.DateTimeField()
    # last_activity_at = models.DateTimeField()

    def __str__(self):
        return self.name

    def api_url(self):
        return {
            SOURCES.github: f'{self.forge.api_url()}/repos/{self.namespace.slug}/{self.slug}',
            SOURCES.redmine: f'{self.forge.api_url()}/projects/{self.repo_id}.json',
            SOURCES.gitlab: f'{self.forge.api_url()}/projects/{self.repo_id}',
        }[self.forge.source]

    def api_data(self, url=''):
        logger.info(f'requesting api {self.forge} {self.namespace} {self} {url}')
        req = requests.get(self.api_url() + url, verify=self.forge.verify, headers=self.forge.headers())
        return req.json() if req.status_code == 200 else []

    def api_update(self):
        data = self.api_data()
        if data:
            return getattr(self, f'api_update_{self.forge.get_source_display()}')(data)

    def api_update_gitlab(self, data):
        # TODO Missing: license, homepage, open_pr
        self.name = data['name']
        self.slug = data['path']
        self.url = data['web_url']
        self.open_issues = data['open_issues_count']
        self.default_branch = data['default_branch']
        if 'forked_from_project' in data:
            self.forked_from = data['forked_from_project']['id']
        self.clone_url = data['http_url_to_repo']
        self.save()

    def api_update_github(self, data):
        # TODO Missing: open_pr
        self.name = data['name']
        if data['license'] is not None:
            self.license = License.objects.filter(spdx_id=data['license']['spdx_id']).first()
        self.homepage = data['homepage']
        self.url = data['url']
        self.default_branch = data['default_branch']
        self.open_issues = data['open_issues_count']
        self.repo_id = data['id']
        if 'source' in data:
            self.forked_from = data['source']['id']
        self.clone_url = data['clone_url']
        self.save()

    def get_clone_url(self):
        if self.forge.source == SOURCES.gitlab:
            return self.clone_url.replace('://', f'://gitlab-ci-token:{self.forge.token}@')
        return self.clone_url

    def git_remote(self):
        return f'{self.forge.slug}/{self.namespace.slug}'

    def git(self):
        git_repo = self.project.git()
        remote = self.git_remote()
        try:
            return git_repo.remote(remote)
        except ValueError:
            logger.info(f'Creating remote {remote}')
            return git_repo.create_remote(remote, self.get_clone_url())

    def main_branch(self):
        return self.project.branch_set.get(name=f'{self.git_remote()}/{self.default_branch}')

    def ahead(self):
        return self.main_branch().ahead

    def behind(self):
        return self.main_branch().behind


class Commit(NamedModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Branch(TimeStampedModel):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    ahead = models.PositiveSmallIntegerField(blank=True, null=True)
    behind = models.PositiveSmallIntegerField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('project', 'name')

    def get_ahead(self, branch='master'):
        commits = self.project.git().git.rev_list(f'{branch}..{self}')
        return len(commits.split('\n')) if commits else 0

    def get_behind(self, branch='master'):
        commits = self.project.git().git.rev_list(f'{self}..{branch}')
        return len(commits.split('\n')) if commits else 0

    def git(self):
        git_repo = self.project.git()
        if self.name not in git_repo.branches:
            remote = self.repo.git()
            _, _, branch = self.name.split('/', maxsplit=2)
            git_repo.create_head(self.name, remote.refs[branch]).set_tracking_branch(remote.refs[branch])
        return git_repo.branches[self.name]

    def update(self, pull=True):
        if pull:
            self.project.main_repo().git().fetch()
            if self.name not in MAIN_BRANCHES:
                self.repo.git().fetch()
        main_branch = self.project.main_branch()
        self.ahead = self.get_ahead(main_branch)
        self.behind = self.get_behind(main_branch)
        self.updated = self.git().commit.authored_datetime
        self.save()


class Test(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    target = models.PositiveSmallIntegerField(choices=enum_to_choices(TARGETS))
    passed = models.BooleanField(default=False)
    # TODO: travis vs gitlab-ci ?
    # TODO: deploy binary, doc, coverage, lint


class SystemDependency(NamedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    target = models.PositiveSmallIntegerField(choices=enum_to_choices(TARGETS))


class Robotpkg(NamedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)

    pkgbase = models.CharField(max_length=50, default='')
    pkgversion = models.CharField(max_length=20, default='')
    master_sites = models.CharField(max_length=200, default='')
    master_repository = models.CharField(max_length=200, default='')
    maintainer = models.CharField(max_length=200, default='')
    comment = models.TextField()
    homepage = models.URLField(max_length=200, default='')

    license = models.ForeignKey(License, on_delete=models.SET_NULL, blank=True, null=True)
    private = models.BooleanField(default=False)
    description = models.TextField()
    updated = models.DateTimeField(blank=True, null=True)

    def main_page(self):
        if self.category != 'wip':
            return f'{RPKG_URL}/robotpkg/{self.category}/{self.name}'

    def build_page(self):
        path = '-wip/wip' if self.category == 'wip' else f'/{self.category}'
        return f'{RPKG_URL}/rbulk/robotpkg{path}/{self.name}'

    def update(self, pull=True):
        path = settings.RAINBOARD_RPKG
        repo = git.Repo(str(path / 'wip' / '.git' if self.category == 'wip' else path / '.git'))
        if pull:
            repo.remotes.origin.pull()

        cwd = path / self.category / self.name
        for field in RPKG_FIELDS:
            cmd = ['make', 'show-var', f'VARNAME={field}']
            self.__dict__[field.lower()] = check_output(cmd, cwd=cwd).decode().strip()

        repo_path = self.name if self.category == 'wip' else f'{self.category}/{self.name}'
        last_commit = next(repo.iter_commits(paths=repo_path, max_count=1))
        self.updated = last_commit.authored_datetime

        license = check_output(['make', 'show-var', f'VARNAME=LICENSE'], cwd=cwd).decode().strip()
        if license in RPKG_LICENSES:
            self.license = License.objects.get(spdx_id=RPKG_LICENSES[license])
        else:
            logger.warning(f'Unknown robotpkg license: {license}')
        self.private = bool(check_output(['make', 'show-var', f'VARNAME=RESTRICTED'], cwd=cwd).decode().strip())
        with (cwd / 'DESCR').open() as f:
            self.description = f.read().strip()

        self.save()


class RobotpkgBuild(TimeStampedModel):
    robotpkg = models.ForeignKey(Robotpkg, on_delete=models.CASCADE)
    target = models.PositiveSmallIntegerField(choices=enum_to_choices(TARGETS))
    passed = models.BooleanField(default=False)


# TODO: later
# class Dockerfile(NamedModel, TimeStampedModel):
    # project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # target = models.PositiveSmallIntegerField(choices=enum_to_choices(TARGETS))
