import os
import subprocess
import logging

from subprocess import CalledProcessError


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def okd4_login(username: str,
               password: str,
               server: str):
    logger.info('Logging %s into %s', username, server)
    project = require_env_var('OKD_NAMESPACE')
    run_oc_command(
        ['oc', 'login', '-u', username, '-p', password, f'--server={server}']
    )
    run_oc_command(
        ['oc', 'project', f'{project}']
    )
    logger.info('Logged %s into %s, set namespace to %s', username, server, project)


def make_new_buildconfig(build_config_name: str,
                         image_and_tag: str,
                         namespace: str,
                         docker_repo: str,
                         push_secret: str,
                         dockerfile=''):
    logger.info('Making new buildconfig %s', build_config_name)

    dockerfile_content = dockerfile if dockerfile else f'FROM {image_and_tag}'

    empty_curly_braces = '{}'

    # TODO replace fstring YAML with PyYAML
    yaml_content = f'''kind: BuildConfig
apiVersion: build.openshift.io/v1
metadata:
  name: {build_config_name}
  namespace: {namespace}
spec:
  nodeSelector: null
  output:
    to:
      kind: DockerImage
      name: 'docker.io/{docker_repo}/{image_and_tag}'
    pushSecret:
      name: {push_secret}
  resources: {empty_curly_braces}
  successfulBuildsHistoryLimit: 5
  failedBuildsHistoryLimit: 5
  strategy:
    type: Docker
    dockerStrategy:
      from:
        kind: ImageStreamTag
        name: '{image_and_tag}'
  postCommit: {empty_curly_braces}
  source:
    type: Dockerfile
    dockerfile: "{dockerfile_content}"
  runPolicy: Serial'''

    yaml_file_name = f'{build_config_name}.yaml'

    directory = require_env_var('APP_YAML_DIRECTORY')
    os.makedirs(directory, exist_ok=True)

    file_path = os.path.join(directory, yaml_file_name)

    with open(file_path, 'w') as f:
        f.write(yaml_content)

    run_oc_command(
        ['oc', 'apply', '-f', f'{file_path}']
    )

    try:
        os.remove(file_path)
    except FileNotFoundError:
        logger.info('%s not found', file_path)
    except PermissionError:
        logger.info('Permission denied trying to delete %s', file_path)
    except Exception as e:
        logger.info('An error occurred trying to delete %s: %s', file_path, e)


def run_buildconfig(buildconfig_name: str,
                    namespace: str):
    logger.info('Running buildconfig %s', buildconfig_name)
    run_oc_command(
        ['oc', 'start-build', '--wait', f'{buildconfig_name}', '-n', f'{namespace}']
    )


def delete_buildconfig(buildconfig_name: str,
                       namespace: str):
    logger.info('Deleting buildconfig %s', buildconfig_name)
    run_oc_command(
        ['oc', 'delete', 'buildconfig', f'{buildconfig_name}', '-n', f'{namespace}']
    )


def push_to_dockerhub(image_and_tag: str,
                      dockerfile=None):
    buildconfig_name = f'{image_and_tag.replace(":","-")}-buildconfig'
    namespace = require_env_var('OKD_NAMESPACE')
    docker_repo = require_env_var('DOCKER_REPO')
    push_secret = require_env_var('OKD_PUSH_SECRET')
    try:
        if dockerfile:
            make_new_buildconfig(buildconfig_name, image_and_tag, namespace, docker_repo, push_secret, dockerfile)
        else:
            make_new_buildconfig(buildconfig_name, image_and_tag, namespace, docker_repo, push_secret)

        run_buildconfig(buildconfig_name, namespace)
    finally:
        delete_buildconfig(buildconfig_name, namespace)


def run_oc_command(command: list[str]):
    try:
        result = subprocess.run(
            command,
            check = True,
            capture_output = True,
            text = True
        )
        return result.stdout
    except CalledProcessError as e:
        logger.error('Command failed: %s', e)
        raise RuntimeError(e.stderr)


def require_env_var(env_var_name: str) -> str:
    env_var_value = os.getenv(env_var_name)
    if not env_var_value:
        raise RuntimeError(f'Environment variable {env_var_name} is required')
    return env_var_value
