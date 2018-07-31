from rest_framework import serializers

from . import models


class NamespaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Namespace
        fields = ('id', 'name', 'slug', 'group')


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.License
        fields = ('id', 'name', 'spdx_id', 'url')


class ForgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Forge
        fields = ('id', 'name', 'slug', 'source', 'url')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Project
        fields = ('id', 'name', 'slug', 'public', 'main_namespace', 'main_forge', 'license', 'homepage', 'description',
                  'version', 'updated', 'tests', 'docs', 'debug', 'from_gepetto', 'created', 'updated')


class RepoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Repo
        fields = ('id', 'name', 'slug', 'forge', 'namespace', 'project', 'license', 'homepage', 'url',
                  'default_branch', 'open_issues', 'open_pr', 'repo_id', 'forked_from', 'clone_url', 'travis_id',
                  'description')


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Branch
        fields = ('id', 'name', 'project', 'ahead', 'behind', 'updated', 'repo', 'deleted', 'keep_doc', 'created',
                  'updated')


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Target
        fields = ('id', 'name', 'slug', 'active')


class RobotpkgSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Robotpkg
        fields = ('id', 'name', 'slug', 'project', 'category', 'pkgbase', 'pkgversion', 'master_sites',
                  'master_repository', 'maintainer', 'comment', 'homepage', 'license', 'public', 'description',
                  'updated')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ('id', 'robotpkg', 'target', 'created', 'image', 'py3', 'debug')


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contributor
        fields = ('id', 'projects', 'agreement_signed')


class ContributorNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContributorName
        fields = ('id', 'contributor', 'name')


class ContributorMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContributorMail
        fields = ('id', 'contributor', 'mail', 'invalid')


class DependencySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Dependency
        fields = ('id', 'project', 'library', 'robotpkg', 'cmake', 'ros')


