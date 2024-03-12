# [[file:../../org/projects.org::*Project utils][Project utils:1]]
import re
import functools
import json

from sqrt_data_service.api import settings

__all__ = ['fix_project_name', 'ProjectMatcher', 'get_project_id']

@functools.cache
def fix_project_name(name):
    return re.sub(r'^[\d\.A-Z-]+ ', '', name).strip()
# Project utils:1 ends here

# [[file:../../org/projects.org::*Project utils][Project utils:2]]
def get_project_id(name):
    res = re.search(r'^([\d\.A-Z-]+) ', name)
    if res:
        project_id = res.group(1)
        if '-' in project_id:
            project_id = '~' + project_id
        return project_id
    return None
# Project utils:2 ends here

# [[file:../../org/projects.org::*Project utils][Project utils:3]]
class ProjectMatcher:
    def __init__(self):
        with open(settings.projects.index, 'r') as f:
            self._data = json.load(f)
        self._project_per_git_repo = {}
        self._path_per_git_repo = {}
        self._projects = set()
        self._process_data(self._data)

    def _process_data(self, data, project=None, path=None):
        if path is None:
            path = []
        for datum in data:
            name = fix_project_name(datum['name'])
            if datum.get('project') is True:
                project = name
                self._projects.add(name)
            if datum.get('kind') == 'git':
                if project is not None:
                    self._project_per_git_repo[name] = project
                self._path_per_git_repo[name] = path
            if 'children' in datum:
                self._process_data(datum['children'], project, [*path, datum['name']])

    def get_project(self, git_repo):
        return self._project_per_git_repo.get(git_repo, None)

    def get_path(self, git_repo):
        return self._path_per_git_repo.get(git_repo, None)

    def get_is_project(self, name):
        return name in self._projects
# Project utils:3 ends here
