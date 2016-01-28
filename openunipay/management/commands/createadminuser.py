'''
Created on Nov 16, 2015

@author: panweif
'''
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'create amdin superuser with password 123'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        User.objects.create_superuser('admin', '', '123')
        self.stdout.write('admin user created successfully')
