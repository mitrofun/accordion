#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import *
from fabric.colors import red
from fabric.contrib.files import upload_template
from settings import USER, PASS
from settings import HOSTS, DOMAIN, SUBDOMAIN

REPO = 'https://github.com/mitrofun/loftschool-javascript.git'
PROJECT_NAME = 'loftschool-javascript'
env.hosts = HOSTS


@task
def clone_project():
    try:
        run('git clone {repo}'.format(repo=REPO))
    except:
        print(red('dir {} already have, del dir and clone again'.format(PROJECT_NAME)))
        run('rm -rf {project}'.format(project=PROJECT_NAME))
        run('git clone {repo}'.format(repo=REPO))


@task
def create_config(build):
    if build:
        env.root = env.root + 'build/'
    context = {
        'domain': env.domain,
        'root': env.root
    }
    env.nginx = '{}/config/{}-nginx.conf'.format(env.project_dir, env.work)
    upload_template('config/nginx.template', env.nginx, context, use_jinja=True, )


@task
def link_conf():
    nginx_link = '/etc/nginx/sites-enabled/{}.conf'.format(env.domain)
    sudo('ln -s {} {}'.format(env.nginx, nginx_link))


@task
def reload():
    """
    Рестарт nginx
    :return:
    """
    sudo('nginx -s reload')


@task
def install_bower():
    sudo('apt-get install nodejs -y')
    sudo('apt-get install npm -y')
    sudo('npm install -g bower')
    sudo('ln -s /usr/bin/nodejs /usr/bin/node')


def bower_install():
    try:
        run('bower i')
    except:
        with cd(env.root):
            run('bower install')


@task
def deploy(user=USER, pas=PASS, subdomain=SUBDOMAIN):
    """
    Развертываение на сервер с уже установленными системными библиотеками, СУБД
    :param user: Пользователь
    :param pas: Пароль пользователя
    :param subdomain Поддомен для приложения
    :return: Развернутое приложения на сервере
    """
    env.user = user
    env.password = pas
    env.work = subdomain
    env.domain = '{}.{}'.format(subdomain, DOMAIN)
    env.project_dir = '/home/{user}/{project}'.format(user=user, project=PROJECT_NAME)
    env.root = '{project_dir}/works/{work}/'.format(project_dir=env.project_dir, work=env.work)
    clone_project()
    create_config()
    link_conf()
    reload()


@task
def config(user=USER, pas=PASS, subdomain=SUBDOMAIN):
    """
    Конфигурирование проекта, уже склонированного
    :param user: Пользователь
    :param pas: Пароль
    :param subdomain: Поддомен для приложения
    :return:
    """
    env.user = user
    env.password = pas
    env.work = subdomain
    env.domain = '{}.{}'.format(subdomain, DOMAIN)
    env.project_dir = '/home/{user}/{project}'.format(user=user, project=PROJECT_NAME)
    env.root = '{project_dir}/works/{work}/'.format(project_dir=env.project_dir, work=env.work)
    create_config()
    link_conf()
    reload()


@task
def update(user=USER, pas=PASS):
    """
    Загружаем последние изменения и рестартим nginx
    :param user: Пользователь
    :param pas: Пароль
    :return: Обновление проекта
    """
    env.user = user
    env.password = pas
    with cd(PROJECT_NAME):
        run('git pull origin master')
    reload()


def initial_setting(user, pas, subdomain):
    env.user = user
    env.password = pas
    env.work = subdomain
    env.domain = '{}.{}'.format(subdomain, DOMAIN)
    env.project_dir = '/home/{user}/{project}'.format(user=user, project=PROJECT_NAME)
    env.root = '{project_dir}/works/{work}/'.format(project_dir=env.project_dir, work=env.work)


@task(alias='test')
def config_test_work(user=USER, pas=PASS, subdomain='test', build=True):
    initial_setting(user, pas, subdomain)
    if build:
        with cd(env.root):
            run('npm i')
            run('gulp clean')
            run('gulp build')
    create_config(build)
    link_conf()
    reload()
