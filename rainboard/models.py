import logging

from django.db import models
from django.urls import reverse

from autoslug import AutoSlugField
from ndh.models import NamedModel, TimeStampedModel, Links
from ndh.utils import enum_to_choices, query_sum

import requests

from .utils import SOURCES, TARGETS

logger = logging.getLogger('rainboard.models')


class Namespace(NamedModel):
    group = models.BooleanField(default=False)


class License(models.Model):
    name = models.CharField(max_length=200)
    spdx_id = models.CharField(max_length=50, unique=True)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.spdx_id or self.name


class Project(Links, NamedModel, TimeStampedModel):
    private = models.BooleanField(default=False)
    main_namespace = models.ForeignKey(Namespace, on_delete=models.SET_NULL, null=True, blank=True)
    license = models.ForeignKey(License, on_delete=models.SET_NULL, blank=True, null=True)
    homepage = models.URLField(max_length=200, blank=True, null=True)

    def get_absolute_url(self):
        return reverse('rainboard:project', kwargs={'slug': self.slug})


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
        if self.source == SOURCES.github:
            return {'Authorization': f'token {self.token}', 'Accept': 'application/vnd.github.drax-preview+json'}
        if self.source == SOURCES.gitlab:
            return {'Private-Token': self.token}
        if self.source == SOURCES.redmine:
            return {'X-Redmine-API-Key': self.token}

    def api_url(self):
        if self.source == SOURCES.github:
            return 'https://api.github.com'
        if self.source == SOURCES.gitlab:
            return f'{self.url}/api/v4'
        return self.url

    def get_projects(self):  # TODO auto
        if self.source == SOURCES.github:
            return self.get_projects_github()
        if self.source == SOURCES.gitlab:
            return self.get_projects_gitlab()
        if self.source == SOURCES.redmine:
            return self.get_projects_redmine()

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
                print(repo_data['license'])
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
        self.get_namespaces_gitlab()
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

        for data in self.api_data('/projects'):
            update_gitlab(data)

        for orphan in Project.objects.filter(main_namespace=None):
            repo = orphan.repo_set.get(forge__source=SOURCES.gitlab)
            update_gitlab(self.api_data(f'/projects/{repo.forked_from}'))

    def get_projects_redmine(self):
        pass  # TODO


class Repo(TimeStampedModel):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name')
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
    # TODO gitlab:
    # description = models.TextField()
    # created_at = models.DateTimeField()
    # last_activity_at = models.DateTimeField()

    def __str__(self):
        return self.name

    def api_url(self):
        if self.forge.source == SOURCES.github:
            return f'{self.forge.api_url()}/repos/{self.namespace.slug}/{self.slug}'
        if self.forge.source == SOURCES.redmine:
            return f'{self.forge.api_url()}/projects/{self.repo_id}.json'
        if self.forge.source == SOURCES.gitlab:
            return f'{self.forge.api_url()}/projects/{self.repo_id}'

    def api_data(self, url=''):
        logger.info(f'requesting api {self.forge} {self.namespace} {self} {url}')
        req = requests.get(self.api_url() + url, verify=self.forge.verify, headers=self.forge.headers())
        return req.json() if req.status_code == 200 else []

    def api_update(self):
        data = self.api_data()
        if data:
            if self.forge.source == SOURCES.gitlab:
                return self.api_update_gitlab(data)
            if self.forge.source == SOURCES.github:
                return self.api_update_github(data)

    def api_update_gitlab(self, data):
        # TODO Missing: license, homepage, open_pr
        self.name = data['name']
        self.slug = data['path']
        self.url = data['web_url']
        self.open_issues = data['open_issues_count']
        self.default_branch = data['default_branch']
        if 'forked_from_project' in data:
            self.forked_from = data['forked_from_project']['id']
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



class Commit(NamedModel, TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Branch(NamedModel, TimeStampedModel):
    repo = models.ForeignKey(Repo, on_delete=models.CASCADE)
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.repo}/{self.name}'


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


class RobotpkgDependency(NamedModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Robotpkg(NamedModel):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    license = models.ForeignKey(License, on_delete=models.SET_NULL, blank=True, null=True)
    homepage = models.URLField(max_length=200, blank=True, null=True)


class RobotpkgBuild(TimeStampedModel):
    robotpkg = models.ForeignKey(Robotpkg, on_delete=models.CASCADE)
    target = models.PositiveSmallIntegerField(choices=enum_to_choices(TARGETS))
    passed = models.BooleanField(default=False)


# TODO: later
# class Dockerfile(NamedModel, TimeStampedModel):
    # project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # target = models.PositiveSmallIntegerField(choices=enum_to_choices(TARGETS))
